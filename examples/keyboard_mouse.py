'''
Example demonstrating keyboard and mouse utilities.

This example shows how to use the Keyboard and Mouse classes to simulate
user input on a web page.

To use this example, start Chrome (or any other browser that supports CDP) with
the option `--remote-debugging-port=9000`. The URL that Chrome is listening on
is displayed in the terminal after Chrome starts up.

Then run this script with the Chrome URL as the first argument and the target
website URL as the second argument:

$ python examples/keyboard_mouse.py \
    ws://localhost:9000/devtools/browser/facfb2295-... \
    https://www.google.com
'''
import logging
import os
import sys

import trio
from trio_cdp import open_cdp, page, target
from trio_cdp.util import Keyboard, Mouse, query_selector, wait_for_selector


log_level = os.environ.get('LOG_LEVEL', 'info').upper()
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger('keyboard_mouse')
logging.getLogger('trio-websocket').setLevel(logging.WARNING)


async def main():
    logger.info('Connecting to browser: %s', sys.argv[1])
    async with open_cdp(sys.argv[1]) as conn:
        logger.info('Listing targets')
        targets = await target.get_targets()

        for t in targets:
            if (t.type == 'page' and
                not t.url.startswith('devtools://') and
                not t.attached):
                target_id = t.target_id
                break

        logger.info('Attaching to target id=%s', target_id)
        async with conn.open_session(target_id) as session:
            
            # Enable page events
            logger.info('Enabling page events')
            await page.enable()

            logger.info('Navigating to %s', sys.argv[2])
            async with session.wait_for(page.LoadEventFired):
                await page.navigate(sys.argv[2])

            # Wait a moment for the page to fully load
            await trio.sleep(1)

            # Create utility instances
            keyboard = Keyboard(session)
            mouse = Mouse(session)

            # Example: Move mouse and click at a specific position
            logger.info('Moving mouse to position (100, 100)')
            await mouse.move(100, 100, steps=10)
            await trio.sleep(0.5)
            
            logger.info('Clicking at current position')
            await mouse.click(100, 100)
            await trio.sleep(0.5)

            # Example: Type text using keyboard
            logger.info('Typing text with keyboard')
            await keyboard.type('Hello, World!', delay=0.1)
            await trio.sleep(0.5)

            # Example: Press special keys
            logger.info('Pressing Enter key')
            await keyboard.press('Enter')
            await trio.sleep(0.5)

            # Example: Keyboard shortcuts
            logger.info('Pressing Ctrl+A')
            await keyboard.down('Control')
            await keyboard.press('a')
            await keyboard.up('Control')
            
            logger.info('Example complete!')
            await trio.sleep(2)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.stderr.write('Usage: keyboard_mouse.py <browser url> <target url>\n')
        sys.exit(1)
    trio.run(main, restrict_keyboard_interrupt_to_checkpoints=True)
