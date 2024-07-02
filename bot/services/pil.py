import io

from PIL import Image, ImageDraw


def save_image(image: Image.Image) -> io.BytesIO:
    image_binary = io.BytesIO()
    image.save(image_binary, "PNG")
    image_binary.seek(0)
    return image_binary


def create_image_from_rgb_colors(rgb_colors: list[tuple[int, int, int]]) -> io.BytesIO:
    num_of_colors = len(rgb_colors)
    width, height = 100, 100
    image = Image.new("RGB", (num_of_colors * width, height))
    draw_image = ImageDraw.Draw(image)
    for i, rgb_color in enumerate(rgb_colors):
        x, y = i * width, 0
        shape = [(x, y), (x + width, y + height)]
        draw_image.rectangle(shape, fill=rgb_color)
    return save_image(image)


def resize_image(image_binary: bytes, *, width: int, height: int) -> io.BytesIO:
    image = Image.open(io.BytesIO(image_binary))
    if image.size != (width, height):
        image = image.resize((width, height))
    return save_image(image)
