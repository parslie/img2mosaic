import cv2
import numpy
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from glob import glob
from threading import Lock

from arguments.parsers import Arguments
from arguments.types import VALID_IMAGE_EXTS # TODO: should be handled differently
from data.cache import Cache
from data.palette import Palette
from utils import colors_to_key
from .base import Action


class Analyze(Action):
    def __init__(self, args: Arguments):
        self.__unpack_args(args)

        profile = f"{self.density}"
        self.cache = Cache(profile)
        self.palette = Palette(profile)

        self.__load_paths()

        self.futures = list[Future]()
        self.data_lock = Lock()
        self.paths_analyzed_lock = Lock()

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
        self.paths_analyzed = 0
        self.path_count = len(paths)

    def run(self):
        with ThreadPoolExecutor(max_workers=6) as executor:
            for path in self.paths:
                future = executor.submit(self.__analyze_img, path)
                self.futures.append(future)
            for future in as_completed(self.futures):
                self.paths_analyzed += 1
                print(f"{self.paths_analyzed} / {self.path_count} images analyzed", end="\r")
                if self.paths_analyzed % 1000 == 0:
                    with self.data_lock:
                        self.cache.save()
                        self.palette.save()
            print(f"{self.paths_analyzed} / {self.path_count} images analyzed")

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
        colors = self.__get_img_colors(img)
        img_key = colors_to_key(colors)

        with self.data_lock:
            img_list = self.palette.get(img_key, [])
            if path not in img_list:
                img_list.append(path)
                self.cache.pop(img_key)
            self.palette.set(img_key, img_list)

    def cancel(self):
        for future in self.futures:
            future.cancel()
        self.cache.save()
        self.palette.save()
