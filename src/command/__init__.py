from pathlib import Path

import click
import cv2 as cv

from command.analyze import extract_colors, extract_image_paths, extract_image_sections
from database import Database
from database.models import Image
from util import colors_to_str


def generate(profile: str, density: int):
    database = Database()
    image = database.get_random_image(profile, density, [(52, 10, 217)])
    print(image)


def analyze(profile: str, density: int, base_path: Path, recurse: bool):
    database = Database()

    image_paths = extract_image_paths(base_path, recurse)
    with click.progressbar(image_paths, label="Analyzing images") as bar:
        for image_path in bar:
            if database.has_image(profile, density, image_path):
                continue

            image = cv.imread(str(image_path), cv.IMREAD_COLOR_BGR)
            for image_section in extract_image_sections(image):
                color_str = colors_to_str(extract_colors(image_section.pixels, density))
                db_image = Image(
                    path=str(image_path),
                    x=image_section.x,
                    y=image_section.y,
                    density=density,
                    profile=profile,
                    color_str=color_str,
                )
                database.add(db_image)

    database.commit()
