#!/usr/bin/python3

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "7"

import gradio as gr
import torch
import numpy as np
from PIL import Image
import torchvision.transforms as transforms
from torchvision.utils import save_image
from torch.autograd import Variable
import sys
import io

from model import Generator, GlobalGenerator2, InceptionV3
from utils import channel2width


class Opt:
    def __init__(self):
        self.name = 'anime_style'
        self.checkpoints_dir = 'checkpoints'
        self.results_dir = 'results'
        self.geom_name = 'feats2Geom'
        self.batchSize = 1
        self.dataroot = ''
        self.depthroot = ''
        self.input_nc = 3
        self.output_nc = 1
        self.geom_nc = 3
        self.every_feat = 1
        self.num_classes = 55
        self.midas = 0
        self.ngf = 64
        self.n_blocks = 3
        self.size = 1024  
        self.cuda = True
        self.n_cpu = 8
        self.which_epoch = 'latest'
        self.aspect_ratio = 1.0
        self.mode = 'test'
        self.load_size = 1024
        self.crop_size = 1024
        self.max_dataset_size = float("inf")
        self.preprocess = 'resize_and_crop'
        self.no_flip = True
        self.norm = 'instance'
        self.predict_depth = 0
        self.save_input = 0
        self.reconstruct = 0
        self.how_many = 100
        self.preserve_ratio = True  

opt = Opt()


def load_models():
    with torch.no_grad():
        
        net_G = Generator(opt.input_nc, opt.output_nc, opt.n_blocks)
        if torch.cuda.is_available() and opt.cuda:
            net_G.cuda()
        
        
        net_G.load_state_dict(torch.load(os.path.join(opt.checkpoints_dir, opt.name, f'netG_A_{opt.which_epoch}.pth')))
        net_G.eval()

        
        net_GB = None
        if opt.reconstruct == 1:
            net_GB = Generator(opt.output_nc, opt.input_nc, opt.n_blocks)
            if torch.cuda.is_available() and opt.cuda:
                net_GB.cuda()
            net_GB.load_state_dict(torch.load(os.path.join(opt.checkpoints_dir, opt.name, f'netG_B_{opt.which_epoch}.pth')))
            net_GB.eval()
        
        netGeom = None
        net_recog = None
        if opt.predict_depth == 1:
            usename = opt.name
            if (len(opt.geom_name) > 0) and (os.path.exists(os.path.join(opt.checkpoints_dir, opt.geom_name))):
                usename = opt.geom_name
            myname = os.path.join(opt.checkpoints_dir, usename, f'netGeom_{opt.which_epoch}.pth')
            netGeom = GlobalGenerator2(768, opt.geom_nc, n_downsampling=1, n_UPsampling=3)
            netGeom.load_state_dict(torch.load(myname))
            if torch.cuda.is_available() and opt.cuda:
                netGeom.cuda()
            netGeom.eval()

            
            net_recog = InceptionV3(opt.num_classes, False, use_aux=True, pretrain=True, freeze=True, every_feat=opt.every_feat==1)
            if torch.cuda.is_available() and opt.cuda:
                net_recog.cuda()
            net_recog.eval()
        
        return net_G, net_GB, netGeom, net_recog


def process_image(input_image, net_G, net_GB, netGeom, net_recog):
    if input_image is None:
        return None
    
    
    original_width, original_height = input_image.size
    
    
    transform = transforms.Compose([
        transforms.Resize((opt.size, opt.size), Image.BICUBIC),
        transforms.ToTensor()
    ])
    
    input_tensor = transform(input_image).unsqueeze(0)
    if torch.cuda.is_available() and opt.cuda:
        input_tensor = input_tensor.cuda()
    
    
    with torch.no_grad():
        output_tensor = net_G(input_tensor)
    
    
    output_image = tensor_to_pil(output_tensor)
    if opt.preserve_ratio:
        output_image = output_image.resize((original_width, original_height), Image.BICUBIC)
    
    return output_image


def tensor_to_pil(tensor):
    if tensor.ndim == 4:
        tensor = tensor[0]
    
    if tensor.size(0) == 1:  
        image_np = tensor.cpu().float().numpy().squeeze(0) * 255.0
        image_np = image_np.astype(np.uint8)
        return Image.fromarray(image_np, mode='L')
    else:  
        image_np = tensor.cpu().float().numpy().transpose(1, 2, 0) * 255.0
        image_np = image_np.astype(np.uint8)
        return Image.fromarray(image_np)


models = None


def anime_style_transfer(input_image):
    global models
    
    if input_image is None:
        return None
    
    
    if models is None:
        models = load_models()
    
    
    output = process_image(input_image, *models)
    
    return output


demo = gr.Interface(
    fn=anime_style_transfer,
    inputs=gr.Image(type="pil", label="Input Image"),
    outputs=gr.Image(type="pil", label="Anime Style Output"),
    title="Anime Style Transfer",
    description="Upload an image to convert it to anime style. The output will maintain the original image dimensions.",
    examples=[
        ["example1.jpg"],
        ["example2.jpg"]
    ] if os.path.exists("example1.jpg") else None
)


if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0", server_port=8084)