from argparse import ArgumentParser
from dataclasses import dataclass


@dataclass
class UnprocessedArguments:
    command: str = ""
    color_reduction: int = 1

    src: str = ""
    dst: str = ""
    src_size: int = 128
    pixel_size: int = 16

    dir: str = ""
    recursive: bool = False

    all: bool = False


def add_global_arguments(parser: ArgumentParser):
    parser.add_argument(
        "-c",
        default=UnprocessedArguments.color_reduction,
        type=int,
        help="how much to reduce the color space (1=full, 2=half, 3=third, ...)",
        dest="color_reduction",
    )


def add_generation_arguments(parser: ArgumentParser):
    parser.add_argument(
        "src",
        default=UnprocessedArguments.src,
        type=str,
        help="path to the image to create a mosaic of",
    )
    parser.add_argument(
        "dst",
        default=UnprocessedArguments.dst,
        type=str,
        help="path to output the mosaic to",
    )
    parser.add_argument(
        "-s",
        default=UnprocessedArguments.src_size,
        type=int,
        help="size of the image to create a mosaic of",
        metavar="PIXELS",
        dest="src_size",
    )
    parser.add_argument(
        "-p",
        default=UnprocessedArguments.pixel_size,
        type=int,
        help="size of the images to use as pixels",
        metavar="PIXELS",
        dest="pixel_size",
    )


def add_analysis_arguments(parser: ArgumentParser):
    parser.add_argument(
        "dir",
        default=UnprocessedArguments.dir,
        type=str,
        help="path to the directory of images to add to the palette",
    )
    parser.add_argument(
        "-r",
        action="store_true",
        default=UnprocessedArguments.recursive,
        help="recursively look through the directory",
        dest="recursive",
    )


def add_cache_arguments(parser: ArgumentParser):
    parser.add_argument(
        "-a",
        action="store_true",
        default=UnprocessedArguments.all,
        help="generate entries for all colors, even ones already cached",
        dest="color_reduction",
    )


def create_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="img2mosaic",
        description="Generates mosaics of images, where every pixel is represented by another image.",
        allow_abbrev=False,
    )
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    generation_parser = subparsers.add_parser(
        name="generate",
        help="generate a mosaic of an image",
        allow_abbrev=False,
    )
    add_global_arguments(generation_parser)
    add_generation_arguments(generation_parser)

    analysis_parser = subparsers.add_parser(
        name="analyze",
        help="analyze images to represent pixels",
        allow_abbrev=False,
    )
    add_global_arguments(analysis_parser)
    add_analysis_arguments(analysis_parser)

    cache_parser = subparsers.add_parser(
        name="cache",
        help="associate colors with close, already analyzed colors",
        allow_abbrev=False,
    )
    add_global_arguments(cache_parser)
    add_cache_arguments(cache_parser)

    return parser


@dataclass
class GenerationArguments:
    src: str
    dst: str
    src_size: int
    pixel_size: int


@dataclass
class AnalysisArguments:
    dir: str
    recursive: bool


@dataclass
class CacheArguments:
    all: bool


@dataclass
class Arguments:
    command: str
    color_reduction: int
    generation: GenerationArguments
    analysis: AnalysisArguments
    cache: CacheArguments


def parse_args() -> Arguments:
    parser = create_parser()
    args = UnprocessedArguments()
    parser.parse_args(namespace=args)
    return Arguments(
        command=args.command,
        color_reduction=args.color_reduction,
        generation=GenerationArguments(
            src=args.src,
            dst=args.dst,
            src_size=args.src_size,
            pixel_size=args.pixel_size,
        ),
        analysis=AnalysisArguments(
            dir=args.dir,
            recursive=args.recursive,
        ),
        cache=CacheArguments(
            all=args.all,
        ),
    )
