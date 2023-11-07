import json
from os import makedirs
from os.path import exists as path_exists

from arguments.parsers import Arguments


def load_cache(args: Arguments) -> dict:
    file_name = f'cache.{args.density}.json'
    cache = {}
    if path_exists(f'{args.config}/{file_name}'):
        with open(f'{args.config}/{file_name}', 'r') as file:
            cache = json.loads(file.read())
    return cache


def save_cache(args: Arguments, cache: dict):
    file_name = f'cache.{args.density}.json'
    makedirs(args.config, exist_ok=True)
    with open(f'{args.config}/{file_name}', 'w') as file:
        file.write(json.dumps(cache, sort_keys=True))