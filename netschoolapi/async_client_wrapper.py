import asyncio
import functools
from typing import Optional, Awaitable
from typing_extensions import Protocol

import httpx

from netschoolapi import errors

DEFAULT_REQUESTS_TIMEOUT = 5


class Requester(Protocol):

    def __call__(self, request: httpx.Request, follow_redirects=False) -> Awaitable:  # type: ignore
        pass


class AsyncClientWrapper:
    def __init__(
            self, async_client: httpx.AsyncClient,
            default_requests_timeout: int = None):
        self.client = async_client
        if default_requests_timeout is None:
            default_requests_timeout = DEFAULT_REQUESTS_TIMEOUT
        self._default_requests_timeout = default_requests_timeout

    def make_requester(self, requests_timeout: Optional[int]) -> Requester:
        # noinspection PyTypeChecker
        return functools.partial(self.request, requests_timeout)

    async def request(
            self, requests_timeout: Optional[int], request: httpx.Request,
            follow_redirects=False):
        if requests_timeout is None:
            requests_timeout = self._default_requests_timeout
        try:
            if requests_timeout == 0:
                return await self._infinite_request(
                    request, follow_redirects
                )
            else:
                return await asyncio.wait_for(self._infinite_request(
                    request, follow_redirects
                ), requests_timeout)
        except asyncio.TimeoutError:
            raise errors.NoResponseFromServer from None

    async def _infinite_request(self, request: httpx.Request, follow_redirects: bool):
        while True:
            try:
                response = await self.client.send(request, follow_redirects=follow_redirects)
            except httpx.ReadTimeout:
                await asyncio.sleep(0.1)
            else:
                return response
