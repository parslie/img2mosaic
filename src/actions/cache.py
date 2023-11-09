import random
from typing import Generator

from arguments.parsers import Arguments
from data.cache import Cache as CacheData
from data.palette import Palette
from utils import colors_to_closest_key, key_to_colors
from .base import Action


def all_single_color_keys() -> Generator[str, None, None]:
    r_values = list(range(256))
    random.shuffle(r_values)
    for r in r_values:
        g_values = list(range(256))
        random.shuffle(g_values)
        for g in g_values:
            b_values = list(range(256))
            random.shuffle(b_values)
            for b in b_values:
                yield f"{r} {g} {b}"


def all_color_keys_helper(color_count: int) -> Generator[str, None, None]:
    for color_key in all_single_color_keys():
        if color_count == 1:
            yield f"{color_key}"
        else:
            for next_color_key in all_color_keys_helper(color_count - 1):
                yield f"{color_key} {next_color_key}"


def all_color_keys(density: int) -> Generator[str, None, None]:
    for color_key in all_color_keys_helper(density ** 2):
        yield color_key


def total_color_count(density: int) -> int:
    per_density_count = 256 ** 3
    count = per_density_count ** (density ** 2)
    # for _ in range(density ** 2):
    #     count *= per_density_count
    return count


class Cache(Action):
    def __init__(self, args: Arguments):
        self.__unpack_args(args)

        profile = f"{self.density}"
        self.cache = CacheData(profile)
        self.palette = Palette(profile)

    def __unpack_args(self, args: Arguments):
        self.all = args.all
        self.density = args.density

    def run(self):
        color_count = total_color_count(self.density)
        colors_cached = 0

        print("0.00%", end="\r")
        for color_key in all_color_keys(self.density):
            colors_cached += 1

            if self.all or not self.cache.contains(color_key):
                colors = key_to_colors(color_key)
                # TODO: do not use palette's data dict directly here
                closest_key = colors_to_closest_key(self.palette.data, colors)
                self.cache.set(color_key, closest_key)
                
                if colors_cached % 100 == 0:
                    self.cache.save()
            print(f"{colors_cached / color_count:.2f}%", end="\r")
        print("100.00%")
        
        self.cache.save()

    def cancel(self):
        self.cache.save()
