import asyncio
from io import BytesIO

from PIL import Image
from torchvision import transforms
from torchvision.utils import save_image

from .loader import *
from .utils import resize_image


def calc(number: int):
    """Makes the number a multiple of 80"""
    return (number // 80 + 1) * 80 if number % 80 > 40 else number // 80 * 80


def transform_to_tensor(size: tuple):
    return transforms.Compose([transforms.Resize((calc(size[1]), calc(size[0]))),
                               transforms.ToTensor()])


async def eval_func(content_io, style_io):
    content_img = Image.open(content_io).convert('RGB')
    style_img = Image.open(style_io).convert('RGB')

    content_img = await resize_image(content_img)
    style_img = await resize_image(style_img)

    content_tensor = transform_to_tensor(content_img.size)(content_img).to(device).unsqueeze(0)
    style_tensor = transform_to_tensor(style_img.size)(style_img).to(device).unsqueeze(0)

    with torch.no_grad():
        content4_1 = enc_4(enc_3(enc_2(enc_1(content_tensor))))
        content5_1 = enc_5(content4_1)
        style4_1 = enc_4(enc_3(enc_2(enc_1(style_tensor))))
        style5_1 = enc_5(style4_1)

        stylized = decoder(transform(content4_1, style4_1, content5_1, style5_1))
    buffer = BytesIO()

    save_image(stylized.cpu(), fp=buffer, format='jpeg')
    await asyncio.sleep(0.5)
    return buffer
