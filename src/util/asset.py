from __future__ import annotations

import io
from collections.abc import Generator
from contextlib import contextmanager

from PIL import Image


@contextmanager
def concatenate_assets(
    assets_bytes: list[bytes],
    /,
    *,
    columns: str | int,
    rows: str | int,
) -> Generator[io.BytesIO]:
    images = [Image.open(io.BytesIO(img)) for img in assets_bytes]
    min_size = min(img.size[0] for img in images)
    resized_images = [img.resize((min_size, min_size)) for img in images]
    total_width = int(columns) * min_size
    total_height = int(rows) * min_size
    image = Image.new("RGBA", (total_width, total_height))
    for i, img in enumerate(resized_images):
        row = i // int(columns)
        col = i % int(columns)
        image.paste(img, (col * min_size, row * min_size))
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
