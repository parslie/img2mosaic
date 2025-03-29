from pathlib import Path

import click
import cv2 as cv

from command.analyze import extract_colors, extract_image_paths, extract_image_sections
from database import Database
from database.models import Image


def generate(profile: str, density: int):
    pass


def analyze(profile: str, density: int, base_path: Path, recurse: bool):
    database = Database()

    image_paths = extract_image_paths(base_path, recurse)
    with click.progressbar(image_paths, label="Analyzing images") as bar:
        for image_path in bar:
            if database.has_image(profile, density, image_path):
                continue

            image = cv.imread(str(image_path), cv.IMREAD_COLOR_BGR)
            for image_section in extract_image_sections(image):
                color_str = ""
                for blue, green, red in extract_colors(image_section.pixels, density):
                    color_str += f"{blue:03d}{green:03d}{red:03d}"

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
