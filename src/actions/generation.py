import math
import random
import shutil
import cv2
import numpy
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from threading import Lock
from time import perf_counter

from arguments.parsers import Arguments
from data.cache import Cache
from data.palette import Palette
from utils.colors import colors_to_key, colors_to_closest_key, clamp_color
from utils.progress import Progress
from .base import Action

# TODO: rougher color precision could speed up caching, analysis, and generation


class Statistics:
    def __init__(self):
        self.completion_time = 0
        self.cached_entries = 0
        # TODO: add time per pixel array
    
    def __repr__(self) -> str:
        return f"Completion time: {self.completion_time:.1f} sec\n" + \
            f"Cached entries: {self.cached_entries}"


class Generate(Action):
    def __init__(self, args: Arguments):
        self.__unpack_args(args)
        self.__load_src()
        self.__load_dst()

        profile = f"{self.density} {self.complexity}"
        self.cache = Cache(profile)
        self.palette = Palette(profile)

        self.progress = Progress(self.src_height // self.density * self.src_width // self.density)
        self.stats = Statistics()

        self.executor = ThreadPoolExecutor(max_workers=6)
        self.futures = list[Future]()
        self.cache_lock = Lock()
        self.stats_lock = Lock()

    def __unpack_args(self, args: Arguments):
        self.density = args.density
        self.complexity = args.complexity
        self.src_path = args.src
        self.dst_path = args.dst
        self.src_max_size = args.src_size
        self.pixel_size = args.pixel_size

    def __load_src(self):
        src = cv2.imread(self.src_path)
        height, width, _ = src.shape

        # Decides new size of image
        scale_factor = self.src_max_size / max(height, width)
        new_height, new_width = height, width
        if scale_factor < 1:
            new_height = round(height * scale_factor)
            new_width = round(width * scale_factor)

        # Ensures divisible by density
        if diff := new_height % self.density:
            new_height += self.density - diff
        if diff := new_width % self.density:
            new_width += self.density - diff

        # Apply new size of image
        if new_height != height or new_width != width:
            src = cv2.resize(src, (new_width, new_height))

        self.src = src
        self.src_height, self.src_width, _ = self.src.shape

    def __load_dst(self):
        self.dst_height = self.src_height // self.density * self.pixel_size
        self.dst_width = self.src_width // self.density * self.pixel_size
        dst_shape = (self.dst_height, self.dst_width, 3)
        self.dst = numpy.zeros(shape=dst_shape, dtype=numpy.uint8)

    def run(self):
        print(self.progress, end="\r")
        start_time = perf_counter()

        for y in range(0, self.src_height, self.density):
            for x in range(0, self.src_width, self.density):
                future = self.executor.submit(self.__fill_pixel, x, y)
                self.futures.append(future)
        for future in as_completed(self.futures):
            end_time = perf_counter()
            self.stats.completion_time += end_time - start_time
            start_time = end_time
            self.progress.current += 1
            self.progress.speed = self.progress.current / self.stats.completion_time
            print(self.progress, end="\r")

        print(self.progress)
        print(self.stats)

        self.cache.save()
        cv2.imwrite(self.dst_path, self.dst)
    
    def __fill_pixel(self, x: int, y: int):
        src_colors = []
        for y_offset in range(self.density):
            for x_offset in range(self.density):
                src_color = self.src[y+y_offset, x+x_offset]
                src_colors.append(clamp_color(src_color, self.complexity))

        img_key = colors_to_key(src_colors)
        img_list = self.palette.get(img_key, [])

        if not img_list:
            cached_key = self.cache.get(img_key, None)

            if cached_key:
                # Cached key should be valid, unless you've reset the palette w/o resetting the cache
                img_list = self.palette.get(cached_key, [])
            else:
                # TODO: do not use palette's data dict directly here
                closest_key = colors_to_closest_key(self.palette.data, src_colors)
                # Closest key should be valid, since it's found via the palette
                img_list = self.palette.get(closest_key, [])
                with self.cache_lock:
                    self.cache.set(img_key, closest_key)
                with self.stats_lock:
                    self.stats.cached_entries += 1

        img = cv2.imread(random.choice(img_list))
        img = cv2.resize(img, (self.pixel_size, self.pixel_size))

        # Apply palette image to dest
        dest_y = int(y / self.density) * self.pixel_size
        dest_x = int(x / self.density) * self.pixel_size
        dest_y_end = dest_y + self.pixel_size
        dest_x_end = dest_x + self.pixel_size
        self.dst[dest_y:dest_y_end, dest_x:dest_x_end] = img[0:self.pixel_size, 0:self.pixel_size]

    def cancel(self):
        print(f"\r{self.progress}")
        print(self.stats)
        self.executor.shutdown(wait=True, cancel_futures=True)
        self.cache.save()
