from collections import defaultdict
from contextlib import asynccontextmanager
from dataclasses import dataclass
import itertools
import json
import logging
import typing

import cdp
import trio # type: ignore
from trio_websocket import connect_websocket_url, open_websocket_url # type: ignore


logger = logging.getLogger('trio_cdp')
T = typing.TypeVar('T')


class BrowserError(Exception):
    ''' This exception is raised when the browser's response to a command
    indicates that an error occurred. '''
    def __init__(self, obj):
        self.code = obj['code']
        self.message = obj['message']
        self.detail = obj.get('data')

    def __str__(self):
        return 'BrowserError<code={} message={}> {}'.format(self.code,
            self.message, self.detail)


class InternalError(Exception):
    ''' This exception is only raised when there is faulty logic in TrioCDP or
    the integration with PyCDP. '''


@dataclass
class CmEventProxy:
    ''' A proxy object returned by :meth:`CdpBase.wait_for()``. After the
    context manager executes, this proxy object will have a value set that
    contains the returned event. '''
    value: typing.Any = None


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

    def listen(self, *event_types, buffer_size=10):
        ''' Return an async iterator that iterates over events matching the
        indicated types. '''
        sender, receiver = trio.open_memory_channel(buffer_size)
        for event_type in event_types:
            self.channels[event_type].add(sender)
        return receiver

    @asynccontextmanager
    async def wait_for(self, event_type: typing.Type[T], buffer_size=10) -> CmEventProxy:
        '''
        Wait for an event of the given type and return it.

        This is an async context manager, so you should open it inside an async
        with block. The block will not exit until the indicated event is
        received.
        '''
        sender, receiver = trio.open_memory_channel(buffer_size)
        self.channels[event_type].add(sender)
        proxy = CmEventProxy()
        yield proxy
        event = await receiver.receive()
        await receiver.aclose()
        proxy.value = event

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
        logger.debug('Received event: %s', event)
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


class CdpConnection(CdpBase, trio.abc.AsyncResource):
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

    async def aclose(self):
        await self.ws.aclose()

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

        self._dom_enable_count = 0
        self._dom_enable_lock = trio.Lock()
        self._page_enable_count = 0
        self._page_enable_lock = trio.Lock()

    @asynccontextmanager
    async def dom_enable(self):
        '''
        A context manager that executes ``dom.enable()`` when it enters and then
        calls ``dom.disable()``.

        This keeps track of concurrent callers and only disables DOM events when
        all callers have exited.
        '''
        async with self._dom_enable_lock:
            self._dom_enable_count += 1
            if self._dom_enable_count == 1:
                await self.execute(cdp.dom.enable())

        yield

        async with self._dom_enable_lock:
            self._dom_enable_count -= 1
            if self._dom_enable_count == 0:
                await self.execute(cdp.dom.disable())

    @asynccontextmanager
    async def page_enable(self):
        '''
        A context manager that executes ``page.enable()`` when it enters and
        then calls ``page.disable()`` when it exits.

        This keeps track of concurrent callers and only disables page events
        when all callers have exited.
        '''
        async with self._page_enable_lock:
            self._page_enable_count += 1
            if self._page_enable_count == 1:
                await self.execute(cdp.page.enable())

        yield

        async with self._page_enable_lock:
            self._page_enable_count -= 1
            if self._page_enable_count == 0:
                await self.execute(cdp.page.disable())


@asynccontextmanager
async def open_cdp_connection(url) -> typing.AsyncIterator[CdpConnection]:
    '''
    This async context manager opens a connection to the browser specified by
    ``url`` before entering the block, then closes the connection when the block
    exits.
    '''
    async with open_websocket_url(url, max_message_size=2**24) as ws:
        async with trio.open_nursery() as nursery:
            cdp_conn = CdpConnection(ws)
            async with cdp_conn:
                nursery.start_soon(cdp_conn._reader_task)
                yield cdp_conn


async def connect_cdp(nursery, url) -> CdpConnection:
    '''
    Connect to the browser specified by ``url`` and spawn a background task in
    the specified nursery.

    The ``open_cdp_connection()`` context manager is preferred in most
    situations. You should only use this function if you need to specify a
    custom nursery.

    This connection is not automatically closed! You can either use the
    connection object as an async context manager, or else call `aclose()` on it
    when you are done with it.
    '''
    ws = await connect_websocket_url(nursery, url,
        max_message_size=2**24)
    cdp_conn = CdpConnection(ws)
    nursery.start_soon(cdp_conn._reader_task)
    return cdp_conn
