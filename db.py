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
        s.struct["id"] = "INTEGER PRIMARY KEY"
        s.struct["start"] = "NUMBER"
        s.struct["end"] = "NUMBER"
        s.struct["user"] = "TEXT"
        s.struct["software"] = "TEXT"
        s.struct["file"] = "TEXT"
        s.struct["status"] = "TEXT"
        s.struct["notes"] = "TEXT"

    def create(s):
        """ Create a fresh database """
        db = sqlite3.connect(s.path)
        db.cursor().execute("CREATE TABLE timesheet ({})".format(",".join("{} {}".format(a, s.struct[a]) for a in s.struct)))
        db.commit()
        db.close()

    @contextlib.contextmanager
    def connect(s):
        """ Connect to the database and do something """
        if not os.path.isfile(s.path):
            s.create()
        db = sqlite3.connect(s.path)
        cursor = db.cursor()
        try:
            yield cursor
            db.commit()
        finally:
            db.close()

    def poll(s, user, software, file_path, status, notes=""):
        """ Poll the database to show activity """
        return s.write(time.time(), time.time(), user, software, file_path, status, notes)

    def write(s, *values):
        """ Write into DB stuff """
        with s.connect() as cursor:
            cursor.execute("INSERT INTO timesheet VALUES (null, ?, ?, ?, ?, ?, ?, ?)", values)
            return cursor.lastrowid

    def read(s, query, *values):
        """ Read query and return formatted response """
        with s.connect() as cursor:
            return [{k: v for k, v in zip(s.struct, r)} for r in cursor.execute("SELECT * FROM timesheet WHERE ({})".format(query), values)]

    def read_all(s):
        """ Quick way to grab all data from the database """
        return s.read("id!=0")

    def read_time(s, timeago):
        """ Grab records from the DB that have a start date greater than the provided time. """
        return s.read("start>=?", timeago)

if __name__ == '__main__':
    import test
    import pprint
    with test.temp(".db") as f:
        db = DB(f)
        pprint.pprint(db.read_all())
        db.poll("me", "python", "path/to/file", "active", "first test")
        db.poll("you", "python", "path/to/file", "active", "second test")
        db.poll("me", "python", "path/to/other/file", "idle", "third test")
        pprint.pprint(db.read_all())
        pprint.pprint(db.read_time(time.time() - 1000))
