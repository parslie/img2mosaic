from arguments.parsers import Arguments


class Action:
    def __init__(self, args: Arguments):
        print(f'TODO: implement {self.__class__.__name__} __init__()')

    def run(self):
        print(f'TODO: implement {self.__class__.__name__} run()')

    def cancel(self):
        print(f'TODO: implement {self.__class__.__name__} cancel()')
