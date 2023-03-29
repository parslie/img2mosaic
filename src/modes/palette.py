import cv2
import numpy
from argparse import Namespace
from concurrent.futures import ThreadPoolExecutor
from glob import glob
from threading import Lock

from data.palette import load_palette, save_palette, get_palette_paths
from utils import colors_to_key

IMG_EXTS = ('jpg', 'jpeg', 'jpe', 'png', 'webp')

current_path = 0


def get_img_color(img: numpy.ndarray) -> numpy.ndarray:
    average_color = img.mean(axis=(0, 1)).astype(numpy.uint8)
    return average_color


def run(args: Namespace):
    palette = load_palette(args)

    paths = set()
    for dir in args.dirs:
        for ext in IMG_EXTS:
            paths.update(glob(f'{dir}/*.{ext}'))
    paths.difference_update(get_palette_paths(palette))

    palette_lock = Lock()
    current_path_lock = Lock()

    def add_path_to_palette(path_idx, path):
        global current_path

        img = cv2.imread(path)
        height, width, _ = img.shape

        colors = []
        for y in range(args.pixels_per_img):
            start_y = round(y * height / args.pixels_per_img)
            end_y = round((y + 1) * height / args.pixels_per_img)

            for x in range(args.pixels_per_img):
                start_x = round(x * width / args.pixels_per_img)
                end_x = round((x + 1) * width / args.pixels_per_img)

                img_section = img[start_y:end_y, start_x:end_x]
                colors.append(get_img_color(img_section))

        img_key = colors_to_key(colors)
        img_list = palette.get(img_key, [])
        if path not in img_list:
            img_list.append(path)
        with palette_lock:
            palette[img_key] = img_list

        # TODO: save palette after each 100 paths?
        with current_path_lock:
            current_path += 1
            print(f'{current_path} / {len(paths)}', end='\r')

    print(f'0 / {len(paths)}', end='\r')
    with ThreadPoolExecutor(max_workers=8) as executor:
        thread_list = []
        for path_idx, path in enumerate(paths):
            thread_list.append(executor.submit(add_path_to_palette, path_idx, path))
        for thread in thread_list:
            thread.result()
    print()

    save_palette(args, palette)
