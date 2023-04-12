import cv2
import numpy
import random
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from arguments import Arguments
from data.cache import load_cache, save_cache
from data.palette import load_palette
from utils import colors_to_key, colors_to_closest_key

cache_lock = Lock()
pixels_replaced_lock = Lock()
pixels_replaced = 0


def scale_src_img(args: Arguments, src_img: numpy.ndarray) -> numpy.ndarray:
    src_height, src_width, _ = src_img.shape
    src_size = max(src_height, src_width)

    # Decides new size of src
    new_src_height, new_src_width = src_height, src_width
    if args.src_size and args.src_size < src_size:
        scale = args.src_size / src_size
        new_src_height = round(src_height * scale)
        new_src_width = round(src_width * scale)
    
    # Ensure divisible by args.density
    new_src_height -= new_src_height % args.density
    new_src_width -= new_src_width % args.density

    # Apply new size of src
    if new_src_height != src_height or new_src_width != src_width:
        src_img = cv2.resize(src_img, (new_src_width, new_src_height))
    
    return src_img


def fill_section(src_img: numpy.ndarray, dest_img: numpy.ndarray, src_width_range: range, src_height_range: range, pixel_count: int, palette: dict, cache: dict, args: Arguments):
    global pixels_replaced

    for y in src_height_range:
        for x in src_width_range:
            src_colors = []
            for y_offset in range(args.density):
                for x_offset in range(args.density):
                    src_color = src_img[y+y_offset, x+x_offset]
                    src_colors.append(src_color)
            
            img_key = colors_to_key(src_colors)
            img_list = palette.get(img_key, [])

            if not img_list:
                cached_key = cache.get(img_key, None)

                if cached_key:
                    # Cached key should be valid, unless you've reset the palette w/o resetting the cache
                    img_list = palette[cached_key]
                else:
                    closest_key = colors_to_closest_key(palette, src_colors)
                    # Closest key should be valid, since it's found via the palette
                    img_list = palette[closest_key]
                    with cache_lock:
                        cache[img_key] = closest_key

            img = cv2.imread(random.choice(img_list))
            img = cv2.resize(img, (args.pixel_size, args.pixel_size))

            # Apply palette image to dest
            dest_y = int(y / args.density) * args.pixel_size
            dest_x = int(x / args.density) * args.pixel_size
            for dest_y_offset in range(args.pixel_size):
                for dest_x_offset in range(args.pixel_size):
                    dest_img[dest_y+dest_y_offset, dest_x+dest_x_offset] = img[dest_y_offset, dest_x_offset]

            with pixels_replaced_lock:
                pixels_replaced += 1
                print(f'{pixels_replaced} / {pixel_count}', end='\r')


def generate_mosaic(args: Arguments):
    src_img = cv2.imread(args.src)
    src_img = scale_src_img(args, src_img)
    src_height, src_width, _ = src_img.shape

    dest_height = int(src_height / args.density) * args.pixel_size
    dest_width = int(src_width / args.density) * args.pixel_size
    dest_img = numpy.zeros(shape=(dest_height, dest_width, 3), dtype=numpy.uint8)

    palette = load_palette(args)
    cache = load_cache(args)

    pixel_count = int(src_height / args.density * src_width / args.density)
    print(f'0 / {pixel_count}', end='\r')
    with ThreadPoolExecutor(max_workers=4) as executor:
        half_width = int(src_width / 2)
        half_width -= half_width % args.density 
        left_range = range(0, half_width, args.density)
        right_range = range(half_width, src_width, args.density)

        half_height = int(src_height / 2)
        half_height -= half_height % args.density 
        bottom_range = range(0, half_height, args.density)
        top_range = range(half_height, src_height, args.density)

        a = executor.submit(fill_section, src_img, dest_img, left_range, bottom_range, pixel_count, palette, cache, args)
        b = executor.submit(fill_section, src_img, dest_img, right_range, bottom_range, pixel_count, palette, cache, args)
        c = executor.submit(fill_section, src_img, dest_img, left_range, top_range, pixel_count, palette, cache, args)
        d = executor.submit(fill_section, src_img, dest_img, right_range, top_range, pixel_count, palette, cache, args)
        a.result()
        b.result()
        c.result()
        d.result()
    print()

    save_cache(args, cache)
    cv2.imwrite(args.dest, dest_img)