# Query and present data in a nice format.
from __future__ import print_function
import db

class Display(object):
    """ Load and display timesheet data in a nice format """
    def __init__(s, db_path):
        s.db = db.DB(db_path)

    def query(s, from_, to_):
        """ Query active entries betweem date amd date """
        with s.db:
            for row in s.db.read("status = ? AND checkin BETWEEN ? AND ?", "active", from_, to_):
                yield row

    def format_notes(s, in_, out_):
        """ Format """
        result = {}
        for row in s.query(in_, out_):
            print(row)
            result[row["note"]] = result.get(row["note"], 0) + row["period"]
        return result


if __name__ == '__main__':
    import os
    import test
    import time
    with test.temp() as tmp:
        os.unlink(tmp)
        tmp_db = db.DB(tmp)
        tmp_db.struct["note"] = "TEXT"
        tmp_db.struct["status"] = "TEXT"
        tmp_db.poll("Testing 123", "active")
        tmp_db.poll("Another test", "active")
        print(list(tmp_db.read_all()))
        disp = Display(tmp)
        print(disp.format_notes(time.time() - 10, time.time()))
