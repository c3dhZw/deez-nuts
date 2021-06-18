from typing import List, Optional
from typing import Union

import requests
from requests.auth import HTTPBasicAuth
from ratelimit import limits, sleep_and_retry

from .AbstractYippi import AbstractYippi
from .Classes import Flag
from .Classes import Note
from .Classes import Pool
from .Classes import Post
from .Exceptions import APIError
from .Exceptions import UserError


class YippiClient(AbstractYippi):
    def __init__(self, *args, session: requests.Session = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._session: requests.Session = session or requests.Session()

    @sleep_and_retry
    @limits(calls=2, period=1)
    def _call_api(
        self, method: str, url: str, data: dict = None, file=None, **kwargs
    ) -> Optional[Union[List[dict], dict]]:
        auth = None
        if self._login != ("", ""):
            auth = HTTPBasicAuth(*self._login)

        query_string = self._generate_query_keys(**kwargs)
        url += "?" + query_string
        r = self._session.request(
            method, url, data=data, files=file, headers=self.headers, auth=auth
        )
        self._verify_response(r)
        if not r.status_code == 204:
            return r.json()

    def _verify_response(self, r) -> None:
        if 300 <= r.status_code < 500:
            res = r.json()
            if r.status_code >= 400:
                raise UserError(res.get("message") or res.get("reason"), json=res)

        elif r.status_code >= 500:
            raise APIError(r.reason)

        if r.status_code != 204 and (
            not r.headers.get("Content-Type")
            or "application/json" not in r.headers.get("Content-Type")
        ):
            res = r.text
            if "Not found." in res:
                raise UserError("Not found.")
            raise UserError("Invalid input or server error.")

    def posts(
        self,
        tags: Union[List, str] = None,
        limit: int = None,
        page: Union[int, str] = None,
    ) -> List[Post]:
        response = self._get_posts(tags, limit, page)
        result = [Post(p, client=self) for p in response["posts"]]  # type: ignore
        return result

    def post(self, post_id: int) -> Post:
        response = self._get_post(post_id)
        return Post(response["post"], client=self)  # type: ignore

    def notes(
        self,
        body_matches: str = None,
        post_id: int = None,
        post_tags_match: Union[List, str] = None,
        creator_name: str = None,
        creator_id: int = None,
        is_active: bool = None,
        limit: int = None,
    ) -> List[Note]:
        response = self._get_notes(
            body_matches,
            post_id,
            post_tags_match,
            creator_name,
            creator_id,
            is_active,
            limit,
        )
        result = [Note(n, client=self) for n in response]  # type: ignore
        return result

    def flags(
        self,
        post_id: int = None,
        creator_id: int = None,
        creator_name: str = None,
        limit: int = None,
    ) -> List[Flag]:
        response = self._get_flags(post_id, creator_id, creator_name)
        result = [Flag(f, client=self) for f in response]  # type: ignore
        return result

    def pools(
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
    ) -> List[Pool]:
        response = self._get_pools(
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
        result = [Pool(p, client=self) for p in response]  # type: ignore
        return result

    def pool(self, pool_id: int) -> Pool:
        response = self._get_pool(pool_id)
        return Pool(response, client=self)  # type: ignore
