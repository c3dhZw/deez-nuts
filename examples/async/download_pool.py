"""Example of downloading pool asyncronously.

This will download a pool with 4 concurrent download tasks.
You're able to modify the concurrent task, however it is adviced
to not download more concurrently as it will spam the server too much.

** WARNING **
The following pool contains **male/male and male/female explicit images.**
"""
import asyncio

import aiohttp

from yippi import AsyncYippiClient

loop = asyncio.get_event_loop()
concurrent_limit = 4


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


async def download_post(post, page_number, session):
    print(f"Downloading Post #{post.id}.")
    image_url = post.file["url"]
    image_name = f"{page_number} - {image_url.split('/')[-1]}"

    async with session.get(image_url) as r:
        r.raise_for_status()

        with open(image_name, "wb") as f:
            while True:
                chunk = await r.content.read(1024)
                if not chunk:
                    break  # noqa
                f.write(chunk)

    print(f"Downloaded Post #{post.id}.")
    print(image_name)


async def run():
    global concurrent_limit

    page_number = 1
    session = aiohttp.ClientSession()
    client = AsyncYippiClient("ExampleDownloader", "0.1", "ExampleUsername", session)

    pool = (await client.pools("Critical Success"))[0]
    posts = await pool.get_posts()

    tasks = []
    for post in posts:
        tasks.append(download_post(post, page_number, session))
        page_number += 1

    # Chunk into "concurrent_limit" so we don't spam the server
    for chunked in chunks(tasks, concurrent_limit):
        await asyncio.gather(*chunked)
    await session.close()


loop.run_until_complete(run())
