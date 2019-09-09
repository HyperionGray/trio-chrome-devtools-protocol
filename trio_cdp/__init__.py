from collections import defaultdict
from contextlib import asynccontextmanager
import itertools
import json
import logging
import typing

import cdp
import trio # type: ignore
from trio_websocket import open_websocket_url # type: ignore


logger = logging.getLogger('trio_cdp')
T = typing.TypeVar('T')


class BrowserError(Exception):
    def __init__(self, obj):
        self.code = obj['code']
        self.message = obj['message']
        self.detail = obj.get('data')

    def __str__(self):
        return 'BrowserError<code={} message={}> {}'.format(self.code,
            self.message, self.detail)


class InternalError(Exception):
    pass


class CdpBase:
    '''
    Contains shared functionality between the CDP connection and session.
    '''
    def __init__(self, ws, session_id=None, target_id=None):
        self.channels = defaultdict(set)
        self.id_iter = itertools.count()
        self.inflight_cmd = dict()
        self.inflight_result = dict()
        self.session_id = session_id
        self.target_id = target_id
        self.ws = ws

    async def execute(self, cmd: typing.Generator[dict,T,typing.Any]) -> T:
        '''
        Execute a command on the server and wait for the result.

        :param cmd: any CDP command
        :returns: a CDP result
        '''
        cmd_id = next(self.id_iter)
        cmd_event = trio.Event()
        self.inflight_cmd[cmd_id] = cmd, cmd_event
        request = next(cmd)
        request['id'] = cmd_id
        if self.session_id:
            request['sessionId'] = self.session_id
        logger.debug('Sending command %r', request)
        request_str = json.dumps(request)
        await self.ws.send_message(request_str)
        await cmd_event.wait()
        response = self.inflight_result.pop(cmd_id)
        if isinstance(response, Exception):
            raise response
        return response

    def listen(self, *event_types):
        ''' Return an async iterator that iterates over events matching the
        indicated types. '''
        sender, receiver = trio.open_memory_channel(10)
        for event_type in event_types:
            self.channels[event_type].add(sender)
        return receiver

    async def wait_for(self, event_type: typing.Type[T]) -> T:
        '''
        Wait for an event of the given type and return it.
        '''
        sender, receiver = trio.open_memory_channel(1)
        self.channels[event_type].add(sender)
        event = await receiver.receive()
        await receiver.aclose()
        return event

    def _handle_data(self, data):
        '''
        Handle incoming WebSocket data.

        :param dict data: a JSON dictionary
        '''
        if 'id' in data:
            self._handle_cmd_response(data)
        else:
            self._handle_event(data)

    def _handle_cmd_response(self, data):
        '''
        Handle a response to a command. This will set an event flag that will
        return control to the task that called the command.

        :param dict data: response as a JSON dictionary
        '''
        cmd_id = data['id']
        try:
            cmd, event = self.inflight_cmd.pop(cmd_id)
        except KeyError:
            logger.warning('Got a message with a command ID that does'
                ' not exist: {}'.format(data))
            return
        if 'error' in data:
            # If the server reported an error, convert it to an exception and do
            # not process the response any further.
            self.inflight_result[cmd_id] = BrowserError(data['error'])
        else:
            # Otherwise, continue the generator to parse the JSON result
            # into a CDP object.
            try:
                response = cmd.send(data['result'])
                raise InternalError("The command's generator function "
                    "did not exit when expected!")
            except StopIteration as exit:
                return_ = exit.value
            self.inflight_result[cmd_id] = return_
        event.set()

    def _handle_event(self, data):
        '''
        Handle an event.

        :param dict data: event as a JSON dictionary
        '''
        event = cdp.util.parse_json_event(data)
        to_remove = set()
        for sender in self.channels[type(event)]:
            try:
                sender.send_nowait(event)
            except trio.WouldBlock:
                logger.error('Unable to send event "%r" due to full channel %s',
                    event, sender)
            except trio.BrokenResourceError:
                to_remove.add(sender)
        if to_remove:
            self.channels[type(event)] -= to_remove


class CdpConnection(CdpBase):
    '''
    Contains the connection state for a Chrome DevTools Protocol server.

    CDP can multiplex multiple "sessions" over a single connection. This class
    corresponds to the "root" session, i.e. the implicitly created session that
    has no session ID. This class is responsible for reading incoming WebSocket
    messages and forwarding them to the corresponding session, or handling the
    "root" session itself.

    You should generally call the :func:`open_cdp_connection()` instead of
    instantiating this class directly.
    '''
    def __init__(self, ws):
        '''
        Constructor

        :param trio_websocket.WebSocketConnection ws:
        '''
        super().__init__(ws, session_id=None)
        self.sessions = dict()

    async def open_session(self, target_id: cdp.target.TargetID) -> 'CdpSession':
        '''
        Open a :class:`CdpSession` with the specified target.
        '''
        session_id = await self.execute(cdp.target.attach_to_target(
            target_id, True))
        session = CdpSession(self.ws, session_id, target_id)
        self.sessions[session_id] = session
        return session

    async def _reader_task(self):
        '''
        Runs in the background and handles incoming messages: dispatching
        responses to commands and events to listeners.
        '''
        while True:
            message = await self.ws.get_message()
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                raise BrowserError({
                    'code': -32700,
                    'message': 'Client received invalid JSON',
                    'data': message
                })
            logger.debug('Received message %r', data)
            if 'sessionId' in data:
                session_id = cdp.target.SessionID(data['sessionId'])
                try:
                    session = self.sessions[session_id]
                except KeyError:
                    raise BrowserError('Browser sent a message for an invalid '
                        'session: {!r}'.format(session_id))
                session._handle_data(data)
            else:
                self._handle_data(data)


class CdpSession(CdpBase):
    '''
    Contains the state for a CDP session.

    Generally you should not instantiate this object yourself; you should call
    :meth:`CdpConnection.open_session`.
    '''
    def __init__(self, ws, session_id, target_id):
        '''
        Constructor.

        :param trio_websocket.WebSocketConnection ws:
        :param cdp.target.SessionID session_id:
        :param cdp.target.TargetID target_id:
        '''
        super().__init__(ws, session_id, target_id)


@asynccontextmanager
async def open_cdp_connection(url) -> typing.AsyncIterator[CdpConnection]:
    async with open_websocket_url(url, max_message_size=2**24) as ws:
        async with trio.open_nursery() as nursery:
            cdp_conn = CdpConnection(ws)
            nursery.start_soon(cdp_conn._reader_task)
            yield cdp_conn
            nursery.cancel_scope.cancel()
