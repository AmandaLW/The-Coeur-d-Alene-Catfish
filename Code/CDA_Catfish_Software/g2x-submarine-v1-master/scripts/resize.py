#!/usr/bin/env python3

import sys
import fcntl
import struct
import termios

if len(sys.argv) == 3:
    rows = int(sys.argv[1])
    cols = int(sys.argv[2])
    fd = sys.stdin.fileno()
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))
else:
    print("usage: resize <rows> <columns>")

