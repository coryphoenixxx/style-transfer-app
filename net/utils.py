from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

MAX_IMAGE_SIZE = 1280


def calc_mean_std(feat, eps=1e-5):
    # eps is a small value added to the variance to avoid divide-by-zero.
    size = feat.size()
    assert (len(size) == 4)
    N, C = size[:2]
    feat_var = feat.view(N, C, -1).var(dim=2) + eps
    feat_std = feat_var.sqrt().view(N, C, 1, 1)
    feat_mean = feat.view(N, C, -1).mean(dim=2).view(N, C, 1, 1)
    return feat_mean, feat_std


def mean_variance_norm(feat):
    size = feat.size()
    mean, std = calc_mean_std(feat)
    normalized_feat = (feat - mean.expand(size)) / std.expand(size)
    return normalized_feat


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


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


async def draw_number(image_path, index):
    with Image.open(image_path) as base:
        base = await resize_image(base)
        w, h = base.size[0], base.size[1]
        temp_io = BytesIO()
        draw = ImageDraw.Draw(base)
        font_size = int(w * h / 6000)
        font = ImageFont.truetype('static/TooneyNoodleNF.ttf', font_size)
        draw.text((int(w / 5), int(h / 6)), str(index), (0, 0, 0), font=font)
        base.save(temp_io, format='JPEG')
        temp_io.seek(0)

        return temp_io
