from __future__ import annotations

import ast
import random

import disnake
from disnake.ext import commands

__all__ = (
    "HEX",
    "RGB",
    "Color",
)


class RGB(tuple[int, ...]):
    def __new__(cls, r: int, g: int, b: int, /) -> RGB:
        if not all(isinstance(c, int) for c in (r, g, b)):
            raise TypeError(f"Invalid type for RGB values: {type(r)}, {type(g)}, {type(b)}). All must be integers.")
        if not cls._is_valid_rgb(r, g, b):
            raise ValueError(f"Invalid RGB value: RGB({r},{g},{b}). Each value must be between 0 and 255.")
        return super().__new__(cls, (r, g, b))

    @classmethod
    def from_hex(cls, hex: HEX) -> RGB:
        return hex.to_rgb()

    @classmethod
    def random(cls) -> RGB:
        return cls(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))  # nosec # noqa: S311

    @commands.converter_method
    async def convert(cls, inter: disnake.CommandInteraction, rgb_value: str) -> RGB:  # noqa: N805
        r, g, b = ast.literal_eval(rgb_value.removeprefix("rgb"))
        return cls(r, g, b)  # type: ignore

    @staticmethod
    def _is_valid_rgb(r: int, g: int, b: int, /) -> bool:
        return (0 <= r <= 255) and (0 <= g <= 255) and (0 <= b <= 255)

    @property
    def r(self) -> int:
        return self[0]

    @property
    def g(self) -> int:
        return self[1]

    @property
    def b(self) -> int:
        return self[2]

    def __repr__(self) -> str:
        return f"RGB({self.r},{self.g},{self.b})"

    def __str__(self) -> str:
        return f"({self.r}, {self.g}, {self.b})"

    def to_hex(self) -> HEX:
        return HEX(f"{self.r:02X}{self.g:02X}{self.b:02X}")


class HEX(str):
    def __new__(cls, hex_value: str, /) -> HEX:
        if not isinstance(hex_value, str):
            raise TypeError(f"Invalid type for hex value: {type(hex_value)}. Must be a string.")
        if not cls._is_valid_hex(hex_value):
            raise ValueError(f"Invalid HEX value: {hex_value}. Must be a valid 6-character HEX code.")
        return super().__new__(cls, hex_value.lstrip("#").lower())

    @classmethod
    def from_rgb(cls, rgb: RGB) -> HEX:
        return rgb.to_hex()

    @classmethod
    def random(cls) -> HEX:
        return cls(f"#{random.randint(0x000000, 0xFFFFFF):06X}")  # nosec # noqa: S311

    @commands.converter_method
    async def convert(cls, inter: disnake.CommandInteraction, hex_value: str) -> HEX:  # noqa: N805
        return cls(hex_value)  # type: ignore

    @staticmethod
    def _is_valid_hex(value: str, /) -> bool:
        if value.startswith("#"):
            value = value[1:]
        return len(value) == 6 and all(c in "0123456789ABCDEFabcdef" for c in value)

    def __repr__(self) -> str:
        return f"HEX({self})"

    def __int__(self) -> int:
        return int(self, 16)

    def to_rgb(self) -> RGB:
        return RGB(int(self[0:2], 16), int(self[2:4], 16), int(self[4:6], 16))


class Color:
    def __init__(
        self,
        r: int | None = None,
        g: int | None = None,
        b: int | None = None,
        /,
        *,
        hex_value: str | None = None,
    ) -> None:
        self._rgb: RGB = None  # type: ignore
        self._hex: HEX = None  # type: ignore
        if hex_value:
            self.hex = HEX(hex_value)
        elif r is not None and g is not None and b is not None:
            self.rgb = RGB(r, g, b)
        else:
            raise ValueError("You must provide either an RGB tuple (r, g, b) or a HEX value.")

    @classmethod
    def from_rgb(cls, rgb: RGB) -> Color:
        return cls(rgb.r, rgb.g, rgb.b)

    @classmethod
    def from_hex(cls, hex_value: HEX) -> Color:
        return cls(hex_value=str(hex_value))

    @commands.converter_method
    async def convert(cls, inter: disnake.CommandInteraction, value: str) -> Color:  # noqa: N805
        if "," in value:
            rgb = await RGB.convert(inter, value)
            return cls.from_rgb(inter, rgb)  # type: ignore
        else:
            hex = await HEX.convert(inter, value)
            return cls.from_hex(hex)  # type: ignore

    @property
    def rgb(self) -> RGB:
        return self._rgb

    @rgb.setter
    def rgb(self, value: RGB) -> None:
        if not isinstance(value, RGB):
            raise TypeError(f"The value must be an instance of the RGB class, not {type(value)}.")
        if self._rgb != value:
            self._rgb = value
            self.hex = self._rgb.to_hex()

    @property
    def hex(self) -> HEX:
        return self._hex

    @hex.setter
    def hex(self, value: HEX) -> None:
        if not isinstance(value, HEX):
            raise TypeError(f"The value must be an instance of the HEX class, not {type(value)}.")
        if self._hex != value:
            self._hex = value
            self.rgb = self._hex.to_rgb()

    def __repr__(self) -> str:
        return f"Color(rgb={self.rgb}, hex={self.hex})"
