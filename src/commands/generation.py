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
from .base import Command


class Statistics:
    def __init__(self):
        self.completion_time = 0
        self.cached_entries = 0
        # TODO: add time per pixel array
    
    def __repr__(self) -> str:
        return f"Completion time: {self.completion_time:.1f} sec\n" + \
            f"Cached entries: {self.cached_entries}"


class Generate(Command):
    def __init__(self, args: Arguments):
        self.__unpack_args(args)
        self.__load_source()
        self.__load_destination()

        profile = f"{self.color_reduction}"
        self.cache = Cache(profile)
        self.palette = Palette(profile)

        self.progress = Progress((self.source_height - 1) * (self.source_width - 1))
        self.stats = Statistics()

        self.executor = ThreadPoolExecutor(max_workers=6) # TODO: optimize max_workers
        self.futures = list[Future]()
        self.cache_lock = Lock()
        self.stats_lock = Lock()
    
    def __unpack_args(self, args: Arguments):
        self.color_reduction = args.color_reduction
        self.source_path = args.source
        self.destination_path = args.destination
        self.source_size = args.source_size
        self.pixel_size = args.pixel_size

    def __load_source(self):
        source = cv2.imread(self.source_path)
        height, width, _ = source.shape

        # Decides new size of image
        scale_factor = self.source_size / max(height, width)
        new_height, new_width = height, width
        if scale_factor < 1:
            new_height = round(height * scale_factor)
            new_width = round(width * scale_factor)

        # Ensures divisible by density
        if diff := new_height % 2:
            new_height += 2 - diff
        if diff := new_width % 2:
            new_width += 2 - diff

        # Apply new size of image
        if new_height != height or new_width != width:
            source = cv2.resize(source, (new_width, new_height))

        self.source = source
        self.source_height, self.source_width, _ = self.source.shape

    def __load_destination(self):
        self.destination_height = (self.source_height - 1) * self.pixel_size
        self.destination_width = (self.source_width - 1) * self.pixel_size
        destination_shape = (self.destination_height, self.destination_width, 3)
        self.destination = numpy.zeros(shape=destination_shape, dtype=numpy.uint8)

    def run(self):
        print(self.progress, end="\r")
        start_time = perf_counter()
        
        for y in range(0, self.source_height - 1):
            for x in range(0, self.source_width - 1):
                future = self.executor.submit(self.__fill_pixel, x, y)
                self.futures.append(future)
        for future in as_completed(self.futures):
            end_time = perf_counter()
            self.stats.completion_time += end_time - start_time
            start_time = end_time
            self.progress.increment()
            print(self.progress, end="\r")

        print(self.progress)
        print(self.stats)

        self.cache.save()
        cv2.imwrite(self.destination_path, self.destination)

    def __fill_pixel(self, x: int, y: int):
        source_colors = [
            clamp_color(self.source[y, x], self.color_reduction),
            clamp_color(self.source[y, x + 1], self.color_reduction),
            clamp_color(self.source[y + 1, x], self.color_reduction),
            clamp_color(self.source[y + 1, x + 1], self.color_reduction),
        ]

        image_key = colors_to_key(source_colors)
        image_list = self.palette.get(image_key, [])

        if not image_list:
            cached_key = self.cache.get(image_key, None)

            if cached_key:
                # Cached key should be valid, unless you've reset the palette w/o resetting the cache
                image_list = self.palette.get(cached_key, [])
            else:
                # TODO: do not use palette's data dict directly here
                closest_key = colors_to_closest_key(self.palette.data, source_colors)
                # Closest key should be valid, since it's found via the palette
                image_list = self.palette.get(closest_key, [])
                with self.cache_lock:
                    self.cache.set(image_key, closest_key)
                with self.stats_lock:
                    self.stats.cached_entries += 1
        
        image = cv2.imread(random.choice(image_list))
        image = cv2.resize(image, (self.pixel_size, self.pixel_size))

        # Apply palette image to dest
        dest_y = y * self.pixel_size
        dest_x = x * self.pixel_size
        dest_y_end = dest_y + self.pixel_size
        dest_x_end = dest_x + self.pixel_size
        self.destination[dest_y:dest_y_end, dest_x:dest_x_end] = image[0:self.pixel_size, 0:self.pixel_size]

    def cancel(self):
        print(f"\r{self.progress}")
        print(self.stats)
        self.executor.shutdown(wait=True, cancel_futures=True)
        self.cache.save()
