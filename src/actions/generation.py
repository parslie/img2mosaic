import cv2
import numpy
import random
from concurrent.futures import Future, ThreadPoolExecutor
from threading import Lock
from time import perf_counter

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


def fill_pixel(x: int, y: int, 
               src_img: cv2.Mat, dest_img: cv2.Mat, 
               pixel_count: int,
               palette: dict, cache: dict, 
               args: Arguments):
    global pixels_replaced

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
    dest_y_end = dest_y + args.pixel_size
    dest_x_end = dest_x + args.pixel_size
    dest_img[dest_y:dest_y_end, dest_x:dest_x_end] = img[0:args.pixel_size, 0:args.pixel_size]

    with pixels_replaced_lock:
        pixels_replaced += 1
        print(f'{pixels_replaced} / {pixel_count}', end='\r')


def generate_mosaic(args: Arguments):
    src_img = cv2.imread(args.src)
    src_img = scale_src_img(args, src_img)
    src_height, src_width, _ = src_img.shape

    dest_height = src_height // args.density * args.pixel_size
    dest_width = src_width // args.density * args.pixel_size
    dest_img = numpy.zeros(shape=(dest_height, dest_width, 3), dtype=numpy.uint8)

    palette = load_palette(args)
    cache = load_cache(args)

    pixel_count = int(src_height / args.density * src_width / args.density)
    print(f'0 / {pixel_count}', end='\r')
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = list[Future]()
        for y in range(0, src_height, args.density):
            for x in range(0, src_width, args.density):
                future = executor.submit(fill_pixel, x, y, src_img, dest_img, pixel_count, palette, cache, args)
                futures.append(future)
        for future in futures:
            future.result()
    print()

    save_cache(args, cache)
    cv2.imwrite(args.dest, dest_img)
