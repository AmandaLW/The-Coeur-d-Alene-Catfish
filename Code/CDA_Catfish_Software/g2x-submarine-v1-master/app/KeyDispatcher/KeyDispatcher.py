import tty
import sys
import termios
import select


class KeyDispatcher:
    def __init__(self):
        self.table = {}

    def add(self, key, object, methodName):
        reference = (object, methodName)

        self.table[key] = reference

    def dispatch(self, key):
        if key in self.table:
            reference = self.table[key]
            instance = reference[0]
            method = getattr(instance, reference[1])

            return method()
        else:
            return True

    def can_process_key(self):
        return select.select([sys.stdin], [], [], 0.0)[0]

    def process_key(self):
        key = sys.stdin.read(1)[0]

        return self.dispatch(key)

    def __enter__(self):
        self.orig_settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin)

        return self

    def __exit__(self, type, value, traceback):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.orig_settings)
        self.table = None
        self.orig_settings = None
