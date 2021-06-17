from abc import ABC
from abc import abstractmethod
from typing import Awaitable
from typing import List
from typing import Tuple
from typing import TypeVar
from typing import Union
from urllib.parse import urlencode

import aiohttp
import requests

from .Classes import Flag
from .Classes import Note
from .Classes import Pool
from .Classes import Post
from .Constants import FLAGS_URL
from .Constants import NOTES_URL
from .Constants import POOL_URL
from .Constants import POOLS_URL
from .Constants import POST_URL
from .Constants import POSTS_URL
from .Exceptions import UserError

T = TypeVar("T")
MaybeAwaitable = Union[T, Awaitable[T]]
RequestResponse = MaybeAwaitable[dict]
ArrayRequestResponse = MaybeAwaitable[List[dict]]


class AbstractYippi(ABC):
    """An abstract class (abc) for all the Yippi's client.

    Generally you don't really need to use this, except if you want to use
    different implementation for the client.

    Args:
        project_name: Your project's name where this library is going to be used.
        version: You project's version number.
        creator: Your e621 username.
        session: The HTTP client session object.
        loop: The event loop to run on. This is only required on async client.

    """

    VALID_CATEGORY = ("series", "collection")
    VALID_ORDER = ("name", "created_at", "updated_at", "post_count")

    def __init__(
        self, project_name: str, version: str, creator: str,
    ) -> None:
        self.headers = {
            "User-Agent": f"{project_name}/{version} (by {creator} on e621)"
        }
        self._login: Tuple[str, str] = ("", "")

    @abstractmethod
    def _call_api(
        self, method: str, url: str, data: dict = None, **kwargs
    ) -> Union[List[dict], dict]:
        """Calls the API with specified method and url.

        Args:
            method: The method to use.
            url: The URL to call.
            data (Optional): The data to send into the server.
            **kwargs: Query params to request.

        Returns:
            The client's :obj:`Response` object.

        """
        raise NotImplementedError

    @abstractmethod
    def _verify_response(self, r: Union[requests.Response, aiohttp.ClientResponse]) -> None:
        """Verifies response from server.

        Args:
            r: The :obj:`Response` object from client.

        Raises:
            UserError: If the server returns a not found or if the server returns
                HTTP code 4xx.
            APIError: Happens when server returns with HTTP code 5xx.
        """
        raise NotImplementedError

    def _convert_search_query(self, **kwargs) -> dict:
        """Converts keyword arguments into e621's search query dict.

        This function is only used on some endpoints such as pools.

        Args:
            **kwargs: Queries to convert.

        Returns:
            dict: The queries transformed into a dict with this structure::

                { "search[key]" : "value"}

        """
        queries = {}
        for k, v in kwargs.items():
            if k[-1] == "_":
                k = k[0:-1]
            queries[f"search[{k}]"] = v
        return queries

    def _generate_query_keys(self, **kwargs) -> str:
        """Converts keyword arguments into query dict.

        Args:
            **kwargs: Queries to convert.

        Returns:
            dict: The queries transformed into a dict.
        """
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
    ) -> RequestResponse:
        """Internal fetch of posts search.

        In general you don't need to touch this. If you want to override
        how the call works, change :meth:`._call_api` instead.

        Args:
            tags: The tags to search.
            limit: Limits the amount of notes returned to the number specified.
            page: The page that will be returned.

        Returns:
            JSON object of server's response.

        """
        if isinstance(tags, list):
            tags = " ".join(tags)
        return self._call_api("GET", POSTS_URL, tags=tags, limit=limit, page=page)  # type: ignore

    def _get_post(self, post_id: int) -> RequestResponse:
        """Internal fetch of posts search.

        In general you don't need to touch this. If you want to override
        how the call works, change :meth:`._call_api` instead.

        Args:
            post_id: The post's ID to look up.

        Returns:
            JSON object of server's response.

        """
        url = POST_URL + str(post_id) + ".json"
        return self._call_api("GET", url)  # type: ignore

    def _get_flags(
        self,
        post_id: int = None,
        creator_id: int = None,
        creator_name: str = None,
        limit: int = None,
    ) -> ArrayRequestResponse:
        """Internal fetch of flags search.

        In general you don't need to touch this. If you want to override
        how the call works, change :meth:`._call_api` instead.

        Args:
            post_id: The ID of the flagged post.
            creator_id: The user’s ID that created the flag.
            creator_name: The user’s name that created the flag.
            limit: Limits the amount of notes returned to the number specified.

        Returns:
            JSON object of server's response.

        """
        queries: dict = self._convert_search_query(
            post_id=post_id, creator_id=creator_id, creator_name=creator_name
        )
        queries["limit"] = limit

        return self._call_api("GET", FLAGS_URL, **queries)  # type: ignore

    def _get_notes(
        self,
        body_matches: str = None,
        post_id: int = None,
        post_tags_match: Union[List, str] = None,
        creator_name: str = None,
        creator_id: str = None,
        is_active: bool = None,
        limit: int = None,
    ) -> ArrayRequestResponse:
        """Internal fetch of notes search.

        In general you don't need to touch this. If you want to override
        how the call works, change :meth:`._call_api` instead.

        Args:
            body_matches: The note's body matches the given terms.
                 Use a * in the search terms to search for raw strings.
            post_id: The post where the note is located.
            post_tags_match: The note's post's tags match the given terms.
                 Meta-tags are not supported.
            creator_name: The creator's name. Exact match.
            creator_id: The creator's user id.
            is_active: Can be ``True`` or ``False``.
            limit: Limits the amount of notes returned to the number specified.

        Returns:
            JSON object of server's response.

        """
        if isinstance(post_tags_match, list):
            post_tags_match = " ".join(post_tags_match)

        is_active_str: str
        if is_active is not None:
            is_active_str = str(is_active).lower()
        else:
            is_active_str = ""

        queries: dict = self._convert_search_query(
            body_matches=body_matches,
            post_id=post_id,
            post_tags_match=post_tags_match,
            creator_name=creator_name,
            creator_id=creator_id,
            is_active=is_active_str if is_active_str else None,
        )
        queries["limit"] = limit

        return self._call_api("GET", NOTES_URL, **queries)  # type: ignore

    def _get_pools(
        self,
        name_matches: str = None,
        id_: Union[str, int, List[int]] = None,
        description_matches: str = None,
        creator_name: str = None,
        creator_id: int = None,
        is_active: bool = None,
        is_deleted: bool = None,
        category: str = None,
        order: str = None,
        limit: int = None,
    ) -> ArrayRequestResponse:
        """Internal fetch of pools search.

        In general you don't need to touch this. If you want to override
        how the call works, change :meth:`._call_api` instead.

        Args:
            name_matches: Search for pool names.
            id_: Search for a pool ID. Multiple IDs are fine.
                .. warning:: Take note of the underscore (_) mark!
            description_matches: Search for pool descriptions.
            creator_name: Search for pools based on creator name.
            creator_id: Search for pools based on creator ID.
            is_active: If the pool is active or hidden. (True/False)
            is_deleted: If the pool is deleted. (True/False)
            category: Can either be “series” or “collection”.
            order: The order that pools should be returned,
                can be any of: ``name``, ``created_at``, ``updated_at``, ``post_count``.
                If not specified it orders by ``updated_at``.
            limit: The limit of how many pools should be retrieved.

        Returns:
            JSON object of server's response.

        """
        if isinstance(id_, list):
            id_ = ",".join(map(str, id_))

        is_active_str: str
        if is_active is not None:
            is_active_str = str(is_active).lower()
        else:
            is_active_str = ""

        is_deleted_str: str
        if is_deleted is not None:
            is_deleted_str = str(is_deleted).lower()
        else:
            is_deleted_str = ""

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
            is_active=is_active_str if is_active_str else None,
            is_deleted=is_deleted_str if is_deleted_str else None,
            category=category,
            order=order,
        )
        queries["limit"] = limit
        return self._call_api("GET", POOLS_URL, **queries)  # type: ignore

    def _get_pool(self, pool_id: int) -> RequestResponse:
        """Internal fetch of pool lookup.

        In general you don't need to touch this. If you want to override
        how the call works, change :meth:`._call_api` instead.

        Args:
            pool_id: The pool's ID to look up.

        Returns:
            JSON object of server's response.

        """
        url = POOL_URL + str(pool_id) + ".json"
        return self._call_api("GET", url)  # type: ignore

    def login(self, username: str, api_key: str) -> None:
        """Supply login credentials to client.

        Args:
            username: Your e621 username.
            api_key: Your API key. Find it under "Account" on e621.
        """
        self._login = (username, api_key)

    @abstractmethod
    def posts(
        self,
        tags: Union[List, str] = None,
        limit: int = None,
        page: Union[int, str] = None,
    ) -> MaybeAwaitable[List[Post]]:
        """Search for posts.

        Args:
            tags: The tags to search.
            limit: Limits the amount of notes returned to the number specified.
            page: The page that will be returned.

        Returns:
            :obj:`list` of :class:`~yippi.Classes.Post` of the posts.

        """
        raise NotImplementedError

    @abstractmethod
    def post(self, post_id: int) -> MaybeAwaitable[Post]:
        """Fetch for a post.

        Args:
            post_id: The post's ID to look up.

        Returns:
            :class:`~yippi.Classes.Post` of the posts.

        """
        raise NotImplementedError

    @abstractmethod
    def flags(
        self, post_id: int = None, creator_id: int = None, creator_name: str = None
    ) -> MaybeAwaitable[List[Flag]]:
        """Search for flags

        Args:
            post_id: The ID of the flagged post.
            creator_id: The user’s ID that created the flag.
            creator_name: The user’s name that created the flag.
            limit: Limits the amount of notes returned to the number specified.

        Returns:
            :obj:`list` of :class:`~yippi.Classes.Flag` of the flags.

        """
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
    ) -> MaybeAwaitable[List[Note]]:
        """Search for notes.

        Args:
            body_matches: The note's body matches the given terms.
                 Use a * in the search terms to search for raw strings.
            post_id: The post where the note is located.
            post_tags_match: The note's post's tags match the given terms.
                 Meta-tags are not supported.
            creator_name: The creator's name. Exact match.
            creator_id: The creator's user id.
            is_active: Can be ``True`` or ``False``.
            limit: Limits the amount of notes returned to the number specified.

        Returns:
            :obj:`list` of :class:`~yippi.Classes.Note` of the notes.

        """
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
    ) -> MaybeAwaitable[List[Pool]]:
        """Search for pools.

        Args:
            name_matches: Search for pool names.
            id_: Search for a pool ID. Multiple IDs are fine.
                .. warning:: Take note of the underscore (_) mark!
            description_matches: Search for pool descriptions.
            creator_name: Search for pools based on creator name.
            creator_id: Search for pools based on creator ID.
            is_active: If the pool is active or hidden. (True/False)
            is_deleted: If the pool is deleted. (True/False)
            category: Can either be “series” or “collection”.
            order: The order that pools should be returned,
                can be any of: ``name``, ``created_at``, ``updated_at``, ``post_count``.
                If not specified it orders by ``updated_at``.
            limit: The limit of how many pools should be retrieved.

        Returns:
            :obj:`list` of :class:`~yippi.Classes.Pool` of the pools.

        """
        raise NotImplementedError

    @abstractmethod
    def pool(self, pool_id: int) -> MaybeAwaitable[Pool]:
        """Fetch for a pool.

        Args:
            pool_id: The pool's ID to look up.

        Returns:
            :class:`~yippi.Classes.Pool` of the pool.

        """
        raise NotImplementedError
