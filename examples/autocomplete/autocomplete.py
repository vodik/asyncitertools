# Example running an aiohttp server doing search queries against
# Wikipedia to populate the autocomplete dropdown in the web UI. Start
# using `python autocomplete.py` and navigate your web browser to
# http://localhost:8080
# 
# Requirements:
# * aiohttp
# * aiohttp_jinja2

import os
import json
import asyncio

import aiohttp
from aiohttp import web
import aiohttp_jinja2
import asyncitertools as op
import jinja2


async def search_wikipedia(term):
    """Search Wikipedia for a given term"""
    url = 'http://en.wikipedia.org/w/api.php'

    params = {"action": 'opensearch',
              "search": term,
              "format": 'json'}

    print("TRYING:", term)
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.text()


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async def read_ws():
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                yield json.loads(msg.data)

            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f"ws connection closed with exception {ws.exception()}")
                return

    xs = read_ws()
    xs = op.map(lambda x: x["term"].rstrip(), xs)
    xs = op.filter(lambda text: len(text) > 2, xs)
    xs = op.debounce(0.5, xs)
    xs = op.distinct_until_changed(xs)
    xs = op.map(search_wikipedia, xs)

    async for result in xs:
        ws.send_str(result)

    return ws


@aiohttp_jinja2.template('index.html')
async def index(request):
    return dict()


async def init(loop):
    port = os.environ.get("PORT", 8080)
    host = "localhost"
    app = web.Application(loop=loop)
    print("Starting server at port: %s" % port)

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('.'))
    app.router.add_static('/static', "static")
    app.router.add_get('/', index)
    app.router.add_get('/ws', websocket_handler)

    return app, host, port


def main():
    loop = asyncio.get_event_loop()
    app, host, port = loop.run_until_complete(init(loop))
    web.run_app(app, host=host, port=port)


if __name__ == '__main__':
    main()
