import asyncio
from threading import current_thread
import time

import observer
import asyncitertools as op


def long_running(value):
    thread_name = current_thread().name
    print("Long running ({}) on thread {}".format(value, thread_name))
    time.sleep(3)
    print("Long running, done ({}) on thread {}".format(value, thread_name))
    return value


async def main(loop) -> None:
    stream = observer.from_iterator([1, 2, 3, 4, 5])

    def mapper(value):
        return loop.run_in_executor(None, long_running, value)

    async for x in op.map(mapper, stream):
        print(x)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
