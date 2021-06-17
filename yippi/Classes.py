from __future__ import annotations

import inspect
import mimetypes
import os.path
import re
import warnings
from copy import deepcopy
from enum import IntEnum
from typing import cast, TypeVar, Awaitable, Callable
from typing import TYPE_CHECKING
from typing import List
from typing import Optional
from typing import Union

from .Constants import BASE_URL
from .Constants import FAVORITES_URL
from .Constants import NOTE_URL
from .Constants import NOTES_URL
from .Constants import POST_URL
from .Constants import UPLOAD_URL
from .Enums import Rating
from .Exceptions import UserError

if TYPE_CHECKING:
    from .AbstractYippi import AbstractYippi

T = TypeVar("T")
MaybeAwaitable = Union[T, Awaitable[T]]

regex = re.compile(
    r"^(?:http|ftp)s?://"
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
    r"localhost|"
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


class _BaseMixin:
    def __init__(self, json_data: dict, client: AbstractYippi = None) -> None:
        if json_data:
            self._original_data: dict = deepcopy(json_data)
            self.id: Optional[int] = json_data.get("id")
            self.created_at: Optional[str] = json_data.get("created_at")
            self.updated_at: Optional[str] = json_data.get("updated_at")
        self._client = client


class Post(_BaseMixin):
    """Representation of e621's Post object.

    Args:
        data (optional): The json server response of a ``/posts.json`` call.
        client (optional): The yippi client, used for api calls.

    Attributes:
        All (Any): Refer to `e621 API docs`_ for available attributes.

    .. _e621 API docs:
        https://e621.net/wiki_pages/2425
    """

    def __init__(self, json_data=None, *args, **kwargs) -> None:
        super().__init__(json_data, *args, **kwargs)
        self.file_path: Optional[str] = None
        self.file_url: Optional[str] = None
        if json_data:
            self.file: dict = json_data.get("file")
            self.preview: dict = json_data.get("preview")
            self.sample: dict = json_data.get("sample")
            self.score: dict = json_data.get("score")
            self.tags: dict = json_data.get("tags")
            self.locked_tags: list = json_data.get("locked_tags")
            self.change_seq: int = json_data.get("change_seq")
            self.flags: dict = json_data.get("flags")
            self.rating: Rating = Rating(json_data.get("rating"))
            self.fav_count: int = json_data.get("fav_count")
            self.sources: list = json_data.get("sources")
            self.pools: list = json_data.get("pools")
            self.relationships: dict = json_data.get("relationships")
            self.approver_id: int = json_data.get("approver_id")
            self.uploader_id: int = json_data.get("uploader_id")
            self.description: str = json_data.get("description")
            self.comment_count: int = json_data.get("comment_count")
            self.is_favorited: bool = json_data.get("is_favorited")

    def __repr__(self) -> str:
        if self.id:
            name = f"Post(id={self.id})"
        elif self.file_path:
            name = f"Post(file_path={self.file_path})"
        elif self.file_url:
            name = f"Post(file_url={self.file_url})"
        else:
            name = "Post()"
        return name

    def __int__(self) -> int:
        return getattr(self, "id", -1)

    def _diff_list(self, this: List, that: List) -> List[str]:
        """Find differences between two list.

        Args:
            this: List to check from
            that: Base list to check.

        Returns:
            :obj:`list` of :obj:`str`: List of strings that exists in ``this``, but not in ``that``.
        """

        result = []
        for e in this:
            if e not in that:
                result.append(e)
        return result

    def _generate_difference(
        self, original: Union[List, dict, str], new: Union[List, dict, str]
    ) -> str:
        """Generate difference of two dict or list, formatted based on e621's format.

        The e621 format is all the new tags, with removed tags is prepended with a ``-`` sign.

        For example: ``dog -cat`` adds dog and removes cat.

        Returns:
            str: e621 formatted difference string.
        """
        if type(original) != type(new):
            raise ValueError("Original and new must have same type.")

        # Transform dict and str into list of differences.
        if isinstance(original, dict) and isinstance(new, dict):
            joined_original = []  # type: List[str]
            joined_new = []  # type: List[str]
            for k in original.keys():
                joined_original.extend(original[k])
                joined_new.extend(new[k])

            original = joined_original
            new = joined_new
        elif isinstance(original, str) and isinstance(new, str):
            original = original.split()
            new = new.split()

        # At this point, original and new has been transformed into list of tags.
        assert isinstance(original, list) and isinstance(new, list)
        deleted = self._diff_list(original, new)
        added = self._diff_list(new, original)

        output = ""
        if added:
            output += " ".join(added)
        if deleted:
            output += " -" + " -".join(deleted)
        return output.strip()

    def vote(self, score: int = 1, replace: bool = False) -> dict:
        """Vote the post.

        If you want to cancel your vote, repeat the same function again with same
        score value, but with replace set to False.

        Args:
            score (optional): Score to be given, this could be either 1 or -1, with
            1 represents vote up and -1 represent vote down. Defaults to 1.
            replace (optional): Replaces old vote or not. Defaults to False.

        Raises:
            UserError: Raised if
                - Post does not come from :meth:`~yippi.AbstractMethod.post`
                    or :meth:`~yippi.AbstractMethod.posts`.
                - If the value of ``score`` is out of scope.
                - ``client`` kwargs was not supplied.

        Returns:
            dict:
                JSON response with keys ``score``, ``up``, ``down``, and ``our_score``.
                Where ``dict['our_score']`` is 1, 0, -1 depending on the action.
        """
        if not self._client:
            raise UserError("Yippi client isn't initialized.")

        if not self.id:
            raise UserError("Post does not come from e621 API.")

        if score not in (1, -1):
            raise UserError("Score must either be 1 or -1.")

        data = {"score": score, "no_unvote": replace}
        api_response = self._client._call_api(
            "POST", POST_URL + f"/{self.id}/votes.json", data=data
        )
        api_response = cast(dict, api_response)
        return api_response

    @classmethod
    def from_file(cls, path) -> 'Post':
        new_post = cls()
        new_post.file = open(path, "rb")
        new_post.file_path = path
        new_post.file_name = os.path.basename(path)
        return new_post

    @classmethod
    def from_url(cls, url) -> 'Post':
        if not regex.match(url):
            raise ValueError(f'URL "{url}" is invalid.')
        new_post = cls()
        new_post.file_url = url
        return new_post

    def upload(self) -> None:
        warnings.warn("This function has not been tested and should not be used.")
        if isinstance(self.tags, str):
            tags = self.tags
        elif isinstance(self.tags, (list, tuple)):
            tags = " ".join(self.tags)
        elif isinstance(self.tags, dict):
            tags_list = []
            for k in self.tags.keys():
                tags_list.extend(self.tags[k])
            tags = " ".join(self.tags)
        else:
            raise UserError("Tags must be in a form of string, list, tuple or dict.")

        sources = "\n".join(self.sources)
        file = None
        post_data = {
            "upload[tag_string]": tags,
            "upload[rating]": self.rating.value,
            "upload[source]": sources,
            "upload[description]": self.description or "",
            "upload[parent_id]": getattr(self, "parent_id", ""),
            "upload[locked_tags]": self.locked_tags or "",
            "uploaad[locked_rating]": str(
                getattr(self, "locked_rating", False)
            ).lower(),
        }
        if hasattr(self, "file_url"):
            post_data["upload[direct_url]"] = self.file_url
        else:
            file_mime = mimetypes.guess_type(self.file_name)[0]
            file = {"upload[file]": (self.file_name, self.file, file_mime, {})}

        return self._client._call_api("POST", UPLOAD_URL, files=file, data=post_data)

    def update(self, has_notes: bool, reason: str = None) -> Union[List[dict], dict]:
        """Updates the post. **This function has not been tested.**

        Args:
            has_notes: Does the post have embedded notes or not.
            reason (optional): Reasoning behind the edit. Defaults to None.

        Raises:
            UserError: If the post did not come from any Post endpoint or if no changes has been made.
        """
        warnings.warn("This function has not been tested and should not be used.")
        if not self._client:
            raise UserError("Yippi client isn't initialized.")

        if not self._original_data:
            raise UserError("Post object did not come from Post endpoint.")

        post_data = {}
        original = self._original_data

        # Not sure if these are the "good" implementation to this, maybe it could be
        # a little bit more easier to handle without spamming "if"s...
        delta_tags = self._generate_difference(original["tags"], self.tags)
        if delta_tags:
            post_data["post[tag_string_diff]"] = delta_tags

        delta_source = self._generate_difference(original["sources"], self.sources)
        if delta_source:
            post_data["post[source_diff]"] = delta_source

        if self.relationships["parent_id"] != original["relationships"]["parent_id"]:
            post_data["post[parent_id]"] = self.relationships["parent_id"]
            post_data["post[old_parent_id]"] = original["relationships"]["parent_id"]

        if self.description != original["description"]:
            post_data["post[description]"] = self.description
            post_data["post[old_description]"] = original["description"]

        if self.rating._value_ != original["rating"]:
            post_data["post[rating]"] = self.rating._value_
            post_data["post[old_rating]"] = original["rating"]

        if self.flags["rating_locked"] != original["flags"]["rating_locked"]:
            post_data["post[is_rating_locked]"] = str(
                self.flags["rating_locked"]
            ).lower()

        if self.flags["note_locked"] != original["flags"]["note_locked"]:
            post_data["post[is_note_locked]"] = str(self.flags["note_locked"]).lower()

        if not post_data:
            raise UserError("No changes has been made to the object.")

        post_data.update(
            {
                "post[edit_reason]": reason or "",
                "post[has_embedded_notes]": str(has_notes).lower(),
            }
        )

        return self._client._call_api("PATCH", POST_URL + str(self.id), data=post_data)

    def favorite(self) -> dict:
        if not self._original_data:
            raise UserError("Post object did not come from Post endpoint.")

        post_data = {"post_id": str(self.id)}
        return self._client._call_api("POST", FAVORITES_URL + ".json", data=post_data)

    def unfavorite(self) -> None:
        if not self._original_data:
            raise UserError("Post object did not come from Post endpoint.")
        self._client._call_api("DELETE", f"{FAVORITES_URL}/{str(self.id)}.json")


class Note(_BaseMixin):
    """Representation of e621's Note object.

    Args:
        data (optional): The json server response of a ``/notes.json`` call.
        client (optional): The yippi client, used for api calls.

    Attributes:
        All (Any): Refer to `e621 API docs`_ for available attributes.

    .. _e621 API docs:
        https://e621.net/wiki_pages/2425
    """

    def __init__(self, json_data=None, *args, **kwargs) -> None:
        super().__init__(json_data, *args, **kwargs)
        self.creator_id: int = json_data.get("creator_id")
        self.x: int = json_data.get("x")
        self.y: int = json_data.get("y")
        self.width: int = json_data.get("width")
        self.height: int = json_data.get("height")
        self.version: int = json_data.get("version")
        self.is_active: bool = json_data.get("is_active")
        self.post_id: int = json_data.get("post_id")
        self.body: str = json_data.get("body")
        self.creator_name: str = json_data.get("creator_name")

    def __repr__(self) -> str:
        return f"Note(id={self.id})"

    def get_post(self) -> MaybeAwaitable["Post"]:
        """Fetch the post linked with this note.

        Returns:
            :class:`yippi.Classes.Post`: The post linked with this note.
        """
        if not self._client:
            raise UserError("Yippi client isn't initialized.")

        return self._client.post(self.post_id)

    @classmethod
    def create(
        cls,
        post: Union[Post, int],
        x: int,
        y: int,
        width: int,
        height: int,
        body: str,
        client: AbstractYippi,
    ) -> "Note":
        new_post = cls(client=client)
        new_post.post_id = int(post)
        new_post.x = x
        new_post.y = y
        new_post.width = width
        new_post.height = height
        new_post.body = body
        return new_post

    def update(self) -> dict:
        """Updates the note. **This function has not been tested.**

        Returns:
            dict: JSON status response from API.
        """

        warnings.warn("This function has not been tested and should not be used.")
        if not self._client:
            raise UserError("Yippi client isn't initialized.")

        post_data = {
            "note[x]": self.x,
            "note[y]": self.y,
            "note[width]": self.width,
            "note[height]": self.height,
            "note[body]": self.body,
        }
        api_response = self._client._call_api(
            "PUT", NOTE_URL + str(self.id), data=post_data
        )
        api_response = cast(dict, api_response)
        return api_response

    def upload(self) -> dict:
        """Uploads the note. **This function has not been tested.**

        Returns:
            dict: JSON status response from API.
        """
        warnings.warn("This function has not been tested and should not be used.")
        if not self._client:
            raise UserError("Yippi client isn't initialized.")

        post_data = {
            "note[post_id]": self.post_id,
            "note[x]": self.x,
            "note[y]": self.y,
            "note[width]": self.width,
            "note[height]": self.height,
            "note[body]": self.body,
        }
        api_response = self._client._call_api("PUT", NOTES_URL, data=post_data)
        api_response = cast(dict, api_response)
        return api_response

    def revert(self, version_id: str) -> dict:
        """Reverts note to specified version_id. **This function has not been tested.**

        Args:
            version_id: Target version to revert.

        Raises:
            UserError: Raised if
                - Note does not come from :meth:`~yippi.AbstractMethod.notes`.
                - ``client`` kwags was not supplied.

        Returns:
            dict: JSON status response from API.
        """
        warnings.warn("This function has not been tested and should not be used.")
        if not self._client:
            raise UserError("Yippi client isn't initialized.")

        if not self.id:
            raise UserError("Post does not come from e621 API.")

        data = {"version_id": version_id}
        api_response = self._client._call_api(
            "PUT", NOTE_URL + f"{self.id}/revert.json", data=data
        )
        api_response = cast(dict, api_response)
        return api_response

    def delete(self) -> None:
        warnings.warn("This function has not been tested and should not be used.")
        self._client._call_api("DELETE", NOTE_URL + str(self.id))


class Pool(_BaseMixin):
    """Representation of e621's Pool object.

    Args:
        data (optional): The json server response of a ``pools.json`` call.
        client (optional): The yippi client, used for api calls.

    Attributes:
        All (Any): Refer to `e621 API docs`_ for available attributes.

    .. _e621 API docs:
        https://e621.net/wiki_pages/2425
    """

    def __init__(self, json_data=None, *args, **kwargs) -> None:
        super().__init__(json_data, *args, **kwargs)
        if json_data:
            self.name: str = json_data.get("name")
            self.creator_id: int = json_data.get("creator_id")
            self.description: str = json_data.get("description")
            self.is_active: bool = json_data.get("is_active")
            self.category: str = json_data.get("category")
            self.is_deleted: bool = json_data.get("is_deleted")
            self.post_ids: list = json_data.get("post_ids")
            self.creator_name: str = json_data.get("creator_name")
            self.post_count: int = json_data.get("post_count")

    def __repr__(self) -> str:
        return f"Pool(id={self.id}, name={self.name})"

    def _sort_posts(self, arr: List["Post"]) -> List["Post"]:
        """Sort a list of post based on page numbering.

        The way it works is to sort it based on what has been provided on ``.post_ids``.
        Thus it will sort based on page number instead of e621's liking.

        Args:
            arr: List of post to be sorted.
        """
        sorted_array = []
        for post_id in self.post_ids:
            sorted_array.append(next(p for p in arr if p.id == post_id))
        return sorted_array

    def _register_linked(self, arr: List["Post"]) -> None:
        """Register a series of posts to have ``.continue`` and ``.previous`` attribute.

        Useful for those who are lazy to track down index number.

        Args:
            arr: Series of posts to register.
        """
        previous = None
        for current in arr:
            if previous:
                previous.next = current
                current.previous = previous
            previous = current

    async def get_posts_async(self) -> List["Post"]:
        """Async representation of :meth:`.get-posts()`

        Returns:
            :obj:`list` of :class:`yippi.Classes.Post`: All the posts linked with this pool.
        """
        if not self._client:
            raise UserError("Yippi client isn't initialized.")

        result: List["Post"] = []
        get_posts_func = cast(Callable[..., Awaitable[List[Post]]], self._client.posts)

        current_page = 1
        while len(result) < len(self.post_ids):
            result.extend(
                await get_posts_func("pool:" + str(self.id), page=current_page)
            )
            current_page += 1

        result = self._sort_posts(result)
        self._register_linked(result)
        return result

    def get_posts(self) -> MaybeAwaitable[List["Post"]]:
        """Fetch all posts linked with this pool.

        If the client is an async client, it will automatically call :meth:`.get_posts_async()`.

        Returns:
            :obj:`list` of :class:`yippi.Classes.Post`: All the posts linked with this pool.
        """
        if not self._client:
            raise UserError("Yippi client isn't initialized.")

        if inspect.iscoroutinefunction(self._client.post):
            return self.get_posts_async()

        result: List["Post"] = []
        get_posts_func = cast(Callable[..., List[Post]], self._client.posts)

        current_page = 1
        while len(result) < len(self.post_ids):
            result.extend(get_posts_func("pool:" + str(self.id), page=current_page))
            current_page += 1

        result = self._sort_posts(result)
        self._register_linked(result)
        return result

    @classmethod
    def create(cls):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def revert(self, version_id: str) -> dict:
        """Reverts note to specified version_id. **This function has not been tested.**

        Args:
            version_id: Target version to revert.

        Raises:
            UserError: Raised if
                - Pool does not come from :meth:`~yippi.AbstractMethod.pools`.
                - ``client`` kwargs was not supplied.

        Returns:
            dict: JSON status response from API.
        """
        warnings.warn("This function has not been tested and should not be used.")
        if not self._client:
            raise UserError("Yippi client isn't initialized.")

        if not self.id:
            raise UserError("Post does not come from e621 API.")

        data = {"version_id": version_id}
        api_response = self._client._call_api(
            "PUT", BASE_URL + f"/notes/{self.id}/revert.json", data=data
        )
        api_response = cast(dict, api_response)
        return api_response


class Flag(_BaseMixin):
    """Representation of e621's Flag object.

    Args:
        data (optional): The json server response of a ``post_flags.json`` call.
        client (optional): The yippi client, used for api calls.

    Attributes:
        All (Any): Refer to `e621 API docs`_ for available attributes.

    .. _e621 API docs:
        https://e621.net/wiki_pages/2425
    """

    def __init__(self, json_data=None, *args, **kwargs) -> None:
        super().__init__(json_data, *args, **kwargs)
        if json_data:
            self.post_id: int = json_data.get("post_id")
            self.reason: str = json_data.get("reason")
            self.is_resolved: bool = json_data.get("is_resolved")
            self.is_deletion: bool = json_data.get("is_deletion")
            self.category: str = json_data.get("category")

    def __repr__(self) -> str:
        return f"Flag(id={self.id})"

    def get_post(self) -> 'Post':
        """Fetch the post linked with this flag.

        Returns:
            :class:`yippi.Classes.Post`: The post linked with this flag.
        """
        return self._client.post(self.post_id)

    @classmethod
    def create(cls):
        raise NotImplementedError


class TagCategory(IntEnum):
    GENERAL = 0
    ARTIST = 1
    COPYRIGHT = 3
    CHARACTER = 4
    SPECIES = 5
    INVALID = 6
    META = 7
    LORE = 8


class Tag(_BaseMixin):
    def __init__(self, json_data=None, *args, **kwargs) -> None:
        super().__init__(json_data, *args, **kwargs)
        if json_data:
            self.name: str = json_data.get("name")
            self.post_count: int = json_data.get("post_count")
            self.related_tags: List[str] = json_data.get("related_tags")
            self.related_tags_updated_at = json_data.get("related_tags_updated_at")
            self.category: TagCategory = TagCategory(json_data.get("category"))
            self.is_locked: bool = json_data.get("is_locked")
