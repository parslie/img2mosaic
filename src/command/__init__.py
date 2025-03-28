from pathlib import Path

import click

from command.analyze import extract_image_paths
from database import Database


def generate(profile: str, density: int):
    pass


def analyze(profile: str, density: int, base_path: Path, recurse: bool):
    database = Database()

    image_paths = extract_image_paths(base_path, recurse)
    with click.progressbar(image_paths, label="Analyzing images") as bar:
        for image_path in bar:
            pass
            # TODO:
            #   - Load image
            #   - Divide image into square sections
            #   - Get the average colors of each square section
            #   - Associate each color with the square sections in the database

    database.commit()
