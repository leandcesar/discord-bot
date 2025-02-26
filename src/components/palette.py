from __future__ import annotations

import io
import math
from collections import Counter
from collections.abc import Generator
from contextlib import contextmanager

from PIL import Image, ImageDraw

from src.types.color import Color

__all__ = ("Palette",)


class Palette:
    def __init__(self, colors: list[Color]) -> None:
        self.colors = colors

    @staticmethod
    def color_distance(color1: tuple[int, ...], color2: tuple[int, ...]) -> float:
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(color1, color2)))

    @classmethod
    def from_image(cls, image: Image.Image, /, *, top_n: int = 10) -> Palette:
        pixels = image.convert("RGB").getdata()
        pixels_counts = Counter(pixels)
        colors: list[Color] = []
        for (r, g, b), count in pixels_counts.most_common():
            if not any(cls.color_distance((r, g, b), color.rgb) < 15 for color in colors):
                color = Color(r, g, b)
                colors.append(color)
            if len(colors) >= top_n:
                break
        return cls(colors)

    @classmethod
    def from_bytes(cls, asset_bytes: bytes, /, *, top_n: int = 10) -> Palette:
        with io.BytesIO(asset_bytes) as asset_file:
            with Image.open(asset_file) as image:
                return cls.from_image(image, top_n=top_n)

    @contextmanager
    def draw(self) -> Generator[io.BytesIO]:
        width, height = 200, 200
        num_of_colors = len(self.colors)
        image = Image.new("RGB", (num_of_colors * width, height))
        draw_image = ImageDraw.Draw(image)
        for i, color in enumerate(self.colors):
            x, y = i * width, 0
            shape = [(x, y), (x + width, y + height)]
            draw_image.rectangle(shape, fill=color.rgb)

        with io.BytesIO() as image_binary:
            image.save(image_binary, "PNG")
            image_binary.seek(0)
            yield image_binary
