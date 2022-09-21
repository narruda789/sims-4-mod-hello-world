from enum import IntEnum


class CommandType(IntEnum):
    DebugOnly = 1
    Automation = 3
    Cheat = 4
    Live = 5


def Command(*aliases, command_type=CommandType.DebugOnly):
    def named_command(func):
        return func

    return named_command


class Output:
    __slots__ = ('_context',)

    def __init__(self, context):
        self._context = context

    def __call__(self, s):
        output(s, self._context)


def output(s, context):
    pass


class CheatOutput(Output):
    def __call__(self, s):
        print(s)
