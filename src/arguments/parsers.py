from argparse import ArgumentParser
from dataclasses import dataclass

from .types import existing_folder, existing_image, image, positive_int


@dataclass
class Arguments:
    command: str = ""
    color_reduction: int = 1

    source: str = ""
    destination: str = ""
    source_size: int = 96
    pixel_size: int = 32

    directory: str = ""
    recursive: bool = False

    all: bool = False


def add_general_arguments(parser: ArgumentParser):
    parser.add_argument(
        "--reduce",
        type=positive_int,
        default=Arguments.color_reduction,
        dest="color_reduction",
        help="how much to reduce the color space (1 = full, 2 = half, 3 = third)",
        metavar="AMOUNT",
    )


def add_generation_arguments(parser: ArgumentParser):
    parser.add_argument(
        "source",
        type=existing_image,
        help="path to the image to mosaic",
    )
    parser.add_argument(
        "destination",
        type=image,
        help="path to output the generated mosaic",
    )
    parser.add_argument(
        "-s",
        dest="source_size",
        type=positive_int,
        default=Arguments.source_size,
        help="size of the image to mosaic",
        metavar="PIXELS",
    )
    parser.add_argument(
        "-p",
        dest="pixel_size",
        type=positive_int,
        default=Arguments.pixel_size,
        help="size of the images used as pixels",
        metavar="PIXELS",
    )


def add_analysis_arguments(parser: ArgumentParser):
    parser.add_argument(
        "directory",
        type=existing_folder,
        help="path to the directory of images to add to the palette",
        metavar="PATH",
    )
    parser.add_argument(
        "-r", "--recursive",
        default=False,
        action="store_true",
        help="recursively look through directory",
    )


def add_cache_arguments(parser: ArgumentParser):
    parser.add_argument(
        "-a", "--all",
        default=False,
        action="store_true",
        help="generate entries for all colors, even ones already cached",
    )


def create_parser() -> ArgumentParser:
    parser = ArgumentParser(
        "img2mosaic",
        description="Generates mosaics of images, where every pixel is represented by another image.",
        allow_abbrev=False,
    )
    sub_parsers = parser.add_subparsers(
        dest="action",
        required=True,
    )

    generate_parser = sub_parsers.add_parser(
        "generate",
        description="Generates a mosaic of an image, with images that have been analyzed.",
        help="generate a mosaic of an image",
    )
    add_generation_arguments(generate_parser)
    add_general_arguments(generate_parser)

    analyze_parser = sub_parsers.add_parser(
        "analyze",
        description="Analyzes which pixels images represent, so that they can be used for generation.",
        help="analyze images to represent pixels",
    )
    add_analysis_arguments(analyze_parser)
    add_general_arguments(analyze_parser)

    cache_parser = sub_parsers.add_parser(
        "cache",
        description="Analyzes colors and associates it with the closest existing color in the palette.",
        help="associate colors with close analyzed colors",
    )
    add_cache_arguments(cache_parser)
    add_general_arguments(cache_parser)

    return parser


def get_args() -> Arguments:
    parser = create_parser()
    args = Arguments()
    parser.parse_args(namespace=args)
    return args
