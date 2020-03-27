Getting Started
===============

```python
from trio_cdp import open_cdp, page, dom

async with open_cdp(cdp_url) as conn:
    # Find the first available target (usually a browser tab).
    targets = await target.get_targets()
    target_id = targets[0].id

    # Create a new session with the chosen target.
    async with conn.open_session(target_id) as session:

        # Navigate to a website.
        async with session.page_enable()
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
async with open_cdp(cdp_url) as conn:
```

This context manager opens a connection to the browser when the block is entered and
closes the connection automatically when the block exits. Now we have a connection to
the browser, but the browser has multiple targets that can be operated independently.
For example, each browser tab is a separate target. In order to interact with one of
them, we have to create a session for it.

```python
# Find the first available target (usually a browser tab).
targets = await target.get_targets()
target_id = targets[0].id
```

The first line here executes the `get_targets()` command in the browser. Trio CDP
multiplexes commands and responses on a single connection, so we can send commands from
multiple Trio tasks, and the responses will be routed back to the correct task.

> Note however that we didn't actually specify _which_ connection to run the
`get_targets()` command  on. The `async with open_cdp(...)` context manager sets the
connection as the default connection for all commands executed within this Trio task.
When you run a CDP command inside this task, it will automatically be sent on that
connection.

The command `target.get_targets()` returns a list of `TargetInfo` objects. We grab the
first object and extract its `target_id`.

```python
# Create a new session with the chosen target.
async with conn.open_session(target_id) as session:
```

In order to connect to a target, we open a session based on the target ID. As with the
connection, we do this inside a context manager so that the session is automatically
cleaned up for us when we are done with it.

```python
async with session.page_enable():
    async with session.wait_for(page.LoadEventFired):
        await page.navigate(target_url)
```

This code block is where we actually start to manipulate the browser, but there's a lot
going on here. We'll actually walk through this backwards.

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
power, or you can use the context manager `async with session.page_enable(): ...`
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
in `tests/` also provide more examples.

<a href="https://www.hyperiongray.com/?pk_campaign=github&pk_kwd=triocdp"><img alt="define hyperion gray" width="500px" src="https://hyperiongray.s3.amazonaws.com/define-hg.svg"></a>
