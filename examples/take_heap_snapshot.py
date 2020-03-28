'''
Take a heap snapshot.

To use this example, start Chrome (or any other browser that supports CDP) with
the option `--remote-debugging-port=9000`. The URL that Chrome is listening on
is displayed in the terminal after Chrome starts up.

Then run this script with the Chrome URL as the first argument

$ python examples/take_heap_snapshot.py \
    ws://localhost:9000/devtools/browser/facfb2295-...
'''
from datetime import datetime
import logging
import os
import sys

import trio
from trio_cdp import open_cdp, browser, dom, heap_profiler, page, target


log_level = os.environ.get('LOG_LEVEL', 'info').upper()
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger('monitor')
logging.getLogger('trio-websocket').setLevel(logging.WARNING)


# Profiler starts taking snapshot immediately when the command
# arrives (as before) and if `reportProgress` param is `true` it
# will send `HeapProfiler.reportHeapSnapshotProgress` events.
# After that a series of snapshot chunks is sent to the frontend
# as `HeapProfiler.addHeapSnapshotChunk` events. *When whole
# snapshot is sent the backend will sent response to
# `HeapProfiler.takeHeapSnapshot` command.*
# ([ref](https://codereview.chromium.org/98273008))

async def _take_heap_snapshot(session, outfile, report_progress=False):
    async def chunk_helper():
        async for event in session.listen(heap_profiler.AddHeapSnapshotChunk):
            await outfile.write(event.chunk)
    async def progress_helper():
        async for event in session.listen(heap_profiler.ReportHeapSnapshotProgress):
            logger.info('Heap snapshot: {} ({:0.1f}%) {}'.format(event.done, event.done*100 / event.total, 'finished' if event.finished else ''))
    async with trio.open_nursery() as nursery:
        nursery.start_soon(chunk_helper)
        if report_progress:
            nursery.start_soon(progress_helper)
        await heap_profiler.take_heap_snapshot(report_progress)
        nursery.cancel_scope.cancel()


async def main():
    cdp_uri = sys.argv[1]
    async with open_cdp(cdp_uri) as conn:
        logger.info('Connecting')
        targets = await target.get_targets()
        target_id = targets[0].target_id

        # First page
        logger.info('Attaching to target id=%s', target_id)
        async with conn.open_session(target_id) as session:

            logger.info('Started heap snapshot')
            outfile_path = trio.Path('%s.heapsnapshot' % datetime.today().isoformat())
            async with await outfile_path.open('a') as outfile:
                logger.info('Started writing heap snapshot')
                await _take_heap_snapshot(session, outfile, report_progress=True)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write('Usage: take_heap_snapshot.py <browser url>')
        sys.exit(1)
    trio.run(main, restrict_keyboard_interrupt_to_checkpoints=True)
