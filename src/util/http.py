from __future__ import annotations

import asyncio
import typing as t

import aiohttp


async def json_or_text(response: aiohttp.ClientResponse) -> dict[str, t.Any] | list[dict[str, t.Any]] | str:
    try:
        if "application/json" in response.headers["content-type"].lower():
            return await response.json()
    except KeyError:
        pass
    return await response.text(encoding="utf-8")


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

    def _ensure_session(self) -> None:
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession(connector=self.connector, loop=self.loop)

    async def close(self) -> None:
        if self._session:
            await self._session.close()

    async def request(self, method: str, url: str, **kwargs) -> dict[str, t.Any] | list[dict[str, t.Any]] | str:
        self._ensure_session()
        async with self._session.request(method, url, **kwargs) as response:
            response.raise_for_status()
            return await json_or_text(response)
