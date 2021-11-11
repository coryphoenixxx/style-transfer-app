import torch
import torch.backends.cudnn as cudnn

from PIL import Image, ImageFile
from tqdm import tqdm

from net.dataloader import init_loaders
from net.network import create_network
from config import START_ITER, MAX_ITER, SAVE_ITER, STATE_DICTS_DIR

cudnn.benchmark = True
Image.MAX_IMAGE_PIXELS = None  # Disable DecompressionBombError
ImageFile.LOAD_TRUNCATED_IMAGES = True  # Disable OSError: image file is truncated


def adjust_learning_rate(optimizer, iteration_count):
    lr = 1e-4 / (1.0 + 5e-5 * iteration_count)
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr


if __name__ == '__main__':
    avg_loss = 0

    device = torch.device('cuda:0')
    print(f"CUDA: {torch.cuda.is_available()}")

    content_iter, style_iter = init_loaders()
    network, decoder, vgg, optimizer = create_network()

    for i in tqdm(range(START_ITER, MAX_ITER)):
        adjust_learning_rate(optimizer, iteration_count=i)

        content_images = next(content_iter).to(device)
        style_images = next(style_iter).to(device)

        loss_c, loss_s, l_identity1, l_identity2 = network(content_images, style_images)
        loss_c = 1.0 * loss_c
        loss_s = 3.0 * loss_s
        loss = loss_c + loss_s + l_identity1 * 50 + l_identity2 * 1
        avg_loss += loss.item()

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if (i + 1) % SAVE_ITER == 0:
            print(f"    LOSS: {avg_loss / SAVE_ITER}")
            avg_loss = 0

            state_dict = decoder.state_dict()

            for key in state_dict.keys():
                state_dict[key] = state_dict[key].to(torch.device('cpu'))
            torch.save(state_dict, STATE_DICTS_DIR / f'decoder_iter_{i + 1}.pth')

            state_dict = network.transform.state_dict()
            for key in state_dict.keys():
                state_dict[key] = state_dict[key].to(torch.device('cpu'))
            torch.save(state_dict, STATE_DICTS_DIR / f'transformer_iter_{i + 1}.pth')

            state_dict = optimizer.state_dict()
            torch.save(state_dict, STATE_DICTS_DIR / f'optimizer_iter_{i + 1}.pth')

