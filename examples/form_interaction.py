'''
Example demonstrating higher-level utilities for form interaction.

This example shows how to use the Keyboard, Mouse, and ElementHandle utilities
to interact with a web page in a more intuitive way, similar to Puppeteer.

To use this example, start Chrome (or any other browser that supports CDP) with
the option `--remote-debugging-port=9000`. The URL that Chrome is listening on
is displayed in the terminal after Chrome starts up.

Then run this script with the Chrome URL as the first argument and the target
website URL as the second argument:

$ python examples/form_interaction.py \
    ws://localhost:9000/devtools/browser/facfb2295-... \
    https://www.example.com
'''
import logging
import os
import sys

import trio
from trio_cdp import open_cdp, page, target
from trio_cdp.util import Keyboard, Mouse, query_selector, wait_for_selector


log_level = os.environ.get('LOG_LEVEL', 'info').upper()
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger('form_interaction')
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

            # Create utility instances
            keyboard = Keyboard(session)
            mouse = Mouse(session)

            # Example 1: Find an element and click it
            logger.info('Looking for a link...')
            link = await query_selector(session, 'a')
            if link:
                logger.info('Found link, clicking it')
                await link.click()
                await trio.sleep(1)  # Wait for navigation
            
            # Example 2: Type into an input field
            logger.info('Looking for an input field...')
            input_field = await query_selector(session, 'input[type="text"], input:not([type])')
            if input_field:
                logger.info('Found input field, typing text')
                await input_field.type('Hello from Trio CDP!')
                await trio.sleep(0.5)
            
            # Example 3: Use keyboard shortcuts
            logger.info('Pressing Ctrl+A to select all')
            await keyboard.down('Control')
            await keyboard.press('a')
            await keyboard.up('Control')
            
            # Example 4: Get element attributes
            if link:
                href = await link.get_attribute('href')
                logger.info('Link href: %s', href)
            
            logger.info('Example complete!')
            await trio.sleep(2)  # Pause to see results


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.stderr.write('Usage: form_interaction.py <browser url> <target url>\n')
        sys.exit(1)
    trio.run(main, restrict_keyboard_interrupt_to_checkpoints=True)
