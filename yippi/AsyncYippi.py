import aiohttp
import asyncio
from .AbstractYippi import AbstractYippi
from .Exceptions import UserError

from ratelimit import limits


class AsyncYippiClient(AbstractYippi):
    def __init__(self, *args, loop: asyncio.AbstractEventLoop = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._loop = loop if loop else asyncio.get_event_loop()
        self._session = aiohttp.ClientSession(loop=loop)

    @limits(calls=2, period=60)
    async def _call_api(self, method, url, **kwargs):
        query_string = self._generate_query_keys(**kwargs)
        url += "?" + query_string
        r = await self._session.request(method, url, headers=self.headers)
        await self._verify_response(r)
        return await r.json()

    async def _verify_response(self, r):
        if r.status != 200 and r.status < 500:
            res = await r.json()
            if r.status >= 400:
                raise UserError(res["reason"])

        elif r.status > 500:
            r.raise_for_status()
