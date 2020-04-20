import asyncio
from typing import List
from typing import Union

import aiohttp

from .AbstractYippi import AbstractYippi
from .Classes import Flag
from .Classes import Note
from .Classes import Pool
from .Classes import Post
from .Exceptions import APIError
from .Exceptions import UserError


class AsyncYippiClient(AbstractYippi):
    def __init__(
        self,
        *args,
        session: aiohttp.ClientSession = None,
        loop: asyncio.AbstractEventLoop = None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._loop = loop if loop else asyncio.get_event_loop()
        self._session = session if session else aiohttp.ClientSession(loop=self._loop)

    async def close(self) -> None:
        await self._session.close()

    async def __aenter__(self) -> "AsyncYippiClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def _call_api(self, method, url, data=None, **kwargs):
        query_string = self._generate_query_keys(**kwargs)
        url += "?" + query_string
        r = await self._session.request(method, url, data=data, headers=self.headers)
        await self._verify_response(r)
        return await r.json()

    async def _verify_response(self, r):
        if r.status != 200 and r.status < 500:
            res = await r.json()
            if r.status >= 400:
                raise UserError(res["message"])

        elif r.status >= 500:
            raise APIError(r.reason)

        if "application/json" not in r.headers.get("Content-Type"):
            raise UserError("Invalid input or server error.")

    async def posts(
        self,
        tags: Union[List, str] = None,
        limit: int = None,
        page: Union[int, str] = None,
    ):
        response = await self._get_posts(tags, limit, page)
        posts = [Post(p, self) for p in response["posts"]]
        return posts

    async def post(self, post_id: int):
        api_res = await self._get_post(post_id)
        return Post(api_res["post"], self)

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
        response = await self._get_notes(
            body_matches,
            post_id,
            post_tags_match,
            creator_name,
            creator_id,
            is_active,
            limit,
        )
        result = [Note(n, self) for n in response]
        return result

    async def flags(
        self,
        post_id: int = None,
        creator_id: int = None,
        creator_name: str = None,
        limit: int = None,
    ):
        response = await self._get_flags(post_id, creator_id, creator_name)
        result = [Flag(f, self) for f in response]
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
        response = await self._get_pools(
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
        result = [Pool(p, self) for p in response]
        return result
