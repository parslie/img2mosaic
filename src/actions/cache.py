import math
import random
from time import perf_counter
from typing import Generator

from arguments.parsers import Arguments
from data.cache import Cache as CacheData
from data.palette import Palette
from utils.colors import colors_to_closest_key, key_to_colors
from utils.progress import Progress
from .base import Action


def all_single_color_keys(complexity: int) -> Generator[str, None, None]:
    # r_values = list(range(256))
    # random.shuffle(r_values)
    r_values = range(0, 256, complexity)
    for r in r_values:
        # g_values = list(range(256))
        # random.shuffle(g_values)
        g_values = range(0, 256, complexity)
        for g in g_values:
            # b_values = list(range(256))
            # random.shuffle(b_values)
            b_values = range(0, 256, complexity)
            for b in b_values:
                yield f"{r} {g} {b}"


def all_color_keys_helper(color_count: int, complexity: int) -> Generator[str, None, None]:
    for color_key in all_single_color_keys(complexity):
        if color_count == 1:
            yield f"{color_key}"
        else:
            for next_color_key in all_color_keys_helper(color_count - 1, complexity):
                yield f"{color_key} {next_color_key}"


def all_color_keys(density: int, complexity: int) -> Generator[str, None, None]:
    for color_key in all_color_keys_helper(density ** 2, complexity):
        yield color_key


def total_color_count(density: int, complexity: int) -> int:
    per_density_count = (256 // complexity) ** 3
    count = per_density_count ** (density ** 2)
    # for _ in range(density ** 2):
    #     count *= per_density_count
    return count


class Statistics:
    def __init__(self):
        self.completion_time = 0
    
    def __repr__(self) -> str:
        return f"Completion time: {self.completion_time:.1f} sec"


class Cache(Action):
    def __init__(self, args: Arguments):
        self.__unpack_args(args)

        profile = f"{self.density} {self.complexity}"
        self.cache = CacheData(profile)
        self.palette = Palette(profile)

        self.progress = Progress(total_color_count(self.density, self.complexity))
        self.stats = Statistics()

    def __unpack_args(self, args: Arguments):
        self.all = args.all
        self.density = args.density
        self.complexity = args.complexity

    def run(self):
        print(self.progress, end="\r")
        start_time = perf_counter()

        for color_key in all_color_keys(self.density, self.complexity):
            if self.all or not self.cache.contains(color_key):
                colors = key_to_colors(color_key)
                # TODO: do not use palette's data dict directly here
                closest_key = colors_to_closest_key(self.palette.data, colors)
                self.cache.set(color_key, closest_key)
                
                if self.progress.current % 100 == 0:
                    self.cache.save()

            end_time = perf_counter()
            self.stats.completion_time += end_time - start_time
            start_time = end_time
            
            self.progress.current += 1
            self.progress.speed = self.progress.current / self.stats.completion_time
            print(self.progress, end="\r")

        print(self.progress)
        print(self.stats)
        self.cache.save()

    def cancel(self):
        print(f"\r{self.progress}")
        print(self.stats)
        self.cache.save()
