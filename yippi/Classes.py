import inspect


class Post:
    def __init__(self, data: dict = None, client=None):
        if data:
            self._original_data = data
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
            self.rating: str = data.get("rating", None)
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

    def _diff_list(self, this, that):
        result = []
        for e in this:
            if e not in that:
                result.append(e)
        return result

    def get_tags_difference(self) -> str:
        orig = self._original_data["tags"]
        new = self.tags

        deleted = []
        added = []
        for k in orig.keys():
            orig_key_tags = orig[k]
            new_key_tags = new[k]

            deleted += self._diff_list(orig_key_tags, new_key_tags)
            added += self._diff_list(new_key_tags, orig_key_tags)

        output = ""
        if added:
            output += " ".join(added) + " "
        if deleted:
            output += "-" + " -".join(deleted)
        return output


class Note:
    def __init__(self, data=None, client=None):
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

    def get_post(self):
        return self._client.post(self.post_id)


class Pool:
    def __init__(self, data=None, client=None):
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

    def _register_linked(self, arr):
        previous = None
        for current in arr:
            if previous:
                previous.next = current
                current.previous = previous
            previous = current

    async def get_posts_async(self):
        result = [await self._client.post(post_id) for post_id in self.post_ids]
        self._register_linked(result)
        return result

    def get_posts(self):
        if inspect.iscoroutinefunction(self._client.post):
            return self.get_posts_async()

        result = [self._client.post(post_id) for post_id in self.post_ids]
        self._register_linked(result)
        return result


class Flag:
    def __init__(self, data=None, client=None):
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
        return self._client.post(self.post_id)
