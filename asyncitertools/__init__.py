import asyncio
import inspect
from typing import Any, AsyncIterator, Awaitable, Callable, TypeVar, Union


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


async def flat_map(mapper,
                   source: AsyncIterator[T1]) -> AsyncIterator[T2]:
    async for msg in source:
        result = mapper(msg)
        if inspect.isawaitable(result):
            result = await result

        async for submsg in result:
            yield submsg


async def filter(predicate: Callable[[T1], Union[bool, Awaitable[bool]]],
                 source: AsyncIterator[T1]) -> AsyncIterator[T1]:
    async for msg in source:
        result = predicate(msg)
        if inspect.isawaitable(result) and await result:
            yield msg
        elif result:
            yield msg


async def delay(seconds: float,
                source: AsyncIterator[T1]) -> AsyncIterator[T1]:
    """Time shift an async iterator.

    The relative time intervals between the values are preserved.

    xs = delay(5, source)

    Keyword arguments:
    seconds -- Relative time in seconds by which to shift the source
        stream.
    """
    first_msg = await source.__anext__()
    print("SLEEPING", seconds)
    await asyncio.sleep(seconds)
    yield first_msg

    async for msg in source:
        print("SLEEPING", seconds)
        await asyncio.sleep(seconds)
        yield msg


async def debounce(seconds: float,
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
    last_msg: T1
    event = asyncio.Event()

    async def _consumer():
        nonlocal last_msg
        async for msg in source:
            last_msg = msg
            event.set()
        event.set()

    consumer = asyncio.ensure_future(_consumer())
    try:
        while not consumer.done():
            await event.wait()
            await asyncio.sleep(seconds)
            yield last_msg
            event.clear()
    finally:
        consumer.cancel()


async def distinct_until_changed(source: AsyncIterator[T1]) -> AsyncIterator[T1]:
    """Filter an async iterator to have continously distict values.

    Example:
    xs = distinct_until_changed(source)
    """
    async for last_msg in source:
        yield last_msg
        break

    async for msg in source:
        if msg != last_msg:
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
    async for msg in source:
        await callback(msg)
