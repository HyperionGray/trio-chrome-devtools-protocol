'''
Get the title of a target web page using HTTP URL.

This example shows the simplest way to connect to Chrome using just an HTTP URL.

To use this example, start Chrome (or any other browser that supports CDP) with
the option `--remote-debugging-port=9000`.

Then run this script with just the target website URL:

$ python examples/get_title_http.py https://www.hyperiongray.com

You can also set the Chrome debugging port via environment variable:

$ CHROME_DEBUG_PORT=9000 python examples/get_title_http.py https://www.hyperiongray.com
'''
import logging
import os
import sys

import trio
from trio_cdp import open_cdp, dom, page, target


log_level = os.environ.get('LOG_LEVEL', 'info').upper()
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger('get_title_http')
logging.getLogger('trio-websocket').setLevel(logging.WARNING)


async def main():
    # Simply use an HTTP URL - it will be automatically resolved to a WebSocket URL
    port = int(os.environ.get('CHROME_DEBUG_PORT', '9222'))
    chrome_url = f'http://localhost:{port}'
    
    logger.info('Connecting to Chrome at: %s', chrome_url)
    
    async with open_cdp(chrome_url) as conn:
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
        sys.stderr.write('Usage: get_title_http.py <target url>\n')
        sys.stderr.write('Example: get_title_http.py https://www.hyperiongray.com\n')
        sys.stderr.write('\nEnvironment variables:\n')
        sys.stderr.write('  CHROME_DEBUG_PORT: Chrome debugging port (default: 9222)\n')
        sys.exit(1)
    trio.run(main, restrict_keyboard_interrupt_to_checkpoints=True)
