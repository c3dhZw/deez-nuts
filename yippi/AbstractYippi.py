from abc import ABC, abstractmethod
from typing import Optional, Dict, Mapping, Union, List
from urllib.parse import urlencode
from .Exceptions import UserError
from .Constants import (
    BASE_URL,
    POSTS_URL,
    UPLOAD_URL,
    FLAGS_URL,
    NOTES_URL,
    POOLS_URL,
    POST_URL,
)
import requests
import aiohttp


class AbstractYippi(ABC):
    VALID_CATEGORY = ("series", "collection")
    VALID_ORDER = ("name", "created_at", "updated_at", "post_count")

    def __init__(self, project_name: str, version: str, creator: str):
        self.headers = {
            "User-Agent": f"{project_name}/f{version} (by {creator} on e621)"
        }

    @abstractmethod
    def _call_api(
        self, method, url, **kwargs
    ) -> Union[requests.Response, aiohttp.ClientResponse]:
        raise NotImplementedError

    @abstractmethod
    def _verify_response(self):
        raise NotImplementedError

    def _convert_search_query(self, **kwargs) -> dict:
        queries = {}
        for k, v in kwargs.items():
            if k[-1] == "_":
                k = k[0:-1]
            queries[f"search[{k}]"] = v
        return queries

    def _generate_query_keys(self, **kwargs) -> str:
        queries = {}
        for k, v in kwargs.items():
            if v:
                queries[k] = v
        return urlencode(queries)

    def _get_posts(
        self,
        tags: Union[List, str] = None,
        limit: int = None,
        page: Union[int, str] = None,
    ) -> dict:
        if isinstance(tags, list):
            tags = " ".join(tags)
        return self._call_api("GET", POSTS_URL, tags=tags, limit=limit, page=page)

    def _get_post(self, post_id: int):
        url = POST_URL + str(post_id) + ".json"
        return self._call_api("GET", url)

    def _get_flags(
        self,
        post_id: int = None,
        creator_id: int = None,
        creator_name: str = None,
        limit: int = None
    ) -> dict:
        queries: dict = self._convert_search_query(
            post_id=post_id, creator_id=creator_id, creator_name=creator_name
        )
        queries["limit"] = limit
        
        return self._call_api("GET", FLAGS_URL, **queries)

    def _get_notes(
        self,
        body_matches: str = None,
        post_id: int = None,
        post_tags_match: Union[List, str] = None,
        creator_name: str = None,
        creator_id: str = None,
        is_active: bool = None,
        limit: int = None,
    ) -> dict:
        if isinstance(post_tags_match, list):
            post_tags_match = " ".join(post_tags_match)
        if is_active is not None:
            is_active = str(is_active).lower()

        queries: dict = self._convert_search_query(
            body_matches=body_matches,
            post_id=post_id,
            post_tags_match=post_tags_match,
            creator_name=creator_name,
            creator_id=creator_id,
            is_active=is_active,
        )
        queries["limit"] = limit

        return self._call_api("GET", NOTES_URL, **queries)

    def _get_pools(
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
    ) -> dict:
        if isinstance(id_, list):
            id_ = ",".join(id_)

        if is_active is not None:
            is_active = str(is_active).lower()
        if is_deleted is not None:
            is_deleted = str(is_deleted).lower()

        if category and category not in self.VALID_CATEGORY:
            raise UserError(
                f"Invalid category {category}. Valid categories are {self.VALID_CATEGORY}"
            )
        if order and order not in self.VALID_ORDER:
            raise UserError(
                f"Invalid category {order}. Valid categories are {self.VALID_ORDER}"
            )

        queries: dict = self._convert_search_query(
            name_matches=name_matches,
            id_=id_,
            description_matches=description_matches,
            creator_name=creator_name,
            creator_id=creator_id,
            is_active=is_active,
            is_deleted=is_deleted,
            category=category,
            order=order,
        )
        queries["limit"] = limit
        return self._call_api("GET", POOLS_URL, **queries)

    @abstractmethod
    def posts(
        self,
        tags: Union[List, str] = None,
        limit: int = None,
        page: Union[int, str] = None,
    ):
        raise NotImplementedError

    @abstractmethod
    def post(self, post: int):
        raise NotImplementedError

    @abstractmethod
    def flags(
        self, post_id: int = None, creator_id: int = None, creator_name: str = None
    ):
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError
