Installation
============

PyPI
----

The library itself can be installed from PyPI:

.. code::

    $ pip install trio-chrome-devtools-protocol

Browser
-------

You also need a compatible browser. Here are instructions for getting the correct
browser version and running the example scripts.

MacOS
^^^^^

**Terminal 1**

This sets up the chrome browser in a specific version, and runs it in debug mode with
Tor proxy for network traffic.

.. code::

    $ wget https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Mac%2F678035%2Fchrome-mac.zip?generation=1563322360871926&alt=media
    $ unzip chrome-mac.zip && rm chrome-mac.zip
    $ ./chrome-mac/Chromium.app/Contents/MacOS/Chromium --remote-debugging-port=9000
    > DevTools listening on ws://127.0.0.1:9000/devtools/browser/<DEV_SESSION_GUID>

When Chromium starts, it will display a random URL that it is listening on. Copy this
URL for use in the next step.

**Terminal 2**

This runs the example browser automation script on the instantiated browser window.

.. code:: 

    $ python examples/get_title.py <PASTE BROWSER URL HERE> https://hyperiongray.com

Linux
^^^^^

**Terminal 1**

This sets up the chrome browser in a specific version, and runs it in debug mode with Tor proxy for network traffic.

.. code::

    $ wget https://storage.googleapis.com/chromium-browser-snapshots/Linux_x64/678025/chrome-linux.zip
    $ unzip chrome-linux.zip && rm chrome-linux.zip
    $ ./chrome-linux/chrome --remote-debugging-port=9000
    > DevTools listening on ws://127.0.0.1:9000/devtools/browser/<DEV_SESSION_GUID>

When Chromium starts, it will display a random URL that it is listening on. Copy this
URL for use in the next step.

**Terminal 2**

This runs the example browser automation script on the instantiated browser window.

.. code::

    python examples/get_title.py <PASTE BROWSER URL HERE> https://hyperiongray.com

