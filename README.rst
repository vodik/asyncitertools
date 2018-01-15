asyncitertools
==============

Tools for working with asynchronous generators in Python with a heavy
ReactiveX inspiration.

Design Goals
------------

* Python 3.5+ only. Requires ``async`` and ``await`` syntax and
  ``async for``.
* Simple, clean and uses few abstractions. Try to replicate the API of
  the ``itertools`` package as much as possible.
* Support type hints and optional static type checking.

asyncitertools
--------------

This module implements a number of asynchronous iterator building
blocks inspired by constructs from Python's own ``itertools`` and from
the ReactiveX project.

All the module functions construct and return asynchronous iterators
(``async_generator`` to be specific). Some provide streams of infinite
length, so they should only be accessed by functions or loops that
truncate the stream.

The result should be a rich set of building blocks for creating
functional reactive pipelines in a much more Python and generalize
way. For example:

* **debounce**: Throttles an observable.
* **delay**: delays the items within an observable.
* **distinct_until_changed**: an observable with continuously distinct
  values.
* **filter**: filters an observable.
* **map**: transforms an observable.

observable
----------

The observable package provides the ``Observable`` object, which is
similar to how aioreactive's ``AsyncObserver`` works, but without
making a distinction between Iterator and Observable.

Everything is implemented from a pull model's perspective.

**TODO**: Provide a distinction between cold and hot observable.

Example
-------

A snippet to highlight how the two pieces work together, here's a
snippet of a port of the RxPy autocomplete example.

Note that there is no provided threading support:

.. code-block:: python

    import asyncitertools as op
    import observer

    async def main():
        stream = observer.Subject()

        xs = stream
        xs = op.map(lambda x: x["term"].rstrip(), xs)
        xs = op.filter(lambda text: len(text) > 2, xs)
        xs = op.debounce(0.5, xs)
        xs = op.distinct_until_changed(xs)
        xs = op.map(search_wikipedia, xs)

        async for result in xs:
            print(value)

Now events can be fed into the processing pipeline with a ``send`` call:

.. code-block:: python

    stream.send({"term": "Python"})
