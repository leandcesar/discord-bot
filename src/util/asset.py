from __future__ import annotations

import io
from collections.abc import Generator
from contextlib import contextmanager

from PIL import Image

__all__ = (
    "concatenate_assets",
    "to_black_and_white",
    "resize_asset",
)


@contextmanager
def concatenate_assets(
    asset1_bytes: bytes,
    asset2_bytes: bytes,
    /,
    *,
    side_by_side: bool = True,
) -> Generator[io.BytesIO]:
    asset1 = Image.open(io.BytesIO(asset1_bytes))
    asset2 = Image.open(io.BytesIO(asset2_bytes))
    if side_by_side:
        max_height = max(asset1.height, asset2.height)
        asset1_resized = asset1.resize((int(asset1.width * max_height / asset1.height), max_height))
        asset2_resized = asset2.resize((int(asset2.width * max_height / asset2.height), max_height))
        new_width = asset1_resized.width + asset2_resized.width
        image = Image.new("RGB", (new_width, max_height))
        image.paste(asset1_resized, (0, 0))
        image.paste(asset2_resized, (asset1_resized.width, 0))
    else:
        max_width = max(asset1.width, asset2.width)
        asset1_resized = asset1.resize((max_width, int(asset1.height * max_width / asset1.width)))
        asset2_resized = asset2.resize((max_width, int(asset2.height * max_width / asset2.width)))
        new_height = asset1_resized.height + asset2_resized.height
        image = Image.new("RGB", (max_width, new_height))
        image.paste(asset1_resized, (0, 0))
        image.paste(asset2_resized, (0, asset1_resized.height))

    asset1.close()
    asset2.close()

    with io.BytesIO() as image_binary:
        image.save(image_binary, "PNG")
        image_binary.seek(0)
        yield image_binary


@contextmanager
def to_black_and_white(asset_bytes: bytes) -> Generator[io.BytesIO]:
    image = Image.open(io.BytesIO(asset_bytes))
    bw_image = image.convert("L")

    with io.BytesIO() as image_binary:
        bw_image.save(image_binary, "PNG")
        image_binary.seek(0)
        yield image_binary


@contextmanager
def resize_asset(
    asset_bytes: bytes,
    *,
    width: int,
    height: int,
) -> Generator[io.BytesIO]:
    image = Image.open(io.BytesIO(asset_bytes))
    if image.size != (width, height):
        image = image.resize((width, height))

    with io.BytesIO() as image_binary:
        image.save(image_binary, "PNG")
        image_binary.seek(0)
        yield image_binary
