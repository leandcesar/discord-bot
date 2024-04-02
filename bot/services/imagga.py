from __future__ import annotations

import aiohttp

from bot import config

RGB = tuple[int, int, int]


class Color:
    def __init__(self, *, name: str, hex_code: str, rgb_code: RGB) -> None:
        self.name = name
        self.hex_code = hex_code
        self.rgb_code = rgb_code

    def __str__(self) -> str:
        return f"{self.name} ({self.hex_code})"

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Color):
            return self.__id__ == o.__id__
        return NotImplemented

    def __hash__(self):
        return hash(self.__id__)

    @property
    def __id__(self) -> tuple[str, RGB]:
        return (self.hex_code, self.rgb_code)

    @property
    def int_code(self) -> int:
        return int(self.hex_code.strip("#"), 16)


class Colors(set[Color]):
    async def from_image(self, image_binary: bytes) -> Colors:
        colors = await get_colors_from_image(image_binary)
        for color in colors:
            self.add(
                Color(
                    name=str(color["closest_palette_color"]),
                    hex_code=str(color["html_code"]),
                    rgb_code=(int(color["r"]), int(color["g"]), int(color["b"])),
                )
            )
        return self


async def get_colors_from_image(image_binary: bytes) -> list[dict[str, str]]:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{config.IMAGGA_API_URL}/{config.IMAGGA_API_VERSION}/colors",
            auth=aiohttp.client.BasicAuth(config.IMAGGA_API_KEY, config.IMAGGA_API_SECRET),
            data={"image": image_binary},
        ) as response:
            response.raise_for_status()
            data = await response.json()
            colors = data["result"]["colors"]["image_colors"] + data["result"]["colors"]["background_colors"]
            return colors
    return []
