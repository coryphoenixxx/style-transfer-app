from io import BytesIO

from PIL import Image
from torchvision import transforms
from torchvision.utils import save_image

from .loader import *


def calc(number):
    return (number // 80 + 1) * 80 if number % 80 > 40 else number // 80 * 80


def style_transform(size):
    return transforms.Compose([transforms.Resize((calc(size[1]), calc(size[0]))),
                               transforms.ToTensor()])


MAX_IMAGE_SIZE = 1280


async def resize_image(img_obj: Image):
    width, height = img_obj.width, img_obj.height

    if width > MAX_IMAGE_SIZE or height > MAX_IMAGE_SIZE:
        if width > height:
            new_width = MAX_IMAGE_SIZE
            new_height = MAX_IMAGE_SIZE * height // width
        else:
            new_width = MAX_IMAGE_SIZE * width // height
            new_height = MAX_IMAGE_SIZE

        img_obj = img_obj.resize((new_width, new_height))
        return img_obj
    return img_obj


async def eval_func(content_io, style_io):
    content_image = Image.open(content_io).convert('RGB')
    style_image = Image.open(style_io).convert('RGB')

    content_img_obj = await resize_image(content_image)
    style_img_obj = await resize_image(style_image)

    content = style_transform(content_img_obj.size)(content_img_obj).to(device).unsqueeze(0)
    style = style_transform(style_img_obj.size)(style_img_obj).to(device).unsqueeze(0)

    with torch.no_grad():
        content4_1 = enc_4(enc_3(enc_2(enc_1(content))))
        content5_1 = enc_5(content4_1)
        style4_1 = enc_4(enc_3(enc_2(enc_1(style))))
        style5_1 = enc_5(style4_1)

        stylized = decoder(transform(content4_1, style4_1, content5_1, style5_1))
    buffer = BytesIO()

    save_image(stylized.cpu(), fp=buffer, format='jpeg')

    return buffer
