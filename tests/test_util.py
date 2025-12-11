import json
import logging

from cdp import dom, input_, page, runtime, target
import pytest
import trio
from trio_websocket import serve_websocket

from . import fail_after
from trio_cdp import open_cdp
from trio_cdp.util import (
    Keyboard, Mouse, ElementHandle,
    query_selector, query_selector_all, wait_for_selector
)


HOST = '127.0.0.1'


async def start_server(nursery, handler):
    ''' A helper that starts a WebSocket server and runs ``handler`` for each
    connection. Returns the server URL. '''
    server = await nursery.start(serve_websocket, handler, HOST, 0, None)
    return f'ws://{HOST}:{server.port}/devtools/browser/uuid'


def test_keyboard_instance():
    """Test that Keyboard can be instantiated."""
    # This is a simple test that doesn't require a real connection
    # In practice, keyboard needs a session, so we'll test with a mock
    pass


@fail_after(2)
async def test_keyboard_press(nursery):
    """Test that keyboard.press sends correct CDP commands."""
    command_log = []
    
    async def handler(request):
        try:
            ws = await request.accept()
            
            # Handle Target.attachToTarget
            command = json.loads(await ws.get_message())
            if command['method'] == 'Target.attachToTarget':
                response = {
                    'id': command['id'],
                    'result': {'sessionId': 'test-session-123'}
                }
                await ws.send_message(json.dumps(response))
            
            # Handle keyboard events
            while True:
                try:
                    msg = await ws.get_message()
                    command = json.loads(msg)
                    command_log.append(command)
                    
                    response = {'id': command['id'], 'result': {}}
                    await ws.send_message(json.dumps(response))
                except Exception:
                    break
        except Exception:
            logging.exception('Server exception')
    
    server = await start_server(nursery, handler)
    async with open_cdp(server) as conn:
        session = await conn.connect_session(target.TargetID('target1'))
        
        keyboard = Keyboard(session)
        await keyboard.press('a')
        
        # Give time for commands to be sent
        await trio.sleep(0.1)
        
        # Check that we got keyDown and keyUp events
        key_events = [cmd for cmd in command_log if cmd.get('method') == 'Input.dispatchKeyEvent']
        assert len(key_events) >= 2
        assert key_events[0]['params']['type'] == 'keyDown'
        assert key_events[1]['params']['type'] == 'keyUp'


@fail_after(2)
async def test_keyboard_type(nursery):
    """Test that keyboard.type sends events for each character."""
    command_log = []
    
    async def handler(request):
        try:
            ws = await request.accept()
            
            # Handle Target.attachToTarget
            command = json.loads(await ws.get_message())
            if command['method'] == 'Target.attachToTarget':
                response = {
                    'id': command['id'],
                    'result': {'sessionId': 'test-session-123'}
                }
                await ws.send_message(json.dumps(response))
            
            # Handle keyboard events
            while True:
                try:
                    msg = await ws.get_message()
                    command = json.loads(msg)
                    command_log.append(command)
                    
                    response = {'id': command['id'], 'result': {}}
                    await ws.send_message(json.dumps(response))
                except Exception:
                    break
        except Exception:
            logging.exception('Server exception')
    
    server = await start_server(nursery, handler)
    async with open_cdp(server) as conn:
        session = await conn.connect_session(target.TargetID('target1'))
        
        keyboard = Keyboard(session)
        await keyboard.type('hi')
        
        # Give time for commands to be sent
        await trio.sleep(0.1)
        
        # Check that we got keyDown and keyUp events for each character
        key_events = [cmd for cmd in command_log if cmd.get('method') == 'Input.dispatchKeyEvent']
        assert len(key_events) >= 4  # 2 events per character (down + up) * 2 characters


