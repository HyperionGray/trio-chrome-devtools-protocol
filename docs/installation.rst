Installation
============

PyPI
----

The library itself can be installed from PyPI:

.. code::

    $ pip install trio-cdp

Browser
-------

You also need a compatible browser. Here are instructions for getting the correct
browser version and running the example scripts.


## Running Examples on MacOS

**Terminal 1**

This sets up the chrome browser in a specific version, and runs it in debug mode with Tor proxy for network traffic.

```
wget https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Mac%2F678035%2Fchrome-mac.zip?generation=1563322360871926&alt=media
unzip chrome-mac.zip && rm chrome-mac.zip
./chrome-mac/Chromium.app/Contents/MacOS/Chromium --remote-debugging-port=9000
> DevTools listening on ws://127.0.0.1:9000/devtools/browser/<DEV_SESSION_GUID>
```

**Terminal 2**

This runs the example browser automation script on the instantiated browser window.

```bash
python examples/get_title.py ws://127.0.0.1:9000/devtools/browser/<DEV_SESSION_GUID> https://hyperiongray.com
```

## Running Examples on Linux

**Terminal 1**

This sets up the chrome browser in a specific version, and runs it in debug mode with Tor proxy for network traffic.

```
wget https://storage.googleapis.com/chromium-browser-snapshots/Linux_x64/678025/chrome-linux.zip
unzip chrome-linux.zip && rm chrome-linux.zip
./chrome-linux/chrome --remote-debugging-port=9000
> DevTools listening on ws://127.0.0.1:9000/devtools/browser/<DEV_SESSION_GUID>
```

**Terminal 2**

This runs the example browser automation script on the instantiated browser window.

```bash
python examples/get_title.py ws://127.0.0.1:9000/devtools/browser/<DEV_SESSION_GUID> https://hyperiongray.com
```

<a href="https://www.hyperiongray.com/?pk_campaign=github&pk_kwd=trio-cdp"><img alt="define hyperion gray" width="500px" src="https://hyperiongray.s3.amazonaws.com/define-hg.svg"></a>
