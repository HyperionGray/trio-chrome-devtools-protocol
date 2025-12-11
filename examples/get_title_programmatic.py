'''
Get the title of a target web page - programmatic version.

This example shows how to use trio_cdp to connect to Chrome programmatically
without manually copying WebSocket URLs.

To use this example, start Chrome (or any other browser that supports CDP) with
the option `--remote-debugging-port=9000`.

Then run this script with just the target website URL as the first argument:

$ python examples/get_title_programmatic.py https://www.hyperiongray.com

The script will automatically discover the Chrome WebSocket URL.
'''
import logging
import os
import sys

import trio
from trio_cdp import open_cdp, find_chrome_debugger_url, dom, page, target


log_level = os.environ.get('LOG_LEVEL', 'info').upper()
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger('get_title_programmatic')
logging.getLogger('trio-websocket').setLevel(logging.WARNING)


async def main():
    # Discover the Chrome debugging URL automatically
    # By default, Chrome uses port 9222, but you can specify a different port
    port = int(os.environ.get('CHROME_DEBUG_PORT', '9222'))
    
    logger.info('Discovering Chrome debugging URL on port %d', port)
    try:
        browser_url = find_chrome_debugger_url(port=port)
        logger.info('Found Chrome at: %s', browser_url)
    except Exception as e:
        logger.error('Failed to discover Chrome: %s', e)
        logger.error('Make sure Chrome is running with --remote-debugging-port=%d', port)
        sys.exit(1)
    
    # Connect to Chrome
    async with open_cdp(browser_url) as conn:
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

            logger.info('Navigating to %s', sys.argv[1])
            await page.enable()
            async with session.wait_for(page.LoadEventFired):
                await page.navigate(sys.argv[1])

            logger.info('Extracting page title')
            root_node = await dom.get_document()
            title_node_id = await dom.query_selector(root_node.node_id, 'title')
            html = await dom.get_outer_html(title_node_id)
            print(html)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write('Usage: get_title_programmatic.py <target url>\n')
        sys.stderr.write('Example: get_title_programmatic.py https://www.hyperiongray.com\n')
        sys.stderr.write('\nEnvironment variables:\n')
        sys.stderr.write('  CHROME_DEBUG_PORT: Chrome debugging port (default: 9222)\n')
        sys.exit(1)
    trio.run(main, restrict_keyboard_interrupt_to_checkpoints=True)
