import time


class ScreenLogger:
    def __init__(self, eol="\x0d\x0a"):
        self.eol = eol

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def log(self, device, property, value, t=None):
        if t is None:
            t = time.time()

        print("[{0}] {1}: {2}".format(t, property, value), end=self.eol)
