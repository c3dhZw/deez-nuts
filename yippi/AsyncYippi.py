import aiohttp
import asyncio
from .AbstractYippi import AbstractYippi
from .Exceptions import UserError
from .Classes import Post
from typing import Union, List
from ratelimit import limits


class AsyncYippiClient(AbstractYippi):
    def __init__(self, *args, loop: asyncio.AbstractEventLoop = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._loop = loop if loop else asyncio.get_event_loop()
        self._session = aiohttp.ClientSession(loop=loop)

    @limits(calls=2, period=60)
    async def _call_api(self, method, url, **kwargs):
        query_string = self._generate_query_keys(**kwargs)
        url += "?" + query_string
        r = await self._session.request(method, url, headers=self.headers)
        await self._verify_response(r)
        return await r.json()

    async def _verify_response(self, r):
        if r.status != 200 and r.status < 500:
            res = await r.json()
            if r.status >= 400:
                raise UserError(res["reason"])

        elif r.status > 500:
            r.raise_for_status()

    async def posts(
        self,
        tags: Union[List, str] = None,
        limit: int = None,
        page: Union[int, str] = None,
    ):
        result = await self._get_posts(tags, limit, page)
        posts = list(map(Post, result["posts"]))
        return posts

    async def post(self, post_id: int):
        api_res = await self._get_post(post_id)
        return Post(api_res['post'])

    async def notes(
        self,
        body_matches: str = None,
        post_id: int = None,
        post_tags_match: Union[List, str] = None,
        creator_name: str = None,
        creator_id: str = None,
        is_active: bool = None,
        limit: int = None,
    ):
        result = await self._get_notes(
            body_matches,
            post_id,
            post_tags_match,
            creator_name,
            creator_id,
            is_active,
            limit,
        )
        return result

    async def flags(
        self, post_id: int = None, creator_id: int = None, creator_name: str = None
    ):
        result = await self._get_flags(post_id, creator_id, creator_name)
        return result

    async def pools(
        self,
        name_matches: str = None,
        id_: Union[int, List[int]] = None,
        description_matches: str = None,
        creator_name: str = None,
        creator_id: int = None,
        is_active: bool = None,
        is_deleted: bool = None,
        category: str = None,
        order: str = None,
        limit: int = None,
    ):
        result = await self._get_pools(
            name_matches,
            id_,
            description_matches,
            creator_name,
            creator_id,
            is_active,
            is_deleted,
            category,
            order,
            limit,
        )
        return result
