from actions.analysis import analyze_img_dir
from actions.generation import generate_mosaic
from arguments import get_arguments 


def main():
    args = get_arguments()

    match args.action:
        case 'generate':
            generate_mosaic(args)
        case 'analyze':
            analyze_img_dir(args)


if __name__ == '__main__':
    main()
