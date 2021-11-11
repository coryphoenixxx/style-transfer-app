import asyncio
import torch
import torch.nn as nn

from io import BytesIO
from PIL import Image
from torchvision import transforms
from torchvision.utils import save_image

from app.utils import resize_image
from app.config import MAX_IMAGE_SIZE, EVAL_ITER, STATE_DICTS_DIR
from .network import decoder, vgg, Transform


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

transform = Transform(in_planes=512)

decoder.eval()
transform.eval()
vgg.eval()

decoder.load_state_dict(torch.load(STATE_DICTS_DIR / f'decoder_iter_{EVAL_ITER}.pth'))
transform.load_state_dict(torch.load(STATE_DICTS_DIR / f'transformer_iter_{EVAL_ITER}.pth'))
vgg.load_state_dict(torch.load(STATE_DICTS_DIR / 'vgg_normalised.pth'))

norm = nn.Sequential(*list(vgg.children())[:1])
enc_1 = nn.Sequential(*list(vgg.children())[:4])  # input -> relu1_1
enc_2 = nn.Sequential(*list(vgg.children())[4:11])  # relu1_1 -> relu2_1
enc_3 = nn.Sequential(*list(vgg.children())[11:18])  # relu2_1 -> relu3_1
enc_4 = nn.Sequential(*list(vgg.children())[18:31])  # relu3_1 -> relu4_1
enc_5 = nn.Sequential(*list(vgg.children())[31:44])  # relu4_1 -> relu5_1

norm.to(device)
enc_1.to(device)
enc_2.to(device)
enc_3.to(device)
enc_4.to(device)
enc_5.to(device)
transform.to(device)
decoder.to(device)


def calc(number: int) -> int:
    """Makes the number a multiple of 80 (fix incorrect matrix multiplication in Transform class)"""
    return (number // 80 + 1) * 80 if number % 80 > 40 else number // 80 * 80


def transform_to_tensor(img: Image) -> torch.Tensor:
    size = img.size
    return transforms.Compose([transforms.Resize((calc(size[1]), calc(size[0]))),
                               transforms.ToTensor()])(img)


async def eval(content_io: BytesIO, style_io: BytesIO) -> BytesIO:
    content_img = Image.open(content_io).convert('RGB')
    style_img = Image.open(style_io).convert('RGB')

    content_img = resize_image(content_img, MAX_IMAGE_SIZE)
    style_img = resize_image(style_img, MAX_IMAGE_SIZE)

    content_tensor = transform_to_tensor(content_img).to(device).unsqueeze(0)
    style_tensor = transform_to_tensor(style_img).to(device).unsqueeze(0)

    with torch.no_grad():
        content4_1 = enc_4(enc_3(enc_2(enc_1(content_tensor))))
        content5_1 = enc_5(content4_1)
        style4_1 = enc_4(enc_3(enc_2(enc_1(style_tensor))))
        style5_1 = enc_5(style4_1)

        stylized = decoder(transform(content4_1, style4_1, content5_1, style5_1))
    stylized_io = BytesIO()

    save_image(stylized.cpu(), fp=stylized_io, format='jpeg')

    await asyncio.sleep(0.5)
    return stylized_io
