#!python
from argparse import ArgumentParser
from os import path

import mode


def path_type(value):
    return path.expanduser(value)


parser = ArgumentParser('Img2Mosaic')
subparsers = parser.add_subparsers(dest='mode', required=True)

mosaic_parser = subparsers.add_parser('mosaic', help='mode for generating mosaics')
mosaic_parser.add_argument('src', type=path_type, help='path to the image to mosaic')
mosaic_parser.add_argument('dest', type=path_type, help='path to the generated mosaic')
mosaic_parser.add_argument('-s', dest='src_size', type=int, help='size of the image to mosaic')
mosaic_parser.add_argument('-p', dest='pixel_size', type=int, default=16, help='size of the images used as pixels')

palette_parser = subparsers.add_parser('palette', help='mode for analyzing images to use as pixels')
palette_parser.add_argument('dirs', nargs='+', type=path_type, help='paths to the directories of images to add to the palette')

for subparser in [mosaic_parser, palette_parser]:
    subparser.add_argument('--config', type=path_type, default='~/.config/img2mosaic', help='path to config folder')

if __name__ == '__main__':
    args = parser.parse_args()
    
    if args.mode == 'mosaic':
        mode.mosaic(args)
    elif args.mode == 'palette':
        mode.palette(args)