# Helpers to run small tests.
from __future__ import print_function

import os
import time
import os.path
import contextlib

TEST = os.path.join(os.path.dirname(__file__), "temp")

@contextlib.contextmanager
def temp(suffix=""):
    """ Output a temporary file name and remove the file if created """
    if not os.path.isdir(TEST):
        os.mkdir(TEST)
    tmp = os.path.join(TEST, str(time.time()) + suffix)
    try:
        yield tmp
    finally:
        if os.path.isfile(tmp):
            os.unlink(tmp)

if __name__ == '__main__':
    with temp(".txt") as f:
        print("File:", f)