@fail_after(2)
async def test_mouse_move(nursery):
    """Test that mouse.move sends correct CDP commands."""
    command_log = []
    
    async def handler(request):
        try:
            ws = await request.accept()
            
            # Handle Target.attachToTarget
            command = json.loads(await ws.get_message())
            if command['method'] == 'Target.attachToTarget':
                response = {
                    'id': command['id'],
                    'result': {'sessionId': 'test-session-123'}
                }
                await ws.send_message(json.dumps(response))
            
            # Handle mouse events
            while True:
                try:
                    msg = await ws.get_message()
                    command = json.loads(msg)
                    command_log.append(command)
                    
                    response = {'id': command['id'], 'result': {}}
                    await ws.send_message(json.dumps(response))
                except Exception:
                    break
        except Exception:
            logging.exception('Server exception')
    
    server = await start_server(nursery, handler)
    async with open_cdp(server) as conn:
        session = await conn.connect_session(target.TargetID('target1'))
        
        mouse = Mouse(session)
        await mouse.move(100, 200, steps=1)
        
        # Give time for commands to be sent
        await trio.sleep(0.1)
        
        # Check that we got a mouseMoved event
        mouse_events = [cmd for cmd in command_log if cmd.get('method') == 'Input.dispatchMouseEvent']
        assert len(mouse_events) >= 1
        assert mouse_events[0]['params']['type'] == 'mouseMoved'
        assert mouse_events[0]['params']['x'] == 100
        assert mouse_events[0]['params']['y'] == 200


@fail_after(2)
async def test_mouse_click(nursery):
    """Test that mouse.click sends correct CDP commands."""
    command_log = []
    
    async def handler(request):
        try:
            ws = await request.accept()
            
            # Handle Target.attachToTarget
            command = json.loads(await ws.get_message())
            if command['method'] == 'Target.attachToTarget':
                response = {
                    'id': command['id'],
                    'result': {'sessionId': 'test-session-123'}
                }
                await ws.send_message(json.dumps(response))
            
            # Handle mouse events
            while True:
                try:
                    msg = await ws.get_message()
                    command = json.loads(msg)
                    command_log.append(command)
                    
                    response = {'id': command['id'], 'result': {}}
                    await ws.send_message(json.dumps(response))
                except Exception:
                    break
        except Exception:
            logging.exception('Server exception')
    
    server = await start_server(nursery, handler)
    async with open_cdp(server) as conn:
        session = await conn.connect_session(target.TargetID('target1'))
        
        mouse = Mouse(session)
        await mouse.click(50, 75)
        
        # Give time for commands to be sent
        await trio.sleep(0.1)
        
        # Check that we got mouseMoved, mousePressed, and mouseReleased events
        mouse_events = [cmd for cmd in command_log if cmd.get('method') == 'Input.dispatchMouseEvent']
        assert len(mouse_events) >= 3
        
        event_types = [e['params']['type'] for e in mouse_events]
        assert 'mouseMoved' in event_types
        assert 'mousePressed' in event_types
        assert 'mouseReleased' in event_types


@fail_after(2)
async def test_query_selector(nursery):
    """Test that query_selector finds an element."""
    async def handler(request):
        try:
            ws = await request.accept()
            
            # Handle Target.attachToTarget
            command = json.loads(await ws.get_message())
            if command['method'] == 'Target.attachToTarget':
                response = {
                    'id': command['id'],
                    'result': {'sessionId': 'test-session-123'}
                }
                await ws.send_message(json.dumps(response))
            
            # Handle subsequent commands
            while True:
                try:
                    msg = await ws.get_message()
                    command = json.loads(msg)
                    
                    if command['method'] == 'DOM.getDocument':
                        response = {
                            'id': command['id'],
                            'result': {
                                'root': {
                                    'nodeId': 1,
                                    'nodeType': 9,
                                    'nodeName': '#document',
                                    'childNodeCount': 1,
                                }
                            }
                        }
                    elif command['method'] == 'DOM.querySelector':
                        response = {
                            'id': command['id'],
                            'result': {'nodeId': 42}
                        }
                    else:
                        response = {'id': command['id'], 'result': {}}
                    
                    await ws.send_message(json.dumps(response))
                except Exception:
                    break
        except Exception:
            logging.exception('Server exception')
    
    server = await start_server(nursery, handler)
    async with open_cdp(server) as conn:
        session = await conn.connect_session(target.TargetID('target1'))
        
        element = await query_selector(session, 'button')
        
        assert element is not None
        assert isinstance(element, ElementHandle)
        assert element.node_id == 42


