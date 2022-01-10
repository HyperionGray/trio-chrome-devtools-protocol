import json
import logging

from cdp import dom, page, target
import pytest
import trio
from trio_websocket import serve_websocket

from . import fail_after
from trio_cdp import BrowserError, open_cdp, dom as trio_cdp_dom


HOST = '127.0.0.1'


async def start_server(nursery, handler):
    ''' A helper that starts a WebSocket server and runs ``handler`` for each
    connection. Returns the server URL. '''
    server = await nursery.start(serve_websocket, handler, HOST, 0, None)
    return f'ws://{HOST}:{server.port}/devtools/browser/uuid'


def test_browser_error():
    err = BrowserError({'code': 1000, 'message': 'This is an error',
        'data': 'This is extra data about the error'})
    assert str(err) == 'BrowserError<code=1000 message=This is an error> ' \
        'This is extra data about the error'


@fail_after(1)
async def test_connection_execute(nursery):
    ''' Open a connection and execute a command on it. '''
    async def handler(request):
        # It's tricky to catch exceptions from the server, so exceptions are
        # logged instead.
        try:
            ws = await request.accept()
            command = json.loads(await ws.get_message())
            logging.info('Server received:  %r', command)
            assert command['method'] == 'Target.getTargets'
            response = {
                'id': command['id'],
                'result': {
                    'targetInfos': [{
                        'targetId': 'target1',
                        'type': 'tab',
                        'title': 'New Tab',
                        'url': 'about:newtab',
                        'attached': False,
                        'canAccessOpener': False,
                    }],
                }
            }
            logging.info('Server sending:  %r', response)
            await ws.send_message(json.dumps(response))
        except Exception:
            logging.exception('Server exception')
    server = await start_server(nursery, handler)
    async with open_cdp(server) as conn:
        targets = await conn.execute(target.get_targets())
        assert len(targets) == 1
        assert isinstance(targets[0], target.TargetInfo)


@fail_after(1)
async def test_connection_invalid_json():
    ''' If the server sends invalid JSON, that exception is raised on the reader
    task, which crashes the entire connection. Therefore, the entire test needs
    to be wrapped in try/except. '''
    with pytest.raises(BrowserError) as exc_info:
        async with trio.open_nursery() as nursery:
            async def handler(request):
                # It's tricky to catch exceptions from the server, so exceptions
                # are logged instead.
                try:
                    ws = await request.accept()
                    command = json.loads(await ws.get_message())
                    logging.info('Server received:  %r', command)
                    logging.info('Server sending bogus reponse')
                    await ws.send_message('bogus')
                except Exception:
                    logging.exception('Server exception')
            server = await start_server(nursery, handler)

            async with open_cdp(server) as conn:
                targets = await conn.execute(target.get_targets())
    assert exc_info.value.code == -32700 # JSON parse error


@fail_after(1)
async def test_connection_browser_error(nursery):
    ''' If the browser sends an error with a valid command ID, then that error
    should be raised at the point where the command was executed. Compare to
    ``test_connection_invalid_json()``, where the error is raised on the reader
    task since there is no way to associate it with a specific commmand. '''
    async def handler(request):
        # It's tricky to catch exceptions from the server, so exceptions
        # are logged instead.
        try:
            ws = await request.accept()
            command = json.loads(await ws.get_message())
            logging.info('Server received:  %r', command)
            response = {
                'id': command['id'],
                'error': {
                    'code': -32000,
                    'message': 'This is a browser error',
                    'data': 'This is additional data'
                }
            }
            logging.info('Server sending reponse: %r', response)
            await ws.send_message(json.dumps(response))
        except Exception:
            logging.exception('Server exception')
    server = await start_server(nursery, handler)

    async with open_cdp(server) as conn:
        with pytest.raises(BrowserError) as exc_info:
            targets = await conn.execute(target.get_targets())

    assert exc_info.value.code == -32000


