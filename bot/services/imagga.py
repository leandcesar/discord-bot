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
        for color_data in colors:
            name = str(color_data["closest_palette_color"])
            hex_code = str(color_data["html_code"])
            rgb_code = (int(color_data["r"]), int(color_data["g"]), int(color_data["b"]))
            color = Color(name=name, hex_code=hex_code, rgb_code=rgb_code)
            self.add(color)
        return self


async def get_colors_from_image(image_binary: bytes) -> list[dict[str, str]]:
    async with aiohttp.ClientSession() as session:
        url = f"{config.IMAGGA_API_URL}/{config.IMAGGA_API_VERSION}/colors"
        auth = aiohttp.client.BasicAuth(config.IMAGGA_API_KEY, config.IMAGGA_API_SECRET)
        payload = {"image": image_binary}
        async with session.post(url, auth=auth, data=payload) as response:
            response.raise_for_status()
            data = await response.json()
            image_colors = data["result"]["colors"]["image_colors"]
            background_colors = data["result"]["colors"]["background_colors"]
            colors = image_colors + background_colors
            return colors
    return []
