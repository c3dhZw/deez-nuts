import requests
from .AbstractYippi import AbstractYippi
from .Exceptions import UserError
from .Classes import Post, Note, Flag, Pool
from typing import Union, List


class YippiClient(AbstractYippi):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._session = requests.Session()

    def _call_api(self, method, url, **kwargs):
        query_string = self._generate_query_keys(**kwargs)
        url += "?" + query_string
        r = self._session.request(method, url, headers=self.headers)
        self._verify_response(r)
        return r.json()

    def _verify_response(self, r):
        if r.status_code != 200 and r.status_code < 500:
            res = r.json()
            if r.status_code >= 400:
                raise UserError(res["message"])

        if "application/json" not in r.headers.get('Content-Type'):
            raise UserError("Invalid input or server error.")

        elif r.status_code > 500:
            r.raise_for_status()

    def posts(
        self,
        tags: Union[List, str] = None,
        limit: int = None,
        page: Union[int, str] = None,
    ):
        response = self._get_posts(tags, limit, page)
        result = list(map(Post, response["posts"]))
        return result

    def post(self, post_id: int):
        response = self._get_post(post_id)
        return Post(response['post'])

    def notes(
        self,
        body_matches: str = None,
        post_id: int = None,
        post_tags_match: Union[List, str] = None,
        creator_name: str = None,
        creator_id: str = None,
        is_active: bool = None,
        limit: int = None,
    ):
        response = self._get_notes(
            body_matches,
            post_id,
            post_tags_match,
            creator_name,
            creator_id,
            is_active,
            limit,
        )
        result = list(map(Note, response))
        return result

    def flags(
        self,
        post_id: int = None,
        creator_id: int = None,
        creator_name: str = None,
        limit: int = None
    ):
        response = self._get_flags(post_id, creator_id, creator_name)
        result = list(map(Flag, response))
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
    ):
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
        result = list(map(Flag, response))
        return result
