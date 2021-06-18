Getting Started
===============

.. highlight:: python

The following example shows how to connect to browser, navigate to a specified web page,
and then extract the page title.

.. code::

    from trio_cdp import open_cdp, page, dom, target

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

We'll go through this example bit by bit. First, it starts with a context
manager.

.. code::

    async with open_cdp(cdp_url) as conn:
        ...

This context manager opens a connection to the browser when the block is entered and
closes the connection automatically when the block exits.

Although we are now connected to the browser, The browser has multiple targets that can
be operated independently. For example, each browser tab is a separate target. In order
to interact with one of them, we have to create a session for it.

.. code::

    # Find the first available target (usually a browser tab).
    targets = await target.get_targets()
    target_id = targets[0].id

The first line here executes the ``get_targets()`` command in the browser. Trio CDP
multiplexes commands and responses on a single connection, so we can send commands from
multiple Trio tasks, and the responses will be routed back to the correct task.

.. note::

    We didn't actually specify *which* connection to run the
    ``get_targets()`` command on. The ``async with open_cdp(...)`` context manager sets the
    connection as the default connection for all commands executed within this Trio task.
    When you run any CDP command inside this task, it will automatically be sent on that
    connection.

The command returns a list of ``TargetInfo`` objects. We grab the first object and
extract its ``target_id``.

.. code::

    # Create a new session with the chosen target.
    async with conn.open_session(target_id) as session:
        ...

In order to connect to a target, we open a session based on the target ID. As with the
connection, we do this inside a context manager so that the session is automatically
cleaned up for us when we are done with it.

.. code::

    async with session.page_enable():
        async with session.wait_for(page.LoadEventFired):
            await page.navigate(target_url)

This code block is where we actually start to manipulate the browser, but there's a lot
going on here so we'll take it one line at time, starting from the bottom and moving
upward.

On the last line, we call ``await page.navigate(...)`` to tell the browser to go to a
specific URL. However, we don't want our script to continue executing until the browser
actually finishes loading this new page. For example, if we try to extract the page
title before the page has loaded, it will fail!

The solution is to wait for the browser to send us an event indicating that the page is
loaded. In this case, we want to wait for ``page.LoadEventFired``. The ``async with
session.wait_for(...)`` block means that the block will not exit until the event has
been received.

However, the browser does not send page events unless we enable them. In raw CDP there
are commands ``page.enable`` and ``page.disable`` that turn page events on and off,
respectively. But in Trio CDP, we make this a little cleaner by once again using a
context manager. The ``async with session.page_enable()`` block will turn on page
events, run the code inside, and then turn off page events automatically.

.. note::

    If another task is using page events concurrently, the context manager is smart enough
    not to disable page events until all tasks are finished with it.

.. code::

    root_node = await dom.get_document()
    title_node_id = await dom.query_selector(root_node.node_id, 'title')
    html = await dom.get_outer_html(title_node_id)
    print(html)

The last part of the script navigates the DOM to find the ``<title>`` element.
First we get the document's root node, then we query for a CSS selector, then
we get the outer HTML of the node. This snippet shows some new APIs, but the
mechanics of sending commands and getting responses are the same as the previous
snippets.

A more complete version of this example can be found in ``examples/get_title.py`` in
the repository. There is also a screenshot example in ``examples/screenshot.py``. The 
unit tests in ``tests/`` also provide some helpful sample code.