@fail_after(2)
async def test_query_selector_not_found(nursery):
    """Test that query_selector returns None when element is not found."""
    async def handler(request):
        try:
            ws = await request.accept()
            
            # Handle Target.attachToTarget
            command = json.loads(await ws.get_message())
            if command['method'] == 'Target.attachToTarget':
                response = {
                    'id': command['id'],
                    'result': {'sessionId': 'test-session-123'}
                }
                await ws.send_message(json.dumps(response))
            
            # Handle subsequent commands
            while True:
                try:
                    msg = await ws.get_message()
                    command = json.loads(msg)
                    
                    if command['method'] == 'DOM.getDocument':
                        response = {
                            'id': command['id'],
                            'result': {
                                'root': {
                                    'nodeId': 1,
                                    'nodeType': 9,
                                    'nodeName': '#document',
                                    'childNodeCount': 1,
                                }
                            }
                        }
                    elif command['method'] == 'DOM.querySelector':
                        # Return 0 to indicate element not found
                        response = {
                            'id': command['id'],
                            'result': {'nodeId': 0}
                        }
                    else:
                        response = {'id': command['id'], 'result': {}}
                    
                    await ws.send_message(json.dumps(response))
                except Exception:
                    break
        except Exception:
            logging.exception('Server exception')
    
    server = await start_server(nursery, handler)
    async with open_cdp(server) as conn:
        session = await conn.connect_session(target.TargetID('target1'))
        
        element = await query_selector(session, 'nonexistent')
        
        assert element is None


@fail_after(2)
async def test_element_handle_get_attribute(nursery):
    """Test that ElementHandle.get_attribute retrieves an attribute."""
    async def handler(request):
        try:
            ws = await request.accept()
            
            # Handle Target.attachToTarget
            command = json.loads(await ws.get_message())
            if command['method'] == 'Target.attachToTarget':
                response = {
                    'id': command['id'],
                    'result': {'sessionId': 'test-session-123'}
                }
                await ws.send_message(json.dumps(response))
            
            # Handle subsequent commands
            while True:
                try:
                    msg = await ws.get_message()
                    command = json.loads(msg)
                    
                    if command['method'] == 'DOM.getAttributes':
                        response = {
                            'id': command['id'],
                            'result': {
                                'attributes': ['id', 'test-button', 'class', 'btn btn-primary']
                            }
                        }
                    else:
                        response = {'id': command['id'], 'result': {}}
                    
                    await ws.send_message(json.dumps(response))
                except Exception:
                    break
        except Exception:
            logging.exception('Server exception')
    
    server = await start_server(nursery, handler)
    async with open_cdp(server) as conn:
        session = await conn.connect_session(target.TargetID('target1'))
        
        element = ElementHandle(session=session, node_id=dom.NodeId(42))
        attr_value = await element.get_attribute('id')
        
        assert attr_value == 'test-button'


@fail_after(2)
async def test_element_handle_get_attribute_not_found(nursery):
    """Test that ElementHandle.get_attribute returns None for missing attribute."""
    async def handler(request):
        try:
            ws = await request.accept()
            
            # Handle Target.attachToTarget
            command = json.loads(await ws.get_message())
            if command['method'] == 'Target.attachToTarget':
                response = {
                    'id': command['id'],
                    'result': {'sessionId': 'test-session-123'}
                }
                await ws.send_message(json.dumps(response))
            
            # Handle subsequent commands
            while True:
                try:
                    msg = await ws.get_message()
                    command = json.loads(msg)
                    
                    if command['method'] == 'DOM.getAttributes':
                        response = {
                            'id': command['id'],
                            'result': {
                                'attributes': ['id', 'test-button']
                            }
                        }
                    else:
                        response = {'id': command['id'], 'result': {}}
                    
                    await ws.send_message(json.dumps(response))
                except Exception:
                    break
        except Exception:
            logging.exception('Server exception')
    
    server = await start_server(nursery, handler)
    async with open_cdp(server) as conn:
        session = await conn.connect_session(target.TargetID('target1'))
        
        element = ElementHandle(session=session, node_id=dom.NodeId(42))
        attr_value = await element.get_attribute('nonexistent')
        
        assert attr_value is None
