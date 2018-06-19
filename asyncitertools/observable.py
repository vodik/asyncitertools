import asyncio
import collections
from collections.abc import AsyncGenerator


class Subject(AsyncGenerator):
    def __init__(self, *, loop=None):
        if loop is None:
            self._loop = asyncio.get_event_loop()
        else:
            self._loop = loop

        self._push = self._loop.create_future()
        self._pull = self._loop.create_future()
        self._awaiters = []
        self._busy = False

    async def asend(self, value):
        await self._serialize_access()
        if not self._push.done():
            self._push.set_result(value)
        await self._wait_for_pull()

    async def athrow(self, typ, val=None, tb=None):
        await self._serialize_access()
        if not self._push.done():
            self._push.set_exception(val or typ())
        await self._wait_for_pull()

    async def aclose(self):
        await self.athrow(StopAsyncIteration)

    async def _wait_for_pull(self):
        await self._pull
        self._pull = self._loop.create_future()
        self._busy = False

    async def _serialize_access(self):
        while self._busy:
            future = self._loop.create_future()
            self._awaiters.append(future)
            await future
            self._awaiters.remove(future)

        self._busy = True

    async def __aiter__(self):
        while True:
            try:
                yield await self._push
            except StopAsyncIteration:
                return
            finally:
                self._push = self._loop.create_future()
                if not self._pull.done():
                    self._pull.set_result(True)
                for awaiter in self._awaiters[:1]:
                    awaiter.set_result(True)

    async def __aenter__(self):
        return self

    async def __aexit__(self, typ, val, tb):
        if not typ:
            await self.aclose()
        else:
            await self.athrow(typ, val, tb)


def consume(wrapper):
    observer = Subject()

    async def closure():
        async with observer:
            await wrapper(observer)

    asyncio.ensure_future(closure())
    return observer
