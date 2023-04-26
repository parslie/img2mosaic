from argparse import ArgumentParser, ArgumentTypeError
from dataclasses import dataclass
from os import path


@dataclass
class Arguments:
    density: int = 1
    config: str = '~/.config/img2mosaic'

    action: str = ''

    src: str = ''
    dest: str = ''
    src_size: int = 128
    pixel_size: int = 32

    dir: str = ''
    recursive: bool = False
    all: bool = False


def config_path_type(value: str) -> str:
    value = path.expanduser(value)
    if path.isfile(value):
        raise ArgumentTypeError(f'{value} is not a directory')
    return value


def src_img_path_type(value: str) -> str:
    value = path.expanduser(value)
    if not path.exists(value):
        raise ArgumentTypeError(f'{value} does not exist')
    elif path.isdir(value):
        raise ArgumentTypeError(f'{value} is not a file')
    return value


def dest_img_path_type(value: str) -> str:
    value = path.expanduser(value)
    if path.isdir(value):
        raise ArgumentTypeError(f'{value} is not a file')
    return value


def analysis_path_type(value: str) -> str:
    value = path.expanduser(value)
    if not path.exists(value):
        raise ArgumentTypeError(f'{value} does not exist')
    elif path.isfile(value):
        raise ArgumentTypeError(f'{value} is not a directory')
    return value


def add_general_arguments(parser: ArgumentParser):
    parser.add_argument(
        '--density',
        type=int,
        default=Arguments.density,
        help='amount of pixels to be represented by one image',
        metavar='PIXELS',
    )
    parser.add_argument(
        '--config',
        type=config_path_type,
        default=Arguments.config,
        help='path to config folder',
    )


def add_generation_arguments(parser: ArgumentParser):
    parser.add_argument(
        'src',
        type=src_img_path_type,
        help='path to the image to mosaic',
    )
    parser.add_argument(
        'dest',
        type=dest_img_path_type,
        help='path to the generated mosaic',
    )
    parser.add_argument(
        '-s',
        dest='src_size',
        type=int,
        default=Arguments.src_size,
        help='size of the image to mosaic',
        metavar='PIXELS',
    )
    parser.add_argument(
        '-p',
        dest='pixel_size',
        type=int,
        default=Arguments.pixel_size,
        help='size of the images used as pixels',
        metavar='PIXELS',
    )


def add_analysis_arguments(parser: ArgumentParser):
    parser.add_argument(
        'dir', 
        type=analysis_path_type, 
        help='path to the directory of images to add to the palette',
        metavar='PATH',
    )
    parser.add_argument(
        '-r', '--recursive',
        default=False,
        action='store_true',
        help='recursively look through directory',
    )
    parser.add_argument(
        '-a', '--all',
        default=False,
        action='store_true',
        help='analyze all images in the directory, even ones already analyzed',
    )


def add_cache_arguments(parser: ArgumentParser):
    parser.add_argument(
        '-a', '--all',
        default=False,
        action='store_true',
        help='generate entries for all colors, even ones already cached',
    )


def create_parser() -> ArgumentParser:
    parser = ArgumentParser(
        'img2mosaic',
        description='Generates mosaics of images, where every pixel is represented by another image.',
        allow_abbrev=False,
    )
    sub_parsers = parser.add_subparsers(title='actions', dest='action', required=True)

    generate_parser = sub_parsers.add_parser(
        'generate',
        description='Generates a mosaic of an image, with images that have been analyzed.',
        help='generate a mosaic of an image',
    )
    add_generation_arguments(generate_parser)
    add_general_arguments(generate_parser)

    analyze_parser = sub_parsers.add_parser(
        'analyze',
        description='Analyzes which pixels images represent, so that they can be used for generation.',
        help='analyze images to represent pixels',
    )
    add_analysis_arguments(analyze_parser)
    add_general_arguments(analyze_parser)

    # TODO: finish
    cache_parser = sub_parsers.add_parser(
        'cache',
        description='TODO',
        help='TODO',
    )
    add_cache_arguments(cache_parser)
    add_general_arguments(cache_parser)
    
    return parser


def get_arguments() -> Arguments:
    parser = create_parser()
    args = Arguments()
    parser.parse_args(namespace=args)
    return args
