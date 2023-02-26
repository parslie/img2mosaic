import cv2
import json
import numpy
import random

from argparse import Namespace
from glob import glob
from os.path import exists as path_exists


def load_palette(args: Namespace) -> dict:
    palette = {}
    if path_exists(f'{args.config}/palette.json'):
        with open(f'{args.config}/palette.json', 'r') as file:
            palette = json.loads(file.read())
    return palette


def save_palette(args: Namespace, palette: dict):
    with open(f'{args.config}/palette.json', 'w') as file:
        file.write(json.dumps(palette, indent=2))


def load_cache(args: Namespace) -> dict:
    cache = {}
    if path_exists(f'{args.config}/cache.json'):
        with open(f'{args.config}/cache.json', 'r') as file:
            cache = json.loads(file.read())
    return cache


def save_cache(args: Namespace, cache: dict):
    with open(f'{args.config}/cache.json', 'w') as file:
        file.write(json.dumps(cache, indent=2))


def colors_to_key(top_left: numpy.ndarray, top_right: numpy.ndarray, bottom_left: numpy.ndarray, bottom_right: numpy.ndarray) -> str:
    return f'{top_left[0]} {top_left[1]} {top_left[2]} ' + \
            f'{top_right[0]} {top_right[1]} {top_right[2]} ' + \
            f'{bottom_left[0]} {bottom_left[1]} {bottom_left[2]} ' + \
            f'{bottom_right[0]} {bottom_right[1]} {bottom_right[2]}'


def key_to_colors(key: str) -> tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray]:
    key_split = key.split(' ')
    top_left = numpy.array([int(x) for x in key_split[0:3]], dtype=numpy.uint8)
    top_right = numpy.array([int(x) for x in key_split[3:6]], dtype=numpy.uint8)
    bottom_left = numpy.array([int(x) for x in key_split[6:9]], dtype=numpy.uint8)
    bottom_right = numpy.array([int(x) for x in key_split[9:12]], dtype=numpy.uint8)
    return top_left, top_right, bottom_left, bottom_right


def color_sqr_dist(a: numpy.ndarray, b: numpy.ndarray) -> float:
    diff_b = int(a[0]) - int(b[0])
    diff_g = int(a[1]) - int(b[1])
    diff_r = int(a[2]) - int(b[2])
    return diff_b ** 2 + diff_g ** 2 + diff_r ** 2


def get_closest_key(palette: dict, top_left: numpy.ndarray, top_right: numpy.ndarray, bottom_left: numpy.ndarray, bottom_right: numpy.ndarray) -> str:
    closest_sqr_dist = float('inf')
    closest_key = None
    
    for close_key in palette.keys():
        close_top_left, close_top_right, close_bottom_left, close_bottom_right = key_to_colors(close_key)
        sqr_dist = color_sqr_dist(top_left, close_top_left) + color_sqr_dist(top_right, close_top_right) + color_sqr_dist(bottom_left, close_bottom_left) + color_sqr_dist(bottom_right, close_bottom_right)

        if sqr_dist < closest_sqr_dist:
            closest_sqr_dist = sqr_dist
            closest_key = close_key

    return closest_key

def get_existing_paths(palette: dict) -> set:
    existing_paths = set()
    for paths in palette.values():
        existing_paths.update(paths)
    return existing_paths

def mosaic(args: Namespace):
    src_img = cv2.imread(args.src)
    src_height, src_width, _ = src_img.shape
    src_size = max(src_height, src_width)

    # Decides new size of src
    new_src_height, new_src_width = src_height, src_width
    if args.src_size and args.src_size < src_size:
        scale = args.src_size / src_size
        new_src_height = round(src_height * scale)
        new_src_width = round(src_width * scale)
    new_src_height -= new_src_height % 2
    new_src_width -= new_src_width % 2

    # Apply new size of src
    if new_src_height != src_height or new_src_width != src_width:
        src_img = cv2.resize(src_img, (new_src_width, new_src_height))
        src_height, src_width = new_src_height, new_src_width

    dest_height = int(src_height / 2) * args.pixel_size
    dest_width = int(src_width / 2) * args.pixel_size
    dest_img = numpy.zeros(shape=(dest_height, dest_width, 3), dtype=numpy.uint8)

    palette = load_palette(args)
    cache = load_cache(args)

    current_pixel = 0
    pixel_count = int(src_height * src_width / 4)
    print(f'0 / {pixel_count}', end='\r')

    for y in range(0, src_height, 2):
        for x in range(0, src_width, 2):
            top_left = src_img[y, x]
            top_right = src_img[y, x+1]
            bottom_left = src_img[y+1, x]
            bottom_right = src_img[y+1, x+1]

            # Get palette image
            img_key = colors_to_key(top_left, top_right, bottom_left, bottom_right)
            img_list = palette.get(img_key, [])
            # TODO: pop from cache if exists

            if not img_list:
                cached_key = cache.get(img_key, None)

                if cached_key:
                    # Cached key should be valid, unless you've reset the palette w/o resetting the cache
                    img_list = palette[cached_key]
                else:
                    closest_key = get_closest_key(palette, top_left, top_right, bottom_left, bottom_right)
                    # Closest key should be valid, since it's found via the palette
                    img_list = palette[closest_key]
                    cache[img_key] = closest_key

            img = cv2.imread(random.choice(img_list))
            img = cv2.resize(img, (args.pixel_size, args.pixel_size))

            # Apply palette image to dest
            dest_y = int(y / 2) * args.pixel_size
            dest_x = int(x / 2) * args.pixel_size
            for dest_y_offset in range(args.pixel_size):
                for dest_x_offset in range(args.pixel_size):
                    dest_img[dest_y+dest_y_offset, dest_x+dest_x_offset] = img[dest_y_offset, dest_x_offset]

            current_pixel += 1
            print(f'{current_pixel} / {pixel_count}', end='\r')
        # TODO: save cache after each row?
    print()

    save_cache(args, cache)
    cv2.imwrite(args.dest, dest_img)


def palette(args: Namespace):
    palette = load_palette(args)
    existing_paths = get_existing_paths(palette)

    paths = set()
    for dir in args.dirs:
        for ext in ('jpg', 'jpeg', 'jpe', 'png', 'webp'):
            new_paths = glob(f'{dir}/*.{ext}')
            paths.update(new_paths)
    paths.difference_update(existing_paths)

    print(f'0 / {len(paths)}', end='\r')

    for path_idx, path in enumerate(paths):
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

        img_key = colors_to_key(top_left_avg, top_right_avg, bottom_left_avg, bottom_right_avg)

        img_list = palette.get(img_key, [])
        if path not in img_list:
            img_list.append(path)
        palette[img_key] = img_list

        # TODO: save palette after each 100 paths?
        print(f'{path_idx + 1} / {len(paths)}', end='\r')
    print()
    
    save_palette(args, palette)