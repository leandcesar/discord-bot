import aiohttp
from aiohttp.client import BasicAuth

from bot import config


async def get_colors_from_image(image_binary: bytes, /) -> list[dict[str, str]]:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{config.IMAGGA_API_URL}/{config.IMAGGA_API_VERSION}/colors",
            auth=BasicAuth(config.IMAGGA_API_KEY, config.IMAGGA_API_SECRET),
            data={"image": image_binary},
        ) as response:
            response.raise_for_status()
            data = await response.json()
            colors = data["result"]["colors"]["image_colors"] + data["result"]["colors"]["background_colors"]
            return colors
    return []
