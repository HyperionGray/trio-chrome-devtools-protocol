from base64 import b64decode
import logging
import os
import sys

import trio

from cdp import emulation, page, target
from trio_cdp import open_cdp_connection


log_level = os.environ.get('LOG_LEVEL', 'info').upper()
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger('screenshot')
logging.getLogger('trio-websocket').setLevel(logging.WARNING)


async def main():
    logger.info('Connecting to browser: %s', sys.argv[1])
    async with open_cdp_connection(sys.argv[1]) as conn:
        logger.info('Listing targets')
        targets = await conn.execute(target.commands.get_targets())
        target_id = targets[0].target_id

        logger.info('Attaching to target id=%s', target_id)
        session = await conn.open_session(target_id)

        logger.info('Setting device emulation')
        await session.execute(emulation.commands.set_device_metrics_override(
            width=800, height=600, device_scale_factor=1, mobile=False
        ))

        logger.info('Enabling page events')
        await session.execute(page.commands.enable())

        logger.info('Navigating to %s', sys.argv[2])
        await session.execute(page.commands.navigate(url=sys.argv[2]))

        logger.info('Waiting for navigation to finish…')
        event = await session.wait_for(page.events.LoadEventFired)

        logger.info('Making a screenshot')
        img_data = await session.execute(page.commands.capture_screenshot(
            format='png'
        ))
        screenshot_file = await trio.open_file('test.png', 'wb')
        async with screenshot_file:
            await screenshot_file.write(b64decode(img_data))


if __name__ == '__main__':
    trio.run(main, restrict_keyboard_interrupt_to_checkpoints=True)
