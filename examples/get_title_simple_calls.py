'''
Get the title of a target web page.

This example is the same as the examples/get_title.py but demonstrates the 
simplified calls to relevant CDP domain functions

To use this example, start Chrome (or any other browser that supports CDP) with
the option `--remote-debugging-port=9000`. The URL that Chrome is listening on
is displayed in the terminal after Chrome starts up.

Then run this script with the Chrome URL as the first argument and the target
website URL as the second argument:

$ python examples/get_title.py \
    ws://localhost:9000/devtools/browser/facfb2295-... \
    https://www.hyperiongray.com
'''
import logging
import os
import sys

from cdp import dom, page, target
import trio
from trio_cdp import open_cdp_connection
#Additional trio_cdp imports to support simplified CDP domain function call, no session.execute(....)
from trio_cdp import CDP_Active_Session_Manager
from trio_cdp import simplify_cdp_domain_calls


log_level = os.environ.get('LOG_LEVEL', 'info').upper()
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger('get_title')
logging.getLogger('trio-websocket').setLevel(logging.WARNING)


async def main():
    logger.info('Connecting to browser: %s', sys.argv[1])
    async with open_cdp_connection(sys.argv[1]) as conn:
        logger.info('Listing targets')
        targets = await conn.execute(target.get_targets())

        for t in targets:
            if (t.type == 'page' and
                not t.url.startswith('devtools://') and
                not t.attached):
                target_id = t.target_id
                break

        logger.info('Attaching to target id=%s', target_id)
        session = await conn.open_session(target_id)

        active_session_manager = CDP_Active_Session_Manager() # Create instance of Manager
        CDP_Active_Session_Manager.getInstance().session = session #update the mananger with the current session

        # Notify the wish to use simple domain function calls
        simplify_cdp_domain_calls(page)
        simplify_cdp_domain_calls(dom)

        logger.info('Navigating to %s', sys.argv[2])
        await page.enable()
        async with session.wait_for(page.LoadEventFired):
            await page.navigate(sys.argv[2])

        logger.info('Extracting page title')
        root_node = await dom.get_document()
        title_node_id = await dom.query_selector(root_node.node_id, 'title')
        html = await dom.get_outer_html(title_node_id)
        print(html)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.stderr.write('Usage: get_title.py <browser url> <target url>')
        sys.exit(1)
    trio.run(main, restrict_keyboard_interrupt_to_checkpoints=True)
