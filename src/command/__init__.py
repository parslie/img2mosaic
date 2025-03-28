from pathlib import Path

from database import Database


def generate(profile: str, density: int):
    pass


def analyze(profile: str, density: int, base_path: Path, recurse: bool):
    database = Database()

    # TODO:
    # - Extract image paths from base_path
    # - For each image path
    #   - Load image
    #   - Divide image into square sections
    #   - Get the average colors of each square section
    #   - Associate each color with the square sections in the database

    database.commit()
