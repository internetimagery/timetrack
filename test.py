# Helpers to run small tests.
from __future__ import print_function

import os
import time
import os.path
import tempfile
import contextlib

TEST = os.path.join(os.path.dirname(__file__), "temp")

@contextlib.contextmanager
def temp(suffix=""):
    """ Output a temporary file name and remove the file if created """
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    tmp.close()
    try:
        yield tmp.name
    finally:
        if os.path.isfile(tmp.name):
            os.unlink(tmp.name)

if __name__ == '__main__':
    with temp(".txt") as f:
        print("File:", f)
    print("Exists?:", os.path.isfile(f))
