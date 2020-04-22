"""Example of downloading a post asyncronously."""
import asyncio

import aiohttp

from yippi import AsyncYippiClient


async def run():
    session = aiohttp.ClientSession()
    client = AsyncYippiClient("ExampleDownloader", "0.1", "ExampleUsername", session)

    # https://e621.net/posts/1934156
    post = await client.post(1934156)
    image_url = post.file["url"]
    image_name = image_url.split("/")[-1]

    async with session.get(image_url) as r:
        r.raise_for_status()

        with open(image_name, "wb") as f:
            while True:
                chunk = await r.content.read(1024)
                if not chunk:
                    break  # noqa
                f.write(chunk)

    await client.close()
    print("Done!")
    print(f"Downloaded Post #{post.id}.")
    print(image_name)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
