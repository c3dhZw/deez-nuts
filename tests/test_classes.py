import os

import aiohttp
import pytest
import requests

from yippi import AsyncYippiClient
from yippi import Post
from yippi import YippiClient


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("authorization", "REDACTED")],
    }


@pytest.fixture(scope="module")
def vcr_cassette_dir(request):
    return "tests/cassettes/classes"


@pytest.fixture
def client():
    username = os.environ.get("ESIX_USERNAME")
    key = os.environ.get("ESIX_APIKEY")
    session = requests.Session()
    client = YippiClient("Yippi", "0.1", "Error-", session)
    if username and key:
        client.login(username, key)
    return client


@pytest.fixture
async def async_client(event_loop):
    async with aiohttp.ClientSession(loop=event_loop) as session:
        async_client = AsyncYippiClient("Yippi", "0.1", "Error-", session)
        yield async_client
        await async_client.close()


@pytest.mark.vcr()
def test_note(client):
    note = client.notes(limit=1)[0]
    assert note.get_post()


@pytest.mark.vcr()
def test_pool_sync(client):
    pool = client.pools("Weekend 2")[0]
    posts = pool.get_posts()
    assert len(posts) == 48


@pytest.mark.asyncio
async def test_pool_async(async_client):
    pool = (await async_client.pools("Weekend 2"))[0]
    posts = await pool.get_posts()
    assert len(posts) == 48


@pytest.mark.vcr()
def test_flag(client):
    flag = client.flags(limit=1)[0]
    assert flag.get_post()


@pytest.mark.vcr()
def test_post_vote(client):
    if not client._login:
        pytest.skip("No login credentials provided.")

    post = client.post(1383235)
    assert post.vote()["our_score"] == 1
    assert post.vote(-1)["our_score"] == -1
    assert post.vote(-1)["our_score"] == 0


def test_diffgen():
    p = Post()
    assert (
        p._generate_difference(
            {"test1": ["furry", "m/m"], "test2": ["male", "duo"]},
            {"test1": ["m/m"], "test2": ["male", "duo", "girly"]},
        )
        == "girly -furry"
    )
    assert (
        p._generate_difference(
            {"test1": ["furry", "m/m"], "test2": ["male", "duo"]},
            {"test1": ["m/m"], "test2": ["male", "duo", "furry"]},
        )
        == ""
    )
    assert p._generate_difference(["furry", "m/m"], ["m/m", "duo"]) == "duo -furry"
    assert p._generate_difference("furry m/m", "m/m furry duo") == "duo"
    assert p._generate_difference("furry m/m", "m/m") == "-furry"
    with pytest.raises(ValueError):
        p._generate_difference("furry m/m", ["m/m furry duo"])


def test_create_post():
    Post.from_file("tests/data/sample.jpg")
    with pytest.raises(ValueError):
        Post.from_file("nonexistent/furry/image")
    Post.from_url("https://google.com")
    with pytest.raises(ValueError):
        Post.from_url("i.am.an.invalid.url")
