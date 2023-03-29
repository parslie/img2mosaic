import json
from argparse import Namespace
from os import makedirs
from os.path import exists as path_exists


def load_cache(args: Namespace) -> dict:
    file_name = f'cache.{args.pixels_per_img}x{args.pixels_per_img}.json'
    cache = {}
    if path_exists(f'{args.config}/{file_name}'):
        with open(f'{args.config}/{file_name}', 'r') as file:
            cache = json.loads(file.read())
    return cache


def save_cache(args: Namespace, cache: dict):
    file_name = f'cache.{args.pixels_per_img}x{args.pixels_per_img}.json'
    makedirs(args.config, exist_ok=True)
    with open(f'{args.config}/{file_name}', 'w') as file:
        file.write(json.dumps(cache, sort_keys=True))