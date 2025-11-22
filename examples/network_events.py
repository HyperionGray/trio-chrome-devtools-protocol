'''
Monitor network events from a web page.

This example demonstrates how to listen to network events such as
RequestWillBeSent, ResponseReceived, etc. It shows both patterns for
handling events:

1. wait_for() - wait for a single event
2. listen() - continuously listen for multiple events

To use this example, start Chrome (or any other browser that supports CDP) with
the option `--remote-debugging-port=9000`. The URL that Chrome is listening on
is displayed in the terminal after Chrome starts up.

Then run this script with the Chrome URL as the first argument and the target
website URL as the second argument:

$ python examples/network_events.py \
    ws://localhost:9000/devtools/browser/facfb2295-... \
    https://www.hyperiongray.com
'''
import logging
import os
import sys

import trio
from trio_cdp import open_cdp, network, page, target


log_level = os.environ.get('LOG_LEVEL', 'info').upper()
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger('network_events')
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

            # Enable network events
            logger.info('Enabling network events')
            await network.enable()

            # Enable page events for navigation
            logger.info('Enabling page events')
            await page.enable()

            # Pattern 1: Using wait_for() to wait for a specific event
            # This is useful when you need to wait for a single event before
            # continuing execution.
            logger.info('Navigating to %s (using wait_for pattern)', sys.argv[2])
            async with session.wait_for(page.LoadEventFired):
                await page.navigate(url=sys.argv[2])
            logger.info('Page loaded')

            # Pattern 2: Using listen() to continuously monitor events
            # This creates an async iterator that yields events as they occur.
            # You can listen to multiple event types simultaneously.
            logger.info('Monitoring network events (press Ctrl+C to stop)...')
            
            # Create an async iterator for network events
            async for event in session.listen(
                network.RequestWillBeSent,
                network.ResponseReceived,
                network.LoadingFinished,
                network.LoadingFailed
            ):
                # Handle different event types
                if isinstance(event, network.RequestWillBeSent):
                    logger.info(
                        'Request: %s %s',
                        event.request.method,
                        event.request.url
                    )
                elif isinstance(event, network.ResponseReceived):
                    logger.info(
                        'Response: %s (status: %d)',
                        event.response.url,
                        event.response.status
                    )
                elif isinstance(event, network.LoadingFinished):
                    logger.info('Loading finished: %s', event.request_id)
                elif isinstance(event, network.LoadingFailed):
                    logger.info(
                        'Loading failed: %s (error: %s)',
                        event.request_id,
                        event.error_text
                    )


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.stderr.write('Usage: network_events.py <browser url> <target url>\n')
        sys.exit(1)
    try:
        trio.run(main, restrict_keyboard_interrupt_to_checkpoints=True)
    except KeyboardInterrupt:
        logger.info('Interrupted by user')
