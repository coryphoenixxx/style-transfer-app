from io import BytesIO

from torchvision import transforms
from torchvision.utils import save_image

from .loader import *


def calc(number):
    return (number // 80 + 1) * 80 if number % 80 > 40 else number // 80 * 80


def style_transform(size):
    return transforms.Compose([transforms.Resize((calc(size[1]), calc(size[0]))),
                               transforms.ToTensor()])


def eval_func(content_img_obj, style_img_obj):
    content_image = content_img_obj.convert('RGB')
    style_image = style_img_obj.convert('RGB')

    content = style_transform(content_image.size)(content_image).to(device).unsqueeze(0)
    style = style_transform(content_image.size)(style_image).to(device).unsqueeze(0)

    with torch.no_grad():
        content4_1 = enc_4(enc_3(enc_2(enc_1(content))))
        content5_1 = enc_5(content4_1)
        style4_1 = enc_4(enc_3(enc_2(enc_1(style))))
        style5_1 = enc_5(style4_1)

        stylized = decoder(transform(content4_1, style4_1, content5_1, style5_1))
    buffer = BytesIO()

    save_image(stylized.cpu(), fp=buffer, format='jpeg')

    return buffer.getvalue()
