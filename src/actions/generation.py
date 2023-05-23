"""
TODO: rougher color precision could speed up caching, analysis, and generation
"""
import cv2
import math
import numpy
import random
import shutil
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from threading import Lock
from time import perf_counter

from arguments import Arguments
from data.palette import load_palette
from data.cache import load_cache, save_cache
from utils import colors_to_key, colors_to_closest_key

MAX_FUTURES_IN_QUEUE = 64

cache_lock = Lock()
stats_lock = Lock()


class Progress:
    def __init__(self, total: int):
        self.current = 0
        self.total = total
        self.speed = 0

    @property
    def percent(self) -> float:
        return self.current / self.total

    def eta_str(self) -> str:
        remaining = self.total - self.current
        if self.speed == 0:
            return f'[ETA: {float("inf")} sec]'
        
        eta = remaining / self.speed
        if eta / 60 >= 1:
            return f'[ETA: {remaining / self.speed / 60:.1f} min]'

        return f'[ETA: {remaining / self.speed:.1f} sec]'
        
    def percent_str(self) -> str:
        return f'[{self.percent * 100:.0f}%]'
    
    def bar_str(self, width: int) -> str:
        inner_width = min(width - 2, 34)
        inner_filled_width = math.floor(inner_width * self.percent)
        inner_empty_width = inner_width - inner_filled_width
        inner_filled = '=' * inner_filled_width
        inner_empty = ' ' * inner_empty_width
        return f'[{inner_filled}{inner_empty}]'

    def __repr__(self) -> str:
        console_width = shutil.get_terminal_size((12, 24)).columns
        
        eta = self.eta_str()
        percent = self.percent_str()
        bar = self.bar_str(console_width - 2 - len(percent) - len(eta))
        padding = ' ' * (console_width - 2 - len(eta) - len(percent) - len(bar))

        return f'{bar} {percent} {eta}{padding}'


class Statistics:
    def __init__(self):
        self.completion_time = 0
        self.cached_entries = 0
        # TODO: add time per pixel array
    
    def __repr__(self) -> str:
        return f'Completion time: {self.completion_time:.1f} sec\n' + \
            f'Cached entries: {self.cached_entries}'


def load_src_img(args: Arguments) -> numpy.ndarray:
    img = cv2.imread(args.src)
    height, width, _ = img.shape

    # Decides new size of image
    scale_factor = args.src_size / max(width, height)
    new_height, new_width = height, width
    if scale_factor < 1:
        new_height = round(height * scale_factor)
        new_width = round(width * scale_factor)
    
    # Ensure divisible by {args.density}
    if diff := new_height % args.density:
        new_height += args.density - diff
    if diff := new_width % args.density:
        new_width += args.density - diff

    # Apply new size of image
    if new_height != height or new_width != width:
        img = cv2.resize(img, (new_width, new_height))

    return img


def fill_pixel(x: int, y: int, 
               src_img: cv2.Mat, dest_img: cv2.Mat,
               stats: Statistics, 
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
            with stats_lock:
                stats.cached_entries += 1

    img = cv2.imread(random.choice(img_list))
    img = cv2.resize(img, (args.pixel_size, args.pixel_size))

    # Apply palette image to dest
    dest_y = int(y / args.density) * args.pixel_size
    dest_x = int(x / args.density) * args.pixel_size
    dest_y_end = dest_y + args.pixel_size
    dest_x_end = dest_x + args.pixel_size
    dest_img[dest_y:dest_y_end, dest_x:dest_x_end] = img[0:args.pixel_size, 0:args.pixel_size]


def generate_mosaic(args: Arguments):
    src_img = load_src_img(args)
    src_height, src_width, _ = src_img.shape
    
    dest_height = src_height // args.density * args.pixel_size
    dest_width = src_width // args.density * args.pixel_size
    dest_img = numpy.zeros(shape=(dest_height, dest_width, 3), dtype=numpy.uint8)

    palette = load_palette(args)
    cache = load_cache(args)

    progress = Progress(src_height // args.density * src_width // args.density)
    stats = Statistics()

    # TODO: implement KeyboardInterrupt except
    print('\r', progress, sep='', end='\r')
    with ThreadPoolExecutor(max_workers=6) as executor:
        start_time = perf_counter()

        futures = list[Future]()
        for y in range(0, src_height, args.density):
            for x in range(0, src_width, args.density):
                future = executor.submit(fill_pixel, x, y, src_img, dest_img, stats, palette, cache, args)
                futures.append(future)

        for future in as_completed(futures):
            stats.completion_time += perf_counter() - start_time
            start_time = perf_counter()
            progress.current += 1
            progress.speed = progress.current / stats.completion_time
            print('\r', progress, sep='', end='\r')
    print('\n\n', stats, sep='')

    save_cache(args, cache)
    cv2.imwrite(args.dest, dest_img)