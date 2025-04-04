from __future__ import annotations

import random

import disnake
from disnake.ext import commands
from disnake.ext.commands.errors import BadArgument


class HEX(str):
    def __int__(self) -> int:
        return int(self, 16)

    @staticmethod
    def _validate(value: str) -> bool:
        return len(value) == 6 and all(c in "0123456789ABCDEFabcdef" for c in value)

    @property
    def rgb(self) -> tuple[int, int, int]:
        return (int(self[0:2], 16), int(self[2:4], 16), int(self[4:6], 16))

    @commands.converter_method
    async def convert(cls, inter: disnake.CommandInteraction, value: str) -> HEX:  # noqa: N805
        value = value.removeprefix("#").lower()
        if not cls._validate(value):
            raise BadArgument(f"Invalid HEX code: {value!r}")
        return cls(value)  # type: ignore[operator]

    @classmethod
    def random(cls) -> HEX:
        return cls(f"{random.randint(0x000000, 0xFFFFFF):06X}")  # nosec # noqa: S311
