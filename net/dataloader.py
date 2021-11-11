import numpy as np
import os

from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
from torch.utils import data

from config import BATCH_SIZE, NUM_WORKERS, TRAIN_CONTENT_DIR, TRAIN_STYLE_DIR, TRAIN_RESIZE


class FlatFolderDataset(Dataset):
    def __init__(self, folder):
        super().__init__()
        self.root = folder
        self.paths = os.listdir(folder)
        self.transform = transforms.Compose([
            transforms.Resize((TRAIN_RESIZE, TRAIN_RESIZE)),
            transforms.RandomCrop(TRAIN_RESIZE / 2),
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
    content_dataset = FlatFolderDataset(TRAIN_CONTENT_DIR)
    style_dataset = FlatFolderDataset(TRAIN_STYLE_DIR)

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
