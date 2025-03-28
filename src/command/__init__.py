from pathlib import Path

import click
import cv2 as cv

from command.analyze import extract_colors, extract_image_paths, extract_image_sections
from database import Database


def generate(profile: str, density: int):
    pass


def analyze(profile: str, density: int, base_path: Path, recurse: bool):
    database = Database()

    image_paths = extract_image_paths(base_path, recurse)
    with click.progressbar(image_paths, label="Analyzing images") as bar:
        for image_path in bar:
            image = cv.imread(str(image_path), cv.IMREAD_COLOR_BGR)
            for image_section in extract_image_sections(image):
                colors = extract_colors(image_section.pixels, density)
                # TODO: Associate each color with the square sections in the database

    database.commit()
