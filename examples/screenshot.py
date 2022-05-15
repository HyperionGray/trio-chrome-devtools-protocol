'''
Make a screenshot of a target web page.

To use this example, start Chrome (or any other browser that supports CDP) with
the option `--remote-debugging-port=9000`. The URL that Chrome is listening on
is displayed in the terminal after Chrome starts up.

Then run this script with the Chrome URL as the first argument and the target
website URL as the second argument:

$ python examples/screenshot.py \
    ws://localhost:9000/devtools/browser/facfb2295-... \
    https://www.hyperiongray.com
'''
from base64 import b64decode
import logging
import os
import sys

import trio
from trio_cdp import open_cdp, emulation, page, target


log_level = os.environ.get('LOG_LEVEL', 'info').upper()
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger('screenshot')
logging.getLogger('trio-websocket').setLevel(logging.WARNING)


async def main():
    logger.info('Connecting to browser: %s', sys.argv[1])
    async with open_cdp(sys.argv[1]) as conn:
        logger.info('Listing targets')
        targets = await target.get_targets()

        for t in targets:
            if (t.type_ == 'page' and
                not t.url.startswith('devtools://') and
                not t.attached):
                target_id = t.target_id
                break

        logger.info('Attaching to target id=%s', target_id)
        async with conn.open_session(target_id) as session:

            logger.info('Setting device emulation')
            await emulation.set_device_metrics_override(
                width=800, height=600, device_scale_factor=1, mobile=False
            )

            logger.info('Enabling page events')
            await page.enable()

            logger.info('Navigating to %s', sys.argv[2])
            async with session.wait_for(page.LoadEventFired):
                await page.navigate(url=sys.argv[2])

            logger.info('Making a screenshot')
            img_data = await page.capture_screenshot(format='png')
            logger.info('Saving to file')
            screenshot_file = await trio.open_file('test.png', 'wb')
            async with screenshot_file:
                await screenshot_file.write(b64decode(img_data))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.stderr.write('Usage: screenshot.py <browser url> <target url>')
        sys.exit(1)
    trio.run(main, restrict_keyboard_interrupt_to_checkpoints=True)
