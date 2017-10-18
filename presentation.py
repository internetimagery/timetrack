# Query and present data in a nice format.
from __future__ import print_function
import db

class Display(object):
    """ Load and display timesheet data in a nice format """
    def __init__(s, db_path):
        s.db = db.DB(db_path)

    def format(s, query):
        """ Format """
        pass


if __name__ == '__main__':
    import os
    import test
    with test.temp() as tmp:
        os.unlink(tmp)
        db = db.DB(tmp)
        db.struct["note"] = "TEXT"
        db.poll("Testing 123")
        db.poll("Another test")
        disp = Display(tmp)
