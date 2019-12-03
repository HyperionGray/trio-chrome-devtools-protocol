# Trio CDP

[![PyPI](https://img.shields.io/pypi/v/trio-chrome-devtools-protocol.svg)](https://pypi.org/project/trio-chrome-devtools-protocol/)
![Python Versions](https://img.shields.io/pypi/pyversions/trio-chrome-devtools-protocol)
![MIT License](https://img.shields.io/github/license/HyperionGray/trio-chrome-devtools-protocol.svg)
[![Build Status](https://img.shields.io/travis/com/HyperionGray/trio-chrome-devtools-protocol.svg?branch=master)](https://travis-ci.com/HyperionGray/trio-chrome-devtools-protocol)

This Python library performs remote control of any web browser that implements
the Chrome DevTools Protocol. It is built using the type wrappers in
[python-chrome-devtools-protocol](https://py-cdp.readthedocs.io) and implements
I/O using [Trio](https://trio.readthedocs.io/). This library handles the
WebSocket negotiation and session management, allowing you to transparently
multiplex commands, responses, and events over a single connection.

The example demonstrates the salient features of the library.

```python
async with open_cdp_connection(cdp_url) as conn:
    # Find the first available target (usually a browser tab).
    targets = await conn.execute(target.get_targets())
    target_id = targets[0].id

    # Create a new session with the chosen target.
    session = await conn.open_session(target_id)

    # Navigate to a website.
    await session.execute(page.enable())
    async with session.wait_for(page.LoadEventFired):
        await session.execute(page.navigate(target_url))

    # Extract the page title.
    root_node = await session.execute(dom.get_document())
    title_node_id = await session.execute(dom.query_selector(root_node.node_id,
        'title'))
    html = await session.execute(dom.get_outer_html(title_node_id))
    print(html)
```

We'll go through this example bit by bit. First, it starts with a context
manager:

```python
async with open_cdp_connection(cdp_url) as conn:
```

This context manager opens a connection to the browser when the block is entered
and closes the connection automatically when the block exits. Now we have a
connection to the browser, but the browser has multiple targets that can be
operated independently. For example, each browser tab is a separate target. In
order to interact with one of them, we have to create a session for it.

```python
targets = await conn.execute(target.get_targets())
target_id = targets[0].id
```

The first line here executes the `get_targets()` command in the browser. Note
the form of the command: `await conn.execute(...)` will send a command to the
browser, parse its response, and return a value (if any). The command is one of
the methods in the PyCDP package. Trio CDP multiplexes commands and responses on
a single connection, so we can send commands concurrently if we want, and the
responses will be routed back to the correct task.

In this case, the command is `target.get_targets()`, which returns a list of
`TargetInfo` objects. We grab the first object and extract its `target_id`.

```python
session = await conn.open_session(target_id)
```

In order to connect to a target, we open a session based on the target ID.

```python
await session.execute(page.enable())
async with session.wait_for(page.LoadEventFired):
    await session.execute(page.navigate(target_url))
```

Here we use the session (remember, it corresponds to a tab in the browser) to
navigate to the target URL. Just like the connection object, the session object
has an `execute(...)` method that sends a command to the target, parses the
response, and returns a value (if any).

This snippet also introduces another concept: events. When we ask the browser to
navigate to a URL, it acknowledges our request with a response, then starts the
navigation process. How do we know when the page is actually loaded, though?
Easy: the browser can send us an event!

We first have to enable page-level events by calling `page.enable()`. Then we
use `session.wait_for(...)` to wait for an event of the desired type. In this
example, the script will suspend until it receives a `page.LoadEventFired`
event. (After this block finishes executing, you can run `page.disable()` to
turn off page-level events if you want to save some bandwidth and processing
power, or you can the context manager `async with session.page_enable(): ...`
to automatically enable page-level events just for a specific block.)

Note that we wait for the event inside an `async with` block, and we do this
_before_ executing the command that will trigger this event. This order of
operations may be surprising, but it avoids race conditions. If we executed a
command and then tried to listen for an event, the browser might fire the event
very quickly before we have had a chance to set up our event listener, and then
we would miss it! The `async with` block sets up the listener before we run the
command, so that no matter how fast the event fires, we are guaranteed to catch
it.

```python
root_node = await session.execute(dom.get_document())
title_node_id = await session.execute(
    dom.query_selector(root_node.node_id, 'title'))
html = await session.execute(dom.get_outer_html(title_node_id))
print(html)
```

The last part of the script navigates the DOM to find the `<title>` element.
First we get the document's root node, then we query for a CSS selector, then
we get the outer HTML of the node. This snippet shows some new APIs, but the
mechanics of sending commands and getting responses are the same as the previous
snippets.

A more complete version of this example can be found in `examples/get_title.py`.
There is also a screenshot example in `examples/screenshot.py`. The unit tests
in `test/` also provide more examples.

<a href="https://www.hyperiongray.com/?pk_campaign=github&pk_kwd=trio-cdp"><img alt="define hyperion gray" width="500px" src="https://hyperiongray.s3.amazonaws.com/define-hg.svg"></a>
