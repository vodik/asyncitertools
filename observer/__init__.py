import asyncio
import collections


class Observer:
    def __init__(self, *, loop=None):
        if loop is None:
            self._loop = asyncio.get_event_loop()
        else:
            self._loop = loop

        self._busy = self._loop.create_future()
        self._result = self._loop.create_future()
        self._waiters = collections.deque()

    async def send(self, value):
        assert not self._result.done()

        await self._busy
        self._busy = self._loop.create_future()

        while self._waiters:
            waiter = self._waiters.popleft()
            if not waiter.done():
                waiter.set_result(value)

    def close(self):
        self._result.set_result(None)
        while self._waiters:
            waiter = self._waiters.popleft()
            if not waiter.done():
                waiter.cancel()

    def set_exception(self, exc):
        self._result.set_exception(exc)
        while self._waiters:
            waiter = self._waiters.popleft()
            if not waiter.done():
                waiter.set_exception(exc)

    def __await__(self):
        return self._result.__await__()

    async def __aiter__(self):
        return self

    async def __anext__(self):
        if self._result.done():
            raise StopAsyncIteration

        waiter = self._loop.create_future()
        self._waiters.append(waiter)
        if not self._busy.done():
            self._busy.set_result(None)

        try:
            import datetime
            print("!!!", datetime.datetime.now())
            return await waiter
        except asyncio.CancelledError:
            raise StopAsyncIteration


def consume(generator):
    observer = Observer()

    async def consumer():
        try:
            async for msg in generator:
                await observer.send(msg)
            observer.close()
        except Exception as exc:
            observer.set_exception(exc)

    asyncio.ensure_future(consumer())
    return observer
