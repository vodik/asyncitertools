import asyncio
import collections
import weakref


class Subscription:
    def __init__(self, observer):
        self._observer = observer
        self._loop = observer._loop

        self._busy = self._loop.create_future()
        self._waiters = collections.deque()

    async def _send(self, msg):
        await self._busy
        self._busy = self._loop.create_future()

        while self._waiters:
            waiter = self._waiters.popleft()
            if not waiter.done():
                waiter.set_result(msg)

    def _cancel(self):
        while self._waiters:
            waiter = self._waiters.popleft()
            if not waiter.done():
                waiter.cancel()

    async def __anext__(self):
        if self._observer.done():
            raise StopAsyncIteration

        waiter = self._loop.create_future()
        self._waiters.append(waiter)
        if not self._busy.done():
            self._busy.set_result(None)

        try:
            return await waiter
        except asyncio.CancelledError:
            raise StopAsyncIteration


class Observer:
    def __init__(self, *, loop=None):
        if loop is None:
            self._loop = asyncio.get_event_loop()
        else:
            self._loop = loop

        self._result = self._loop.create_future()
        self._subscriptions = collections.deque()
        self._ready = asyncio.Event()

    async def send(self, msg):
        assert not self._result.done()

        if not any(sub() for sub in self._subscriptions):
            self._ready.clear()
            await self._ready.wait()

        for task in [sub()._send(msg) for sub in self._subscriptions if sub()]:
            await task
        # await asyncio.gather(*tasks)

    async def feed(self, generator):
        try:
            async for msg in generator:
                await self.send(msg)
        except Exception as exc:
            generator.set_exception(exc)

    def stop(self):
        self._result.set_result(None)
        for sub in self._subscriptions:
            if not sub():
                continue
            sub()._cancel()

    def set_exception(self, exc):
        self._result.set_exception(exc)

    def done(self):
        return self._result.done()

    def __await__(self):
        return self._result.__await__()

    async def __aiter__(self):
        sub = Subscription(self)
        self._subscriptions.append(weakref.ref(sub))
        self._ready.set()
        return sub


def consume(generator):
    async def _inner():
        await observer.feed(generator)
        observer.done()

    observer = Observer()
    asyncio.ensure_future(_inner())
    return observer
