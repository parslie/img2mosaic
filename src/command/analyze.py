from dataclasses import dataclass
from pathlib import Path
from typing import Generator

import cv2 as cv
import cv2.typing as cvt

from util import VALID_IMAGE_EXTS


def extract_image_paths(base_path: Path, recurse: bool) -> list[Path] | None:
    if base_path.is_file() and base_path.suffix[1:] in VALID_IMAGE_EXTS:
        return [base_path]
    elif base_path.is_dir():
        image_paths = []
        for image_ext in VALID_IMAGE_EXTS:
            glob_pattern = f"**.{image_ext}" if recurse else f"*.{image_ext}"
            image_paths.extend(base_path.glob(glob_pattern))
        return image_paths
    else:
        return None


@dataclass
class ImageSection:
    pixels: cvt.MatLike
    x: int
    y: int
    size: int


def extract_image_sections(image: cvt.MatLike) -> Generator[ImageSection]:
    (height, width, _) = image.shape

    if width >= height:
        section_size = height
        section_count = width - height + 1
        delta_x = 1
        delta_y = 0
    else:
        section_size = width
        section_count = height - width + 1
        delta_x = 0
        delta_y = 1

    for section_idx in range(section_count):
        x_start = delta_x * section_idx
        y_start = delta_y * section_idx
        x_end = x_start + section_size
        y_end = y_start + section_size
        yield ImageSection(
            pixels=image[y_start:y_end, x_start:x_end],
            x=x_start,
            y=y_start,
            size=section_size,
        )


def extract_colors(image: cvt.MatLike, density: int) -> list[tuple[int, int, int]]:
    colors = []

    subsection_height = image.shape[0] / density
    subsection_width = image.shape[1] / density
    for density_y in range(density):
        for density_x in range(density):
            x_start = round(density_x * subsection_width)
            y_start = round(density_y * subsection_height)
            x_end = round((density_x + 1) * subsection_width)
            y_end = round((density_y + 1) * subsection_height)
            (blue, green, red, _) = cv.mean(image[y_start:y_end, x_start:x_end])
            colors.append((round(blue), round(green), round(red)))

    return colors
