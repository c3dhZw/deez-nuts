from typing import List
from typing import Union

from aiohttp import BasicAuth
from aiohttp import FormData

from .AbstractYippi import AbstractYippi
from .Classes import Flag
from .Classes import Note
from .Classes import Pool
from .Classes import Post
from .Exceptions import APIError
from .Exceptions import UserError


class AsyncYippiClient(AbstractYippi):
    async def close(self) -> None:
        await self._session.close()

    async def __aenter__(self) -> "AsyncYippiClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def _call_api(self, method, url, data=None, file=None, **kwargs):
        auth = None
        if self._login:
            auth = BasicAuth(*self._login)

        if file:
            file = file["upload[file]"]
            formdata = FormData()
            formdata.add_field(
                "upload[file]", file[1], filename=file[0], content_type=file[2]
            )
            formdata.add_fields(data)
            data = formdata

        query_string = self._generate_query_keys(**kwargs)
        url += "?" + query_string
        r = await self._session.request(
            method, url, data=data, headers=self.headers, auth=auth
        )
        await self._verify_response(r)
        if not r.status == 204:
            return await r.json()

    async def _verify_response(self, r):
        if r.status >= 300 and r.status < 500:
            res = await r.json()
            if r.status >= 400:
                raise UserError(res.get("message") or res.get("reason"), json=res)

        elif r.status >= 500:
            raise APIError(r.reason)

        if "application/json" not in r.headers.get("Content-Type") and r.status != 204:
            res = await r.text()
            if "Not found." in res:
                raise UserError("Not found.")
            raise UserError("Invalid input or server error.")

    async def posts(
        self,
        tags: Union[List, str] = None,
        limit: int = None,
        page: Union[int, str] = None,
    ):
        response = await self._get_posts(tags, limit, page)
        posts = [Post(self, **p) for p in response["posts"]]
        return posts

    async def post(self, post_id: int):
        api_res = await self._get_post(post_id)
        return Post(self, **api_res["post"])

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
        result = [Note(self, **n) for n in response]
        return result

    async def flags(
        self,
        post_id: int = None,
        creator_id: int = None,
        creator_name: str = None,
        limit: int = None,
    ):
        response = await self._get_flags(post_id, creator_id, creator_name)
        result = [Flag(self, **f) for f in response]
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
        result = [Pool(self, **p) for p in response]
        return result

    async def pool(self, pool_id: int):
        response = await self._get_pool(pool_id)
        return Pool(self, **response)
