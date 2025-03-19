from __future__ import annotations

import asyncio
import typing as t

import aiohttp
import yarl

from src import errors, log

__all__ = (
    "APIHTTPClient",
    "Route",
    "json_or_text",
)

logger = log.get_logger(__name__)

SUCCESS_STATUS: int = 200


async def json_or_text(response: aiohttp.ClientResponse) -> dict[str, t.Any] | list[dict[str, t.Any]] | str:
    try:
        if "application/json" in response.headers["content-type"].lower():
            return await response.json()
    except KeyError:
        pass
    return await response.text(encoding="utf-8")


class Route:
    def __init__(self, method: str, url: str, **params: int | str | bool) -> None:
        self.method = method
        new_url: yarl.URL = yarl.URL(url).with_query(params)
        self.url: str = new_url.human_repr()


class APIHTTPClient:
    def __init__(
        self,
        connector: aiohttp.BaseConnector | None = None,
        *,
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
        self.loop = loop or asyncio.get_running_loop()
        self.connector = connector
        self._session: aiohttp.ClientSession = None  # type: ignore[reportAttributeAccessIssue]
        self.ensure_session()

    def ensure_session(self) -> None:
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession(connector=self.connector, loop=self.loop)

    def close(self) -> None:
        if self._session:
            self._session.close()

    async def request(
        self,
        route: Route,
        headers: dict[str, str] | None = None,
        json: dict[str, str] | None = None,
        **kwargs,
    ) -> dict[str, t.Any] | list[dict[str, t.Any]] | str:
        self.ensure_session()
        method = route.method
        url = route.url
        async with self._session.request(method, url, headers=headers, json=json, **kwargs) as response:
            logger.debug(f"{method} {url} returned {response.status}")
            data = await json_or_text(response)
            logger.debug(f"{method} {url} received {data}")
            if response.status == SUCCESS_STATUS:
                return data
            raise errors.HTTPError(method, url, response.status)
