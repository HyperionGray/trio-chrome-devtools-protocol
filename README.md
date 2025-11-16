# Trio CDP

[![PyPI](https://img.shields.io/pypi/v/trio-chrome-devtools-protocol.svg)](https://pypi.org/project/trio-chrome-devtools-protocol/)
![Python Versions](https://img.shields.io/pypi/pyversions/trio-chrome-devtools-protocol)
![MIT License](https://img.shields.io/github/license/HyperionGray/trio-chrome-devtools-protocol.svg)
[![Build Status](https://img.shields.io/travis/com/HyperionGray/trio-chrome-devtools-protocol.svg?branch=master)](https://travis-ci.com/HyperionGray/trio-chrome-devtools-protocol)
[![Read the Docs](https://img.shields.io/readthedocs/trio-cdp.svg)](https://trio-cdp.readthedocs.io)

This Python library performs remote control of any web browser that implements
the Chrome DevTools Protocol. It is built using the type wrappers in
[python-chrome-devtools-protocol](https://py-cdp.readthedocs.io) and implements
I/O using [Trio](https://trio.readthedocs.io/). This library handles the
WebSocket negotiation and session management, allowing you to transparently
multiplex commands, responses, and events over a single connection.

## Features

- **Pure CDP**: Direct access to Chrome DevTools Protocol
- **Async/Await**: Built on Trio for structured concurrency
- **Type Safety**: Full type hints for better IDE support
- **High-Level Utilities**: Puppeteer-inspired abstractions for common tasks
  - Keyboard and mouse simulation
  - Element interaction and querying
  - Wait for elements to appear
  - Pure CDP implementation (no JavaScript injection)

## Basic Example

The example below demonstrates the salient features of the library by navigating to a
web page and extracting the document title.

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

## High-Level Utilities Example

The library also provides high-level utilities for common automation tasks:

```python
from trio_cdp import open_cdp, page, target
from trio_cdp.util import query_selector, Keyboard

async with open_cdp(cdp_url) as conn:
    async with conn.open_session(target_id) as session:
        # Navigate to a page
        await page.enable()
        await page.navigate(url)
        
        # Find an input field and type into it
        input_field = await query_selector(session, 'input[name="search"]')
        if input_field:
            await input_field.type('Hello, World!')
        
        # Press Enter to submit
        keyboard = Keyboard(session)
        await keyboard.press('Enter')
```

This example code is explained [in the documentation](https://trio-cdp.readthedocs.io)
and more example code can be found in the `examples/` directory of this repository.
