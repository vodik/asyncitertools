import asyncio
import functools
from threading import current_thread
import time

import asyncitertools as op


def processor(value):
    thread_name = current_thread().name
    print("Processing {} on thread {}".format(value, thread_name))
    time.sleep(3)
    return value


async def main(loop):
    runner = functools.partial(loop.run_in_executor, None, processor)

    stream = op.from_iterator(range(100))
    async for msg in op.flat_map(runner, stream):
        print(f"Received {msg}")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
