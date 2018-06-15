import sys

ESC       = chr(27)
CSI       = ESC + "["
CLEAR     = CSI + "2J"
MOVE_HOME = CSI + "H"
ERASE     = CLEAR + MOVE_HOME
MOVE_TO   = CSI + "{0};{1}H"

LINES = 24
COLS = 80


class Display:
    def __init__(self, title, info=None):
        self.title = title
        self.info = info

    def clear(self):
        sys.stdout.write(ERASE)
        sys.stdout.flush()

    def move_to(self, row, col):
        sys.stdout.write(MOVE_TO.format(row, col))
        sys.stdout.flush()

    def show_properties(self, properties, names=None):
        if names is None:
            names = properties.keys()

        max_len = max(map(len, names))

        self.clear()
        self.print(self.title.center(COLS))
        print()

        for k in names:
            self.print("{0}: {1}".format(k.rjust(max_len), properties[k]))

        if self.info is not None:
            self.move_to(LINES, 0)
            sys.stdout.write(self.info)
            sys.stdout.flush()

        self.move_to(LINES, 0)

    def print(self, message):
        print(message, end="\x0a\x0d")
