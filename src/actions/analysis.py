import cv2
import numpy
from concurrent.futures import Future, ThreadPoolExecutor
from glob import glob
from threading import Lock

from arguments import Arguments
from data.cache import load_cache, save_cache
from data.palette import load_palette, save_palette, get_palette_paths
from utils import colors_to_key

data_lock = Lock()
paths_analyzed_lock = Lock()
paths_analyzed = 0


def get_img_colors(img: numpy.ndarray, args: Arguments) -> list[numpy.ndarray]:
    height, width, _ = img.shape

    colors = []
    for y in range(args.density):
        start_y = round(height / args.density * y)
        end_y = round(height / args.density * (y + 1))

        for x in range(args.density):
            start_x = round(width / args.density * x)
            end_x = round(width / args.density * (x + 1))

            img_section = img[start_y:end_y, start_x:end_x]
            average_color = img_section.mean(axis=(0, 1)).astype(numpy.uint8)
            colors.append(average_color)
    
    return colors


def analyze_img(path: str, path_count: int, palette: dict, cache: dict, args: Arguments):
    global paths_analyzed

    img = cv2.imread(path) # TODO(?): crop image to square

    colors = get_img_colors(img, args)
    img_key = colors_to_key(colors)

    with paths_analyzed_lock:
        paths_analyzed += 1
        print(f'{paths_analyzed} / {path_count}', end='\r')

    with data_lock:
        img_list = palette.get(img_key, [])
        if path not in img_list:
            img_list.append(path)
            cache.pop(img_key, None)
        palette[img_key] = img_list

        if paths_analyzed % 1000 == 0:
            save_palette(args, palette)
            save_cache(args, cache)



def analyze_img_dir(args: Arguments):
    palette = load_palette(args)
    cache = load_cache(args)

    paths = set()
    for ext in ('jpg', 'jpeg', 'jpe', 'png', 'webp'):
        if args.recursive:
            new_paths = glob(f'{args.dir}/**/*.{ext}', recursive=True)
        else:
            new_paths = glob(f'{args.dir}/*.{ext}', recursive=False)
        paths.update(new_paths)

    if not args.all:
        paths.difference_update(get_palette_paths(palette))

    print(f'0 / {len(paths)}', end='\r')
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = list[Future]()
        try:
            for path in paths:
                future = executor.submit(analyze_img, path, len(paths), palette, cache, args)
                futures.append(future)
            for future in futures:
                future.result()
        except KeyboardInterrupt as inter:
            for future in futures:
                future.cancel()
            raise inter
    print()

    save_palette(args, palette)
