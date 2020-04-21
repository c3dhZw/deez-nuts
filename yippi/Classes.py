import inspect
import os.path
import re
import warnings
from copy import deepcopy
from typing import List
from typing import Union

from .Constants import BASE_URL
from .Constants import NOTE_URL
from .Constants import NOTES_URL
from .Constants import POST_URL
from .Enums import Rating
from .Exceptions import UserError

regex = re.compile(
    r"^(?:http|ftp)s?://"
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
    r"localhost|"
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


class Post:
    """Representation of e621's Post object.

    Args:
        data (optional): The json server response of a ``/posts.json`` call.
        client (optional): The yippi client, used for api calls.

    Attributes:
        Refer to `e621 API docs`_ for available attributes.

    .. _e621 API docs:
        https://e621.net/wiki_pages/2425
    """

    def __init__(
        self, data: dict = None, client: Union["AsyncYippiClient", "YippiClient"] = None
    ):
        if data:
            self._original_data = deepcopy(data)
            self.id: int = data.get("id", None)
            self.created_at: str = data.get("created_at", None)
            self.updated_at: str = data.get("updated_at", None)
            self.file: dict = data.get("file", None)
            self.preview: dict = data.get("preview", None)
            self.sample: dict = data.get("sample", None)
            self.score: dict = data.get("score", None)
            self.tags: dict = data.get("tags", None)
            self.locked_tags: list = data.get("locked_tags", None)
            self.change_seq: int = data.get("change_seq", None)
            self.flags: dict = data.get("flags", None)
            self.rating: Rating = Rating(data.get("rating", None))
            self.fav_count: int = data.get("fav_count", None)
            self.sources: list = data.get("sources", None)
            self.pools: list = data.get("pools", None)
            self.relationships: dict = data.get("relationships", None)
            self.approver_id: int = data.get("approver_id", None)
            self.uploader_id: int = data.get("uploader_id", None)
            self.description: str = data.get("description", None)
            self.comment_count: int = data.get("comment_count", None)
            self.is_favorited: bool = data.get("is_favorited", None)
        self._client = client

    def __repr__(self):
        return "Post(id=%s)" % (self.id)

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

        deleted = []
        added = []
        if isinstance(original, dict):
            joined_original = []
            joined_new = []
            for k in original.keys():
                joined_original.extend(original[k])
                joined_new.extend(new[k])

            original = joined_original
            new = joined_new
        elif isinstance(original, str):
            original = original.split()
            new = new.split()

        deleted += self._diff_list(original, new)
        added += self._diff_list(new, original)

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
            dict: JSON response with keys ``score``, ``up``, ``down``, and ``our_score``.
                Where ``dict['our_score']`` is 1, 0, -1 depending on the action.
        """
        if not self._client:
            raise UserError("Yippi client isn't initialized.")

        if not self.id:
            raise UserError("Post does not come from e621 API.")

        if score not in (1, -1):
            raise UserError("Score must either be 1 or -1.")

        data = {"score": score, "no_unvote": replace}
        return self._client._call_api(
            "POST", BASE_URL + f"/{self.id}/votes.json", data=data
        )

    @classmethod
    def from_file(cls, path):
        if not os.path.exists(path):
            raise ValueError(f'Path "{path}" does not exist.')
        new_post = cls()
        new_post.file_path = path
        return new_post

    @classmethod
    def from_url(cls, url):
        if not regex.match(url):
            raise ValueError(f'URL "{url}" is invalid.')
        new_post = cls()
        new_post.file_url = url
        return new_post

    def upload(self):
        raise NotImplementedError

    def update(self, has_notes: bool, reason: str = None):
        """Updates the post. **This function has not been tested.**

        Args:
            has_notes: Does the post have embedded notes or not.
            reason (optional): Reasoning behind the edit. Defaults to None.

        Raises:
            UserError: If the post did not come from any Post endpoint or if no changes has been made.
        """
        warnings.warn("This function has not been tested and should not be used.")
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

        if self.relationships["parent_id"] != original.relationships["parent_id"]:
            post_data["post[parent_id]"] = self.relationships["parent_id"]
            post_data["post[old_parent_id]"] = original.relationships["parent_id"]

        if self["description"] != original["description"]:
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

        post_data.extend(
            {
                "post[edit_reason]": reason,
                "post[has_embedded_notes]": str(has_notes).lower(),
            }
        )

        return self._client._call_api("PATCH", POST_URL + str(self.id), data=post_data)


class Note:
    """Representation of e621's Note object.

    Args:
        data (optional): The json server response of a ``/notes.json`` call.
        client (optional): The yippi client, used for api calls.

    Attributes:
        Refer to `e621 API docs`_ for available attributes.

    .. _e621 API docs:
        https://e621.net/wiki_pages/2425
    """

    def __init__(
        self, data: dict = None, client: Union["AsyncYippiClient", "YippiClient"] = None
    ):
        if data:
            self.id: int = data.get("id", None)
            self.created_at: str = data.get("created_at", None)
            self.updated_at: str = data.get("updated_at", None)
            self.creator_id: int = data.get("creator_id", None)
            self.x: int = data.get("x", None)
            self.y: int = data.get("y", None)
            self.width: int = data.get("width", None)
            self.height: int = data.get("height", None)
            self.version: int = data.get("version", None)
            self.is_active: bool = data.get("is_active", None)
            self.post_id: int = data.get("post_id", None)
            self.body: str = data.get("body", None)
            self.creator_name: str = data.get("creator_name", None)
        self._client = client

    def __repr__(self):
        return "Note(id=%s)" % (self.id)

    def get_post(self) -> "Post":
        """Fetch the post linked with this note.

        Returns:
            :class:`yippi.Classes.Post`: The post linked with this note.
        """
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
        client: Union["AsyncYippiClient", "YippiClient"],
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
        post_data = {
            "note[x]": self.x,
            "note[y]": self.y,
            "note[width]": self.width,
            "note[height]": self.height,
            "note[body]": self.body,
        }
        return self._client._call_api("PUT", NOTE_URL + str(self.id), data=post_data)

    def upload(self) -> dict:
        """Uploads the note. **This function has not been tested.**

        Returns:
            dict: JSON status response from API.
        """
        warnings.warn("This function has not been tested and should not be used.")
        post_data = {
            "note[post_id]": self.post_id,
            "note[x]": self.x,
            "note[y]": self.y,
            "note[width]": self.width,
            "note[height]": self.height,
            "note[body]": self.body,
        }
        return self._client._call_api("PUT", NOTES_URL, data=post_data)

    def revert(self, version_id: str) -> dict:
        """Reverts note to specified version_id. **This function has not been tested.**

        Args:
            version_id: Target version to revert.

        Raises:
            UserError: Raised if
                - Note does not come from :meth:`~yippi.AbstractMethod.notes`.
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
        return self._client._call_api(
            "PUT", NOTE_URL + f"{self.id}/revert.json", data=data
        )

    def delete(self):
        warnings.warn("This function has not been tested and should not be used.")
        return self._client._call_api("DELETE", NOTE_URL + str(self.id))


class Pool:
    """Representation of e621's Pool object.

    Args:
        data (optional): The json server response of a ``pools.json`` call.
        client (optional): The yippi client, used for api calls.

    Attributes:
        Refer to `e621 API docs`_ for available attributes.

    .. _e621 API docs:
        https://e621.net/wiki_pages/2425
    """

    def __init__(
        self, data: dict = None, client: Union["AsyncYippiClient", "YippiClient"] = None
    ):
        if data:
            self.id: int = data.get("id", None)
            self.name: str = data.get("name", None)
            self.created_at: str = data.get("created_at", None)
            self.updated_at: str = data.get("updated_at", None)
            self.creator_id: int = data.get("creator_id", None)
            self.description: str = data.get("description", None)
            self.is_active: bool = data.get("is_active", None)
            self.category: str = data.get("category", None)
            self.is_deleted: bool = data.get("is_deleted", None)
            self.post_ids: list = data.get("post_ids", None)
            self.creator_name: str = data.get("creator_name", None)
            self.post_count: int = data.get("post_count", None)
        self._client = client

    def __repr__(self):
        return "Pool(id=%s, name=%s)" % (self.id, self.name)

    def _sort_posts(self, arr: List["Post"]):
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

    def _register_linked(self, arr: List["Post"]):
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
        result = []
        current_page = 1
        while len(result) < len(self.post_ids):
            result.extend(
                await self._client.posts("pool:" + str(self.id), page=current_page)
            )
            current_page += 1

        result = self._sort_posts(result)
        self._register_linked(result)
        return result

    def get_posts(self) -> List["Post"]:
        """Fetch all posts linked with this pool.

        If the client is an async client, it will automatically call :meth:`.get_posts_async()`.

        Returns:
            :obj:`list` of :class:`yippi.Classes.Post`: All the posts linked with this pool.
        """
        if inspect.iscoroutinefunction(self._client.post):
            return self.get_posts_async()

        result = []
        current_page = 1
        while len(result) < len(self.post_ids):
            result.extend(self._client.posts("pool:" + str(self.id), page=current_page))
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
        return self._client._call_api(
            "PUT", BASE_URL + f"/notes/{self.id}/revert.json", data=data
        )


class Flag:
    """Representation of e621's Flag object.

    Args:
        data (optional): The json server response of a ``post_flags.json`` call.
        client (optional): The yippi client, used for api calls.

    Attributes:
        Refer to `e621 API docs`_ for available attributes.

    .. _e621 API docs:
        https://e621.net/wiki_pages/2425
    """

    def __init__(
        self, data: dict = None, client: Union["AsyncYippiClient", "YippiClient"] = None
    ):
        if data:
            self.id: int = data.get("id", None)
            self.created_at: str = data.get("created_at", None)
            self.post_id: int = data.get("post_id", None)
            self.reason: str = data.get("reason", None)
            self.is_resolved: bool = data.get("is_resolved", None)
            self.updated_at: str = data.get("updated_at", None)
            self.is_deletion: bool = data.get("is_deletion", None)
            self.category: str = data.get("category", None)
        self._client = client

    def __repr__(self):
        return "Flag(id=%s)" % (self.id)

    def get_post(self):
        """Fetch the post linked with this flag.

        Returns:
            :class:`yippi.Classes.Post`: The post linked with this flag.
        """
        return self._client.post(self.post_id)

    @classmethod
    def create(cls):
        raise NotImplementedError
