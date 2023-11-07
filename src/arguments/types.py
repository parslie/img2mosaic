from argparse import ArgumentTypeError
from os import path

# Taken from OpenCV documentation
# NOTE: may restrict
VALID_IMAGE_EXTS = (
    "bmp", "dib",
    "jpeg", "jpg", "jpe",
    "jp2",
    "png",
    "webp",
    "avif",
    "pbm", "pgm", "ppm", "pxm", "pnm",
    "pfm",
    "sr", "ras",
    "tiff", "tif",
    "exr",
    "hdr", "pic",
)


def image(value: str) -> str:
    ext = path.splitext(value)[1][1:]
    if ext.lower() not in VALID_IMAGE_EXTS:
        raise ArgumentTypeError(f"{value} is not an image")
    return value


def existing_image(value: str) -> str:
    if not path.exists(value):
        raise ArgumentTypeError(f"{value} does not exist")
    elif not path.isfile(value):
        raise ArgumentTypeError(f"{value} is not a file")
    return image(value)


def existing_folder(value: str) -> str:
    if not path.exists(value):
        raise ArgumentTypeError(f"{value} does not exist")
    elif not path.isdir(value):
        raise ArgumentTypeError(f"{value} is not a directory")
    return value


def positive_int(value: str) -> int:
    if not value.isnumeric():
        raise ArgumentTypeError(f"{value} is not a number")
    
    value: int = int(value)
    if value <= 0:
        raise ArgumentTypeError(f"{value} is not a positive integer")
    return value
