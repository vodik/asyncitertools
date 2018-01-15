import asyncio
import inspect
from typing import Any, AsyncIterator, Awaitable, Callable, TypeVar, Union

from .observable import Observable, Subject, consume  # noqa


class TaskSet:
    def __init__(self):
        self.pending = set()

    def start(self, coro):
        future = asyncio.ensure_future(coro)
        if not future.done():
            self.pending.add(future)
            future.add_done_callback(self.pending.remove)

    def wait(self):
        return asyncio.gather(*self.pending)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        await self.wait()


T1 = TypeVar("T1")
T2 = TypeVar("T2")


async def map(mapper: Callable[[T1], Union[T2, Awaitable[T2]]],
              source: AsyncIterator[T1]) -> AsyncIterator[T2]:
    """Make an async iterator that maps values.

    xs = map(lambda value: value * value, source)

    Keyword arguments:
    mapper: A transform function to apply to each source item.
    """
    async for msg in source:
        result = mapper(msg)
        if inspect.isawaitable(result):
            result = await result

        yield result


def flat_map(mapper: Callable[[T1], Union[T2, Awaitable[T2]]],
             source: AsyncIterator[T1]) -> AsyncIterator[T2]:
    """Make an async iterator that maps values.

    xs = flat_map(lambda value: value * value, source)

    Keyword arguments:
    mapper: A transform function to apply to each source item.
    """
    async def closure(obv):
        async def mapped_send(msg):
            result = mapper(msg)
            if inspect.isawaitable(result):
                result = await result

            await obv.send(result)

        async with TaskSet() as tasks:
            async for msg in source:
                tasks.start(mapped_send(msg))

    return consume(closure)


async def filter(predicate: Callable[[T1], Union[bool, Awaitable[bool]]],
                 source: AsyncIterator[T1]) -> AsyncIterator[T1]:
    """Filters the elements of the sequence based on a predicate."""
    async for msg in source:
        result = predicate(msg)
        if inspect.isawaitable(result) and await result:
            yield msg
        elif result:
            yield msg


def delay(seconds: float, source: AsyncIterator[T1]) -> AsyncIterator[T1]:
    """Time shift an async iterator.

    The relative time intervals between the values are preserved.

    xs = delay(5, source)

    Keyword arguments:
    seconds -- Relative time in seconds by which to shift the source
        stream.
    """
    async def closure(obv):
        if seconds <= 0:
            async for msg in source:
                await obv.send(msg)
            return

        async def delayed_send(msg):
            await asyncio.sleep(seconds)
            await obv.send(msg)

        async with TaskSet() as tasks:
            async for msg in source:
                tasks.start(delayed_send(msg))

        await tasks.wait()

    return consume(closure)


def debounce(seconds: float,
             source: AsyncIterator[T1]) -> AsyncIterator[T1]:
    """Debounce an async iterator.

    Ignores values from a source stream which are followed by
    another value before seconds has elapsed.

    Example:
    xs = debounce(5, source) # 5 seconds

    Keyword arguments:
    seconds -- Duration of the throttle period for each value.
    source -- Source stream to debounce.
    """
    async def closure(obv):
        if seconds <= 0:
            async for msg in source:
                await obv.send(msg)
            return

        has_msg = False
        last_msg = None
        index = 0

        async with TaskSet() as tasks:
            async for msg in source:
                has_msg = True
                last_msg = msg
                index += 1

                async def debounced_send(msg, current):
                    nonlocal has_msg, last_msg, index

                    await asyncio.sleep(seconds)
                    if has_msg and current == index:
                        has_msg = False
                        last_msg = msg
                        await obv.send(msg)

                tasks.start(debounced_send(msg, index))

            if has_msg:
                await obv.send(last_msg)

    return consume(closure)


async def distinct_until_changed(source: AsyncIterator[T1]) -> AsyncIterator[T1]:
    """Filter an async iterator to have continously distict values.

    Example:
    xs = distinct_until_changed(source)
    """
    last_msg = object()  # sentinal

    async for msg in source:
        if msg == last_msg:
            await asyncio.sleep(0)
            continue

        last_msg = msg
        yield msg


async def starts_with(value: T1,
                      source: AsyncIterator[T1]) -> AsyncIterator[T1]:
    """Seed an async iterator with an initial value.

    The initial value is consumed first, then the passed async
    iterator is consumed.

    Example:
    xs = starts_with("http://example.org", source)
    """
    yield value
    async for msg in source:
        yield msg


async def take(count: int,
               source: AsyncIterator[T1]) -> AsyncIterator[T1]:
    """Returns a specified number of contiguous elements from an iterator."""
    if count <= 0:
        return

    counter = 0
    async for msg in source:
        yield msg
        counter += 1
        if counter == count:
            return


async def subscribe(callback: Callable[[T1], Awaitable[Any]],
                    source: AsyncIterator[T1]) -> None:
    async with TaskSet() as tasks:
        async for msg in source:
            tasks.start(callback(msg))


async def from_iterator(iterator):
    for msg in iterator:
        yield msg
