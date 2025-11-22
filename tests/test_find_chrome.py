import json
import logging
from unittest.mock import Mock, patch
from urllib.error import URLError

import pytest

from trio_cdp import find_chrome_debugger_url


def test_find_chrome_debugger_url_success():
    ''' Test that find_chrome_debugger_url correctly parses a valid response. '''
    mock_response = Mock()
    mock_response.read.return_value = json.dumps({
        'webSocketDebuggerUrl': 'ws://localhost:9222/devtools/browser/test-uuid'
    }).encode('utf-8')
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=False)
    
    with patch('urllib.request.urlopen', return_value=mock_response) as mock_urlopen:
        url = find_chrome_debugger_url(port=9222)
        
        # Verify the correct URL was called
        mock_urlopen.assert_called_once_with('http://localhost:9222/json/version')
        
        # Verify the correct WebSocket URL was returned
        assert url == 'ws://localhost:9222/devtools/browser/test-uuid'


def test_find_chrome_debugger_url_custom_host_port():
    ''' Test that find_chrome_debugger_url works with custom host and port. '''
    mock_response = Mock()
    mock_response.read.return_value = json.dumps({
        'webSocketDebuggerUrl': 'ws://example.com:9000/devtools/browser/test-uuid'
    }).encode('utf-8')
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=False)
    
    with patch('urllib.request.urlopen', return_value=mock_response) as mock_urlopen:
        url = find_chrome_debugger_url(host='example.com', port=9000)
        
        # Verify the correct URL was called
        mock_urlopen.assert_called_once_with('http://example.com:9000/json/version')
        
        # Verify the correct WebSocket URL was returned
        assert url == 'ws://example.com:9000/devtools/browser/test-uuid'


def test_find_chrome_debugger_url_connection_error():
    ''' Test that find_chrome_debugger_url raises URLError when Chrome is not running. '''
    with patch('urllib.request.urlopen', side_effect=URLError('Connection refused')):
        with pytest.raises(URLError):
            find_chrome_debugger_url()


def test_find_chrome_debugger_url_missing_field():
    ''' Test that find_chrome_debugger_url raises ValueError when response lacks webSocketDebuggerUrl. '''
    mock_response = Mock()
    mock_response.read.return_value = json.dumps({
        'Browser': 'Chrome/90.0',
        # Missing webSocketDebuggerUrl
    }).encode('utf-8')
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=False)
    
    with patch('urllib.request.urlopen', return_value=mock_response):
        with pytest.raises(ValueError) as exc_info:
            find_chrome_debugger_url()
        
        assert 'No webSocketDebuggerUrl found' in str(exc_info.value)


def test_find_chrome_debugger_url_invalid_json():
    ''' Test that find_chrome_debugger_url handles invalid JSON gracefully. '''
    mock_response = Mock()
    mock_response.read.return_value = b'not valid json'
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=False)
    
    with patch('urllib.request.urlopen', return_value=mock_response):
        with pytest.raises(json.JSONDecodeError):
            find_chrome_debugger_url()
