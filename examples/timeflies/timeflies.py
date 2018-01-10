import asyncio
from tkinter import Frame, Label, Tk

import observer
import asyncitertools as op


async def position_label(label, idx, events):
    async for ev in op.delay(idx / 10.0, events):
        label.place(x=ev.x + idx * 15 + 15, y=ev.y)


async def main(loop) -> None:
    mousemoves = observer.Observer()

    root = Tk()
    root.title("asyncitertools")

    frame = Frame(root, width=800, height=600)
    frame.bind("<Motion>", lambda ev: asyncio.ensure_future(mousemoves.send(ev)))

    tasks = []
    for idx, char in enumerate("TIME FLIES LIKE AN ARROW"):
        label = Label(frame, text=char)
        label.config({'borderwidth': 0,
                      'padx': 0,
                      'pady': 0})

        tasks.append(asyncio.ensure_future(position_label(label, idx, mousemoves)))

    frame.pack()
    try:
        while True:
            root.update()
            await asyncio.sleep(0.005)
    finally:
        for task in tasks:
            task.cancel()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
