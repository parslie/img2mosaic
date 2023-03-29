import json
from argparse import Namespace
from os import makedirs
from os.path import exists as path_exists


def load_palette(args: Namespace) -> dict:
    file_name = f'palette.{args.pixels_per_img}x{args.pixels_per_img}.json'
    palette = {}
    if path_exists(f'{args.config}/{file_name}'):
        with open(f'{args.config}/{file_name}', 'r') as file:
            palette = json.loads(file.read())
    return palette


def save_palette(args: Namespace, palette: dict):
    file_name = f'palette.{args.pixels_per_img}x{args.pixels_per_img}.json'
    makedirs(args.config, exist_ok=True)
    with open(f'{args.config}/{file_name}', 'w') as file:
        file.write(json.dumps(palette, sort_keys=True))


def get_palette_paths(palette: dict) -> set:
    paths = set()
    for path in palette.values():
        paths.update(path)
    return paths