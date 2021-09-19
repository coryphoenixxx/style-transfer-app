from PIL import Image
from torchvision import transforms
from torchvision.utils import save_image

from .loader import *


def eval_func(content_url, style_url, user_id):
    content_img = transforms.ToTensor()(Image.open(content_url)).to(device).unsqueeze(0)
    style_img = transforms.ToTensor()(Image.open(style_url)).to(device).unsqueeze(0)

    with torch.no_grad():
        content4_1 = enc_4(enc_3(enc_2(enc_1(content_img))))
        content5_1 = enc_5(content4_1)
        style4_1 = enc_4(enc_3(enc_2(enc_1(style_img))))
        style5_1 = enc_5(style4_1)

        content_img = decoder(transform(content4_1, style4_1, content5_1, style5_1))
        content_img.clamp(0, 255)

    content_img = content_img.cpu()

    output_name = f'images/user{user_id}_stylized.jpg'
    save_image(content_img, output_name)
