import numpy as np
import os

from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
from pathlib import Path
from torch.utils import data

from config import BATCH_SIZE, NUM_WORKERS


class FlatFolderDataset(Dataset):
    def __init__(self, folder):
        super().__init__()
        self.root = folder
        self.paths = os.listdir(folder)
        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.RandomCrop(128),
            transforms.ToTensor()
        ])

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, index):
        img_path = os.path.join(self.root, self.paths[index])
        img = Image.open(img_path).convert('RGB')
        img = self.transform(img)
        return img


def inf_sampler(n):
    i = n - 1
    order = np.random.permutation(n)
    while True:
        yield order[i]
        i += 1
        if i >= n:
            np.random.seed()
            order = np.random.permutation(n)
            i = 0


class InfiniteSamplerWrapper(data.sampler.Sampler):
    def __init__(self, data_source):
        self.num_samples = len(data_source)

    def __iter__(self):
        return iter(inf_sampler(self.num_samples))

    def __len__(self):
        return 2 ** 31


def init_loaders():
    content_folder = Path('train_images/content')
    style_folder = Path('train_images/style')

    content_dataset = FlatFolderDataset(content_folder)
    style_dataset = FlatFolderDataset(style_folder)

    content_iter = iter(DataLoader(dataset=content_dataset,
                                   batch_size=BATCH_SIZE,
                                   num_workers=NUM_WORKERS,
                                   pin_memory=True,
                                   sampler=InfiniteSamplerWrapper(content_dataset)))
    style_iter = iter(DataLoader(dataset=style_dataset,
                                 batch_size=BATCH_SIZE,
                                 num_workers=NUM_WORKERS,
                                 pin_memory=True,
                                 sampler=InfiniteSamplerWrapper(style_dataset)))

    return content_iter, style_iter
