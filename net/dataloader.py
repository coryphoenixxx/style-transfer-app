from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
from pathlib import Path
from torch.utils import data
import numpy as np
import os


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


def InfiniteSampler(n):
    # i = 0
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
        return iter(InfiniteSampler(self.num_samples))

    def __len__(self):
        return 2 ** 31


def init_loaders():
    content_folder = Path(r'C:\Users\coryphoenixxx\Downloads\content')
    style_folder = Path(r'C:\Users\coryphoenixxx\Downloads\style')

    content_dataset = FlatFolderDataset(content_folder)
    style_dataset = FlatFolderDataset(style_folder)

    batch_size = 18
    num_workers = 2
    content_iter = iter(DataLoader(dataset=content_dataset, batch_size=batch_size,
                                   num_workers=num_workers, pin_memory=True,
                                   sampler=InfiniteSamplerWrapper(content_dataset)))
    style_iter = iter(DataLoader(dataset=style_dataset, batch_size=batch_size,
                                 num_workers=num_workers, pin_memory=True,
                                 sampler=InfiniteSamplerWrapper(style_dataset)))

    return content_iter, style_iter
