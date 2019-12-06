import asyncio
import aiohttp
from proxymni import app


app.ACTION = "http://google.com"


async def send(url, session):
    async with session.post(url) as response:
        return await response.text()


async def send_all():
    urls = ["http://localhost:8080/?%s" % i for i in range(10000)]
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            *[send(url, session) for url in urls]
        )


def test_progressive_load():
    asyncio.run(send_all())
