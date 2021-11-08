from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from config import MAX_IMAGE_SIZE


async def resize_image(img: Image):
    width, height = img.width, img.height

    if width > MAX_IMAGE_SIZE or height > MAX_IMAGE_SIZE:
        if width > height:
            new_width = MAX_IMAGE_SIZE
            new_height = MAX_IMAGE_SIZE * height // width
        else:
            new_width = MAX_IMAGE_SIZE * width // height
            new_height = MAX_IMAGE_SIZE

        img = img.resize((new_width, new_height))
        return img
    return img


def cut_into_chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


async def draw_number(image_path, index):
    with Image.open(image_path) as img:
        img = await resize_image(img)
        w, h = img.size[0], img.size[1]
        numbered_img_io = BytesIO()
        draw = ImageDraw.Draw(img)
        font_size = int(w * h / 6000)
        font = ImageFont.truetype('static/TooneyNoodleNF.ttf', font_size)
        draw.text((int(w / 5), int(h / 6)), str(index), (0, 0, 0), font=font)
        img.save(numbered_img_io, format='JPEG')
        numbered_img_io.seek(0)

        return numbered_img_io
