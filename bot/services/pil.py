from io import BytesIO

from PIL import Image, ImageDraw


def create_image(width: int, height: int) -> Image.Image:
    return Image.new("RGB", (width, height))


def open_image(image_binary: bytes) -> Image.Image:
    return Image.open(BytesIO(image_binary))


def save_image(image: Image.Image) -> BytesIO:
    image_binary = BytesIO()
    image.save(image_binary, "PNG")
    image_binary.seek(0)
    return image_binary


def create_image_from_rgb_colors(rgb_colors: list[tuple[int, int, int]]) -> BytesIO:
    num_of_colors = len(rgb_colors)
    width, height = 100, 100
    image = create_image(num_of_colors * width, height)
    draw_image = ImageDraw.Draw(image)
    for i, rgb_color in enumerate(rgb_colors):
        x, y = i * width, 0
        shape = [(x, y), (x + width, y + height)]
        draw_image.rectangle(shape, fill=rgb_color)
    return save_image(image)


def resize_image(image_binary: bytes, *, size: tuple[int, int]) -> BytesIO:
    image = open_image(image_binary)
    if image.size != size:
        image = image.resize(size)
    return save_image(image)


def merge_images_horizontal(image_binary_1: bytes, image_binary_2: bytes) -> BytesIO:
    image_1 = open_image(image_binary_1)
    image_2 = open_image(image_binary_2)
    if image_1.height != image_2.height:
        image_1 = image_1.resize((int(image_1.width * image_2.height / image_1.height), image_2.height))
        image_2 = image_2.resize((int(image_2.width * image_1.height / image_2.height), image_1.height))
    image = create_image(image_1.width + image_2.width, image_1.height)
    image.paste(image_1, (0, 0))
    image.paste(image_2, (image_1.width, 0))
    return save_image(image)


def merge_images_vertical(image_binary_1: bytes, image_binary_2: bytes) -> BytesIO:
    image_1 = open_image(image_binary_1)
    image_2 = open_image(image_binary_2)
    if image_1.width != image_2.width:
        image_1 = image_1.resize((image_2.width, int(image_1.height * image_2.width / image_1.width)))
        image_2 = image_2.resize((image_1.width, int(image_2.height * image_1.width / image_2.width)))
    image = create_image(image_1.width, image_1.height + image_2.height)
    image.paste(image_1, (0, 0))
    image.paste(image_2, (0, image_1.height))
    return save_image(image)
