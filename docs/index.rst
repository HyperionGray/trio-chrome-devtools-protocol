Trio CDP
========

This Python library performs remote control of any web browser that implements the
Chrome DevTools Protocol. It is built using the type wrappers in
`python-chrome-devtools-protocol <https://py-cdp.readthedocs.io>`_ and implements I/O
using `Trio <https://trio.readthedocs.io/>`_. This library handles the WebSocket
negotiation and session management, allowing you to transparently multiplex commands,
responses, and events over a single connection.

Contents
--------

.. toctree::
    :maxdepth: 1

    installation
    getting_started
    api
    changelog
