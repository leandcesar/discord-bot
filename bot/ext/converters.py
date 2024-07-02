import io
import os
import re

import disnake
from disnake.errors import HTTPException, NotFound
from disnake.ext import commands
from disnake.state import ConnectionState


class URL:
    PATTERN = re.compile(r"^(https?://)?(([a-zA-Z0-9-_]+\.)+[a-zA-Z]{2,6})(:\d+)?(/.*)?$", re.IGNORECASE)

    __slots__ = ("url", "_http")

    def __init__(self, *, url: str, state: ConnectionState) -> None:
        if URL.PATTERN.match(url) is None:
            raise ValueError()  # TODO: add message
        self.url: str = url
        self._http = state.http

    def __repr__(self) -> str:
        return f"<URL url={self.url!r}>"

    def __str__(self) -> str:
        return self.url

    @commands.converter_method
    async def convert(cls, inter: disnake.CommandInteraction, url: str):  # noqa: N805
        return cls(url=url, state=inter._state)  # type: ignore

    async def content_type(self) -> str | None:
        async with self._http.__session.head(self.url) as response:
            if response.status != 200:
                raise HTTPException(response, "failed to get content")
            return response.headers.get("content-type")

    async def read(self) -> bytes:
        async with self._http.__session.get(self.url) as response:
            if response.status == 200:
                return await response.read()
            elif response.status == 404:
                raise NotFound(response, "content not found")
            else:
                raise HTTPException(response, "failed to get content")

    async def save(self, fp: io.BufferedIOBase | os.PathLike, *, seek_begin: bool = True) -> int:
        data = await self.read()
        if isinstance(fp, io.BufferedIOBase):
            written = fp.write(data)
            if seek_begin:
                fp.seek(0)
            return written
        else:
            with open(fp, "wb") as f:
                return f.write(data)

    async def to_file(
        self,
        *,
        spoiler: bool = False,
        filename: str | None = None,
        description: str | None = None,
    ) -> disnake.File:
        data = await self.read()
        return disnake.File(io.BytesIO(data), filename=filename, spoiler=spoiler, description=description)


class HEX:
    PATTERN = re.compile(r"^#?([A-Fa-f0-9]{6})$", re.IGNORECASE)

    __slots__ = ("code", "value", "name", "rgb")

    def __init__(self, *, hex_code: str, name: str | None = None) -> None:
        code = HEX.PATTERN.match(hex_code)
        if code is None:
            raise ValueError()  # TODO: add message
        self.code: str = f"#{code.group(1)}"
        self.value: int = int(code.group(1), 16)
        self.name: str | None = name
        r = int(self.code[0:2], 16)
        g = int(self.code[2:4], 16)
        b = int(self.code[4:6], 16)
        self.rgb = (r, g, b)

    def __repr__(self) -> str:
        return f"<HEX code={self.code!r}>"

    def __str__(self) -> str:
        if self.name:
            return f"{self.name} ({self.code})"
        return self.code

    def __int__(self) -> int:
        return self.value

    @commands.converter_method
    async def convert(cls, inter: disnake.CommandInteraction, hex_code: str):  # noqa: N805
        return cls(hex_code=hex_code)  # type: ignore
