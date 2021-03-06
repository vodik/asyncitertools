import asyncio
from threading import current_thread
import time

import asyncitertools as op


def long_running(value):
    thread_name = current_thread().name
    print("Processing {} on thread {}".format(value, thread_name))
    time.sleep(3)
    return value


async def main(loop):
    async def mapper(value):
        return await loop.run_in_executor(None, long_running, value)

    stream = op.from_iterator(range(40))
    async for x in op.flat_map(mapper, stream):
        print(x)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
