from actions.analysis import analyze_img_dir
from actions.cache import generate_cache
from actions.generation import generate_mosaic
from arguments.parsers import get_args 


def main():
    args = get_args()

    match args.action:
        case 'generate':
            generate_mosaic(args)
        case 'analyze':
            analyze_img_dir(args)
        case 'cache':
            generate_cache(args)


if __name__ == '__main__':
    main()
