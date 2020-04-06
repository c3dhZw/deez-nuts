from .Constants import *


class Post:
    def __init__(self, data):
        self._original_data = data
        self.id = data.get("id", None)
        self.created_at = data.get("created_at", None)
        self.updated_at = data.get("updated_at", None)
        self.file = data.get("file", None)
        self.preview = data.get("preview", None)
        self.sample = data.get("sample", None)
        self.score = data.get("score", None)
        self.tags = data.get("tags", None)
        self.locked_tags = data.get("locked_tags", None)
        self.change_seq = data.get("change_seq", None)
        self.flags = data.get("flags", None)
        self.rating = data.get("rating", None)
        self.fav_count = data.get("fav_count", None)
        self.sources = data.get("sources", None)
        self.pools = data.get("pools", None)
        self.relationships = data.get("relationships", None)
        self.approver_id = data.get("approver_id", None)
        self.uploader_id = data.get("uploader_id", None)
        self.description = data.get("description", None)
        self.comment_count = data.get("comment_count", None)
        self.is_favorited = data.get("is_favorited", None)

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