@pytest.fixture
def session_handler():
    ''' This fixture is used for the session tests below. It expects to receive an
    "attachToTarget" command followed by a "querySelector" command. '''
    async def handler(request):
        # It's tricky to catch exceptions from the server, so exceptions are
        # logged instead.
        try:
            ws = await request.accept()

            # Handle "attachToTarget" command.
            command = json.loads(await ws.get_message())
            assert command['method'] == 'Target.attachToTarget'
            assert command['params']['targetId'] == 'target1'
            logging.info('Server received:  %r', command)
            response = {
                'id': command['id'],
                'result': {
                    'sessionId': 'session1',
                }
            }
            logging.info('Server sending:  %r', response)
            await ws.send_message(json.dumps(response))

            # Handle "querySelector" command.
            command = json.loads(await ws.get_message())
            assert command['method'] == 'DOM.querySelector'
            assert command['sessionId'] == 'session1'
            assert command['params']['nodeId'] == 0
            assert command['params']['selector'] == 'p.foo'
            logging.info('Server received:  %r', command)
            response = {
                'id': command['id'],
                'sessionId': command['sessionId'],
                'result': {
                    'nodeId': 1,
                }
            }
            logging.info('Server sending:  %r', response)
            await ws.send_message(json.dumps(response))
        except Exception:
            logging.exception('Server exception')
    return handler


@fail_after(1)
async def test_session_execute(nursery, session_handler):
    ''' Connect a session and execute a command on it. '''
    server = await start_server(nursery, session_handler)

    async with open_cdp(server) as conn:
        session = await conn.connect_session(target.TargetID('target1'))
        assert session.session_id == 'session1'
        node_id = await session.execute(
            dom.query_selector(dom.NodeId(0),'p.foo'))
        assert node_id == 1


@fail_after(1)
async def test_session_context(nursery, session_handler):
    ''' Open a session context and execute a "simplified" API command in it. '''
    server = await start_server(nursery, session_handler)

    async with open_cdp(server) as conn:
        async with conn.open_session(target.TargetID('target1')) as session:
            assert session.session_id == 'session1'
            node_id = await trio_cdp_dom.query_selector(dom.NodeId(0),'p.foo')
            assert node_id == 1


@fail_after(1)
async def test_session_no_context(nursery, session_handler):
    ''' Commands should raise an error if called outside of a session context.. '''
    server = await start_server(nursery, session_handler)

    async with open_cdp(server) as conn:
        with pytest.raises(RuntimeError) as exc_info:
            node_id = await trio_cdp_dom.query_selector(dom.NodeId(0),'p.foo')
        assert str(exc_info.value) == 'dom.query_selector() must be called in a ' \
            'session context.'


@fail_after(1)
async def test_wait_for_event(nursery):
    ''' The server sends 2 different events. The client is listening for a
    specific type of event and therefore only sees the 2nd one. '''
    async def handler(request):
        # It's tricky to catch exceptions from the server, so exceptions are
        # logged instead.
        try:
            ws = await request.accept()

            # Send event 1
            event = {
                'method': 'Page.domContentEventFired',
                'params': {'timestamp': 1},
            }
            logging.info('Server sending:  %r', event)
            await ws.send_message(json.dumps(event))

            # Send event 2
            event = {
                'method': 'Page.loadEventFired',
                'params': {'timestamp': 2},
            }
            logging.info('Server sending:  %r', event)
            await ws.send_message(json.dumps(event))

        except Exception:
            logging.exception('Server exception')
    server = await start_server(nursery, handler)

    async with open_cdp(server) as conn:
        async with conn.wait_for(page.LoadEventFired) as event:
            # In real code we would do something here to trigger a load event,
            # e.g. clicking a link.
            pass
        assert isinstance(event.value, page.LoadEventFired)
        assert event.value.timestamp == 2


@fail_after(1)
async def test_listen_for_events(nursery):
    ''' The server sends 2 different events. The client is listening for a
    specific type of event and therefore only sees the 2nd one. '''
    async def handler(request):
        # It's tricky to catch exceptions from the server, so exceptions are
        # logged instead.
        try:
            ws = await request.accept()

            # Send event 1
            event = {
                'method': 'Page.loadEventFired',
                'params': {'timestamp': 1},
            }
            logging.info('Server sending:  %r', event)
            await ws.send_message(json.dumps(event))

            # Send event 2
            event = {
                'method': 'Page.loadEventFired',
                'params': {'timestamp': 2},
            }
            logging.info('Server sending:  %r', event)
            await ws.send_message(json.dumps(event))

        except Exception:
            logging.exception('Server exception')
    server = await start_server(nursery, handler)

    async with open_cdp(server) as conn:
        n = 1
        async for event in conn.listen(page.LoadEventFired):
            assert isinstance(event, page.LoadEventFired)
            assert event.timestamp == n
            if n == 2:
                break
            n += 1
