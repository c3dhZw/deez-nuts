"""Example of downloading pool syncronously.

** WARNING **
The following pool contains **male/male and male/female explicit images.**
"""
import requests

from yippi import YippiClient

page_number = 1


def download_post(post):
    print(f"Downloading Post #{post.id}.")
    image_url = post.file["url"]
    image_name = f"{page_number} - {image_url.split('/')[-1]}"

    r = session.get(image_url, stream=True)
    r.raise_for_status()

    with open(image_name, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)

    print(f"Downloaded Post #{post.id}.")
    print(image_name)


session = requests.Session()
client = YippiClient("ExampleDownloader", "0.1", "ExampleUsername", session)

pool = client.pools("Critical Success")[0]
posts = pool.get_posts()
for post in posts:
    download_post(post)
    page_number += 1
