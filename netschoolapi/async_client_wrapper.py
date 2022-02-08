import asyncio
import functools
from typing import Optional, Awaitable, Protocol

import httpx

from netschoolapi import errors

DEFAULT_REQUESTS_TIMEOUT = 5


class Requester(Protocol):

    def __call__(
            self, path: str, method="GET", params: dict = None,
            json: dict = None, data: dict = None) -> Awaitable:
        pass


class AsyncClientWrapper:
    def __init__(
            self, async_client: httpx.AsyncClient,
            default_requests_timeout: int = None):
        self.client = async_client
        self._default_requests_timeout = (
            default_requests_timeout or DEFAULT_REQUESTS_TIMEOUT
        )

    def make_requester(self, requests_timeout: Optional[int]) -> Requester:
        # noinspection PyTypeChecker
        return functools.partial(self.request, requests_timeout)

    async def request(
            self, requests_timeout: Optional[int], path: str,
            method="GET", params: dict = None, json: dict = None,
            data: dict = None):
        try:
            return await asyncio.wait_for(self._infinite_request(
                path, method, params, json, data,
            ), requests_timeout or self._default_requests_timeout)
        except asyncio.TimeoutError:
            raise errors.NoResponseFromServer from None

    async def _infinite_request(
            self, path: str, method: str, params: Optional[dict],
            json: Optional[dict], data: Optional[dict]):
        while True:
            try:
                response = await self.client.request(
                    method, path, params=params, json=json, data=data
                )
            except httpx.ReadTimeout:
                pass
            else:
                return response
