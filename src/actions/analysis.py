import cv2
import numpy
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from glob import glob
from threading import Lock
from time import perf_counter

from arguments.parsers import Arguments
from arguments.types import VALID_IMAGE_EXTS # TODO: should be handled differently
from data.cache import Cache
from data.palette import Palette
from utils.colors import colors_to_key
from utils.progress import Progress
from .base import Action


class Statistics:
    def __init__(self):
        self.completion_time = 0
    
    def __repr__(self) -> str:
        return f"Completion time: {self.completion_time:.1f} sec"


class Analyze(Action):
    def __init__(self, args: Arguments):
        self.__unpack_args(args)

        profile = f"{self.density}"
        self.cache = Cache(profile)
        self.palette = Palette(profile)

        self.__load_paths()

        self.progress = Progress(self.path_count)
        self.stats = Statistics()

        self.executor = ThreadPoolExecutor(max_workers=6)
        self.futures = list[Future]()
        self.data_lock = Lock()

    def __unpack_args(self, args: Arguments):
        self.density = args.density
        self.dir = args.dir
        self.recursive = args.recursive

    def __load_paths(self) -> set:
        paths = set()

        for ext in VALID_IMAGE_EXTS:
            if self.recursive:
                new_paths = glob(f"{self.dir}/**/*.{ext}", recursive=True)
            else:
                new_paths = glob(f"{self.dir}/*.{ext}", recursive=False)
            paths.update(new_paths)
        paths.difference_update(self.palette.paths)

        self.paths = paths
        self.path_count = len(paths)

    def run(self):
        print(self.progress, end="\r")
        start_time = perf_counter()

        for path in self.paths:
            future = self.executor.submit(self.__analyze_img, path)
            self.futures.append(future)
        for future in as_completed(self.futures):
            end_time = perf_counter()
            self.stats.completion_time += end_time - start_time
            start_time = end_time
            self.progress.current += 1
            self.progress.speed = self.progress.current / self.stats.completion_time
            if self.progress.current % 1000 == 0:
                # Done in order to avoid unsaved work after crash
                with self.data_lock:
                    self.cache.save()
                    self.palette.save()
            print(self.progress, end="\r")

        print(self.progress)
        print(self.stats)

        self.cache.save()
        self.palette.save()

    def __get_img_colors(self, img: cv2.Mat) -> list[numpy.ndarray]:
        height, width, _ = img.shape

        colors = []
        for y in range(self.density):
            start_y = round(height / self.density * y)
            end_y = round(height / self.density * (y + 1))

            for x in range(self.density):
                start_x = round(width / self.density * x)
                end_x = round(width / self.density * (x + 1))

                img_section = img[start_y:end_y, start_x:end_x]
                average_color = img_section.mean(axis=(0, 1)).astype(numpy.uint8)
                colors.append(average_color)

        return colors

    def __analyze_img(self, path: str):
        img = cv2.imread(path)
        img = cv2.resize(img, (self.density * 100, self.density * 100))
        colors = self.__get_img_colors(img)
        img_key = colors_to_key(colors)

        with self.data_lock:
            img_list = self.palette.get(img_key, [])
            if path not in img_list:
                img_list.append(path)
                self.cache.pop(img_key)
            self.palette.set(img_key, img_list)

    def cancel(self):
        print(f"\r{self.progress}")
        print(self.stats)
        self.executor.shutdown(wait=True, cancel_futures=True)
        self.cache.save()
        self.palette.save()
