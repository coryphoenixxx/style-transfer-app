from PIL import Image
from torchvision import transforms
from torchvision.utils import save_image

from .loader import *


def calc(number):
    return (number // 80 + 1) * 80 if number % 80 > 40 else number // 80 * 80


def style_transform(size):
    return transforms.Compose([transforms.Resize((calc(size[1]), calc(size[0]))),
                               transforms.ToTensor()])


def eval_func(content_url, style_url, user_id):
    content_image = Image.open(content_url).convert('RGB')
    style_image = Image.open(style_url).convert('RGB')

    content = style_transform(content_image.size)(content_image).to(device).unsqueeze(0)
    style = transforms.ToTensor()(style_image).to(device).unsqueeze(0)

    with torch.no_grad():

        content4_1 = enc_4(enc_3(enc_2(enc_1(content))))
        content5_1 = enc_5(content4_1)
        style4_1 = enc_4(enc_3(enc_2(enc_1(style))))
        style5_1 = enc_5(style4_1)

        content = decoder(transform(content4_1, style4_1, content5_1, style5_1))
        content.clamp(0, 255)

    content = content.cpu()

    output_name = f'images/user{user_id}_stylized.jpg'
    save_image(content, output_name)
