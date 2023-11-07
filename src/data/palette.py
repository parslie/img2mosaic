import json
from os import makedirs
from os.path import exists as path_exists

from arguments.parsers import Arguments


def load_palette(args: Arguments) -> dict:
    file_name = f'palette.{args.density}.json'
    palette = {}
    if path_exists(f'{args.config}/{file_name}'):
        with open(f'{args.config}/{file_name}', 'r') as file:
            palette = json.loads(file.read())
    return palette


def save_palette(args: Arguments, palette: dict):
    file_name = f'palette.{args.density}.json'
    makedirs(args.config, exist_ok=True)
    with open(f'{args.config}/{file_name}', 'w') as file:
        file.write(json.dumps(palette, sort_keys=True))


def get_palette_paths(palette: dict) -> set:
    paths = set()
    for path in palette.values():
        paths.update(path)
    return paths