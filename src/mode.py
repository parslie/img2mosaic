import cv2
import json
import numpy

from argparse import Namespace
from glob import glob
from os.path import exists as path_exists


def mosaic(args: Namespace):
    pass


def palette(args: Namespace):
    paths = []
    for dir in args.dirs:
        for ext in ('jpg', 'jpeg', 'jpe', 'png', 'webp'):
            # TODO: skip paths already added to palette here
            new_paths = glob(f'{dir}/*.{ext}')
            paths.extend(new_paths)

    palette = {}
    if path_exists(f'{args.config}/palette.json'):
        with open(f'{args.config}/palette.json', 'r') as file:
            palette = json.loads(file.read())

    for path in paths:
        img = cv2.imread(path)

        height, width, _ = img.shape
        half_height = round(height / 2)
        half_width = round(width / 2)
        
        top_left = img[0:half_height, 0:half_width]
        top_right = img[0:half_height, half_width:width]
        bottom_left = img[half_height:height, 0:half_width]
        bottom_right = img[half_height:height, half_width:width]

        top_left_avg = top_left.mean(axis=(0, 1)).astype(numpy.uint8)
        top_right_avg = top_right.mean(axis=(0, 1)).astype(numpy.uint8)
        bottom_left_avg = bottom_left.mean(axis=(0, 1)).astype(numpy.uint8)
        bottom_right_avg = bottom_right.mean(axis=(0, 1)).astype(numpy.uint8)

        img_key = f'{top_left_avg[0]} {top_left_avg[1]} {top_left_avg[2]} ' + \
              f'{top_right_avg[0]} {top_right_avg[1]} {top_right_avg[2]} ' + \
              f'{bottom_left_avg[0]} {bottom_left_avg[1]} {bottom_left_avg[2]} ' + \
              f'{bottom_right_avg[0]} {bottom_right_avg[1]} {bottom_right_avg[2]}'

        img_list = palette.get(img_key, [])
        if path not in img_list:
            img_list.append(path)
        palette[img_key] = img_list
    
    with open(f'{args.config}/palette.json', 'w') as file:
        file.write(json.dumps(palette, indent=2))