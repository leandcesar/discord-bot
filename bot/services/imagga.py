# -*- coding: utf-8 -*-
from typing import Any

import aiohttp

from bot.core import config


async def get_colors_from_image(image_binary: bytes) -> list[dict[str, Any]]:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{config.IMAGGA_API_URL}/{config.IMAGGA_API_VERSION}/colors",
            auth=aiohttp.client.BasicAuth(config.IMAGGA_API_KEY, config.IMAGGA_API_SECRET),
            data={"image": image_binary},
        ) as response:
            response.raise_for_status()
            data = await response.json()
    colors = []
    colors.extend(data["result"]["colors"]["image_colors"])
    colors.extend(data["result"]["colors"]["background_colors"])
    colors = [dict(x) for x in {tuple(color.items()) for color in colors}]
    return [
        {
            "hex": color["html_code"],
            "rgb": (color["r"], color["g"], color["b"]),
            "name": color["closest_palette_color"],
        }
        for color in colors
    ]
