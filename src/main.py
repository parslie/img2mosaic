# from actions.analysis import analyze_img_dir
# from actions.cache import generate_cache
# from actions.generation import generate_mosaic
from actions.analysis import Analyze
from actions.generation import Generate
from arguments.parsers import get_args 


def main():
    args = get_args()
    action = None

    match args.action:
        case "generate":
            action = Generate(args)
        case "analyze":
            action = Analyze(args)
        case "cache":
            pass

    try:
        action.run()
    except KeyboardInterrupt:
        action.cancel()


if __name__ == '__main__':
    main()
