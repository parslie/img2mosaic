from commands.analysis import Analyze
from commands.cache import Cache
from commands.generation import Generate
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
            action = Cache(args)

    try:
        action.run()
    except KeyboardInterrupt:
        action.cancel()


if __name__ == '__main__':
    main()
