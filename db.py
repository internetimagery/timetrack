# Persist data!
from __future__ import print_function
import collections
import contextlib
import sqlite3
import os.path
import time

# Helpers to work with times
SECOND = 1
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7
WORK_WEEK = DAY * 5
YEAR = DAY * 365

class DB(object):
    """ Access and store records in a DB. Manage updates. """
    def __init__(s, path):
        s.path = path
        s.struct = collections.OrderedDict()
        s.struct["id"] = "INTEGER PRIMARY KEY" # Entry ID
        s.struct["checkin"] = "NUMBER" # Time entry was logged

    def __enter__(s):
        """ Start context manager """
        exist = os.path.isfile(s.path)
        s.db = db = sqlite3.connect(s.path)
        s.cursor = db.cursor()
        if not exist:
            s.cursor.execute("CREATE TABLE timesheet ({})".format(",".join("{} {}".format(a, s.struct[a]) for a in s.struct)))

    def __exit__(s, exc_type, exc_val, exc_tb):
        """ Close DB connection """
        if not exc_type:
            s.db.commit()
        s.db.close()

    def write(s, *values):
        """ Write into DB stuff """
        num = len(s.struct)
        if len(values) != num:
            raise RuntimeError("Not enough values provided.")
        s.cursor.execute("INSERT INTO timesheet VALUES ({})".format(",".join("?" for _ in range(num))), values)
        return s.cursor.lastrowid

    def read(s, query, *values):
        """ Read query and return formatted response """
        return ({k: v for k, v in zip(s.struct, r)} for r in s.cursor.execute("SELECT * FROM timesheet WHERE ({})".format(query), values))

    def poll(s, *values):
        """ Poll the database to show activity """
        with s:
            return s.write(None, time.time(), *values)

    def read_all(s):
        """ Quick way to grab all data from the database """
        with s:
            for row in s.read("id != 0"):
                yield row

if __name__ == '__main__':
    import test
    import os
    with test.temp(".db") as f:
        os.unlink(f)
        db = DB(f)
        db.struct["field"] = "TEXT"
        assert list(db.read_all()) == []
        # Add entries
        db.poll("first test")
        db.poll("second test")
        db.poll("third test")
        assert len(list(db.read_all())) == 3
