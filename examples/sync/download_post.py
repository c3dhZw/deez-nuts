"""Example of downloading a post asyncronously."""
import requests

from yippi import YippiClient

session = requests.Session()
client = YippiClient("ExampleDownloader", "0.1", "ExampleUsername", session)

# https://e621.net/posts/1934156
post = client.post(1934156)
image_url = post.file["url"]
image_name = image_url.split("/")[-1]

r = session.get(image_url, stream=True)
r.raise_for_status()

with open(image_name, "wb") as f:
    for chunk in r.iter_content(1024):
        f.write(chunk)

print("Done!")
print(f"Downloaded Post #{post.id}.")
print(image_name)
