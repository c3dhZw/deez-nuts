import requests
from .AbstractYippi import AbstractYippi
from .Exceptions import UserError
from typing import Union, List
from ratelimit import limits


class YippiClient(AbstractYippi):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._session = requests.Session()

    @limits(calls=2, period=60)
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
                raise UserError(res["reason"])

        elif r.status_code > 500:
            r.raise_for_status()

    def posts(
        self,
        tags: Union[List, str] = None,
        limit: int = None,
        page: Union[int, str] = None,
    ):
        result = self._get_posts(tags, limit, page)
        posts = result["posts"]
