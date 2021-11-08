from .network import decoder, vgg, Transform
import torch
import torch.nn as nn
from config import EVAL_ITER

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

transform = Transform(in_planes=512)

decoder.eval()
transform.eval()
vgg.eval()

decoder.load_state_dict(torch.load(f'net/state_dicts/decoder_iter_{EVAL_ITER}.pth'))
transform.load_state_dict(torch.load(f'net/state_dicts/transformer_iter_{EVAL_ITER}.pth'))
vgg.load_state_dict(torch.load('net/state_dicts/vgg_normalised.pth'))

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
