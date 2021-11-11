from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


def resize_image(img: Image, max_size: int):
    width, height = img.width, img.height

    if width > max_size or height > max_size:
        if width > height:
            new_width = max_size
            new_height = max_size * height // width
        else:
            new_width = max_size * width // height
            new_height = max_size

        img = img.resize((new_width, new_height))
        return img
    return img


def cut_into_chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


async def draw_number(image_path, index):
    with Image.open(image_path) as img:
        # Telegram resize images to 1280px on one side, used for correct drawing of number
        img = resize_image(img, 1280)
        w, h = img.size[0], img.size[1]
        numbered_img_io = BytesIO()
        draw = ImageDraw.Draw(img)
        font_size = int(w * h / 6000)
        font = ImageFont.truetype('static/TooneyNoodleNF.ttf', font_size)
        draw.text((int(w / 5), int(h / 6)), str(index), (0, 0, 0), font=font)
        img.save(numbered_img_io, format='JPEG')
        numbered_img_io.seek(0)

        return numbered_img_io
