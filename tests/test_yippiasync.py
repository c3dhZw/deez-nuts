import aiohttp
import pytest

from yippi import AsyncYippiClient
from yippi.Enums import Rating
from yippi.Exceptions import APIError
from yippi.Exceptions import UserError


@pytest.fixture(scope="module")
def vcr_cassette_dir(request):
    return "tests/cassettes/async"


@pytest.fixture
async def client(event_loop):
    async with aiohttp.ClientSession(loop=event_loop) as session:
        client = AsyncYippiClient("Yippi", "0.1", "Error-", session=session)
        yield client
        await client.close()


@pytest.mark.asyncio
async def test_context(event_loop):
    async with aiohttp.ClientSession(loop=event_loop) as session:
        async with AsyncYippiClient("Yippi", "0.1", "Error-", session=session):
            pass


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_getpost(client):
    post = await client.post(1383235)
    assert post.id == 1383235
    assert post.created_at == "2017-11-20T12:23:11.340-05:00"
    assert post.updated_at == "2020-04-17T20:27:20.798-04:00"
    assert post.file == {
        "width": 767,
        "height": 1000,
        "ext": "png",
        "size": 489122,
        "md5": "539fd6c8c9af7b79693783b995ddf640",
        "url": "https://static1.e621.net/data/53/9f/539fd6c8c9af7b79693783b995ddf640.png",
    }
    assert post.preview == {
        "width": 115,
        "height": 150,
        "url": "https://static1.e621.net/data/preview/53/9f/539fd6c8c9af7b79693783b995ddf640.jpg",
    }
    assert post.sample == {
        "has": False,
        "height": 1000,
        "width": 767,
        "url": "https://static1.e621.net/data/53/9f/539fd6c8c9af7b79693783b995ddf640.png",
    }
    assert post.score == {"up": 126, "down": -1, "total": 125}
    assert post.tags == {
        "general": [
            "5_fingers",
            "anthro",
            "bed",
            "bedding",
            "blanket",
            "clothed",
            "clothing",
            "door",
            "duo",
            "fingers",
            "fur",
            "furniture",
            "lying",
            "male",
            "male/male",
            "on_side",
            "pillow",
            "sleeping",
            "spooning",
        ],
        "species": [
            "bird_dog",
            "canid",
            "canine",
            "canis",
            "domestic_dog",
            "golden_retriever",
            "hunting_dog",
            "mammal",
            "retriever",
            "wolf",
        ],
        "character": ["daniel_segja", "joel_mustard"],
        "copyright": ["patreon"],
        "artist": ["zeta-haru"],
        "invalid": [],
        "lore": [],
        "meta": ["comic"],
    }
    assert post.locked_tags == []
    assert post.change_seq == 23384218
    assert post.flags == {
        "pending": False,
        "flagged": False,
        "note_locked": False,
        "status_locked": False,
        "rating_locked": False,
        "deleted": False,
    }
    assert post.rating == Rating.SAFE
    assert post.fav_count == 306
    assert post.sources == [
        "https://www.furaffinity.net/view/25500100/",
        "https://furaffinity.net/user/zeta-haru",
    ]
    assert post.pools == [6527]
    assert post.relationships == {
        "parent_id": None,
        "has_children": False,
        "has_active_children": False,
        "children": [],
    }
    assert post.approver_id == 38571
    assert post.uploader_id == 269143
    assert post.description == ""
    assert post.comment_count == 42
    assert not post.is_favorited


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_404(client):
    with pytest.raises(UserError):
        await client.post(99999999999)


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_post_search(client):
    assert await client.posts("m/m")
    assert await client.posts(["m/m", "rating:s"])
    assert len(await client.posts("m/m", limit=1)) == 1
    assert await client.posts("m/m", page=1)


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_post_search_error(client):
    with pytest.raises(UserError):
        await client.posts("m/m", page=1000)


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_note(client):
    note = (await client.notes(post_id=2222254, creator_id=366315, limit=1))[0]
    assert note.id == 257037
    assert note.created_at == "2020-04-19T02:58:56.716-04:00"
    assert note.updated_at == "2020-04-19T02:58:56.716-04:00"
    assert note.creator_id == 366315
    assert note.x == 774
    assert note.y == 136
    assert note.width == 36
    assert note.height == 50
    assert note.version == 2
    assert note.is_active
    assert note.post_id == 2222254
    assert note.body == "Chu~"
    assert note.creator_name == "Mutter"


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_flags(client):
    flag = (await client.flags(post_id=2213076, limit=1))[-1]
    assert flag.id == 368383
    assert flag.created_at == "2020-04-19T02:50:38.030-04:00"
    assert flag.post_id == 2213076
    assert "Inferior version" in flag.reason
    assert not flag.is_resolved
    assert flag.updated_at == "2020-04-19T02:50:38.030-04:00"
    assert not flag.is_deletion
    assert flag.category == "normal"


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_pools(client):
    pool = (await client.pools("Critical Success"))[0]
    assert pool.id == 6059
    assert pool.name == "Critical_Success"
    assert pool.created_at == "2015-05-12T03:12:04.070-04:00"
    assert pool.updated_at == "2020-01-11T07:33:28.640-05:00"
    assert pool.creator_id == 80719
    assert "Terry already knew DMing a roleplay game" in pool.description
    assert not pool.is_active
    assert pool.category == "series"
    assert not pool.is_deleted
    assert {653514, 653515, 653820}.issubset(pool.post_ids)
    assert pool.creator_name == "Emserdalf"
    assert pool.post_count == 48


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_500(client):
    # We can't simulate e621 error, so we just use external help.
    with pytest.raises(APIError):
        await client._call_api("GET", "https://httpstat.us/500")
