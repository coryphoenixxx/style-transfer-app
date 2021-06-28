import torch
from network.dataloader import init_loaders
from network.network import create_network
import torch.backends.cudnn as cudnn
from PIL import Image, ImageFile
from tqdm import tqdm


cudnn.benchmark = True
Image.MAX_IMAGE_PIXELS = None  # Disable DecompressionBombError
ImageFile.LOAD_TRUNCATED_IMAGES = True  # Disable OSError: image file is truncated


def adjust_learning_rate(optimizer, iteration_count):
    lr = 1e-4 / (1.0 + 5e-5 * iteration_count)
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr


if __name__ == '__main__':

    start_iter = 820000
    avg_loss = 0

    device = torch.device('cuda:0')
    print(torch.cuda.is_available())

    content_iter, style_iter = init_loaders()
    network, decoder, vgg = create_network()

    decoder.load_state_dict(torch.load(f'./state_dicts/decoder_iter_{start_iter}.pth'))
    network.transform.load_state_dict(torch.load(f'./state_dicts/transformer_iter_{start_iter}.pth'))

    network.cuda()

    optimizer = torch.optim.Adam([
        {'params': network.decoder.parameters()},
        {'params': network.transform.parameters()}], lr=1e-4)
    optimizer.load_state_dict(torch.load(f'./state_dicts/optimizer_iter_{start_iter}.pth'))

    network.train()

    print(device)

    for i in tqdm(range(start_iter, 1000001)):
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

        if (i + 1) % 5000 == 0:
            print(f"    LOSS: {avg_loss / 5000}")
            avg_loss = 0

            state_dict = decoder.state_dict()

            for key in state_dict.keys():
                state_dict[key] = state_dict[key].to(torch.device('cpu'))
            torch.save(state_dict, f'./state_dicts/decoder_iter_{i + 1}.pth')

            state_dict = network.transform.state_dict()
            for key in state_dict.keys():
                state_dict[key] = state_dict[key].to(torch.device('cpu'))
            torch.save(state_dict, f'./state_dicts/transformer_iter_{i + 1}.pth')

            state_dict = optimizer.state_dict()
            torch.save(state_dict, f'./state_dicts/optimizer_iter_{i + 1}.pth')

