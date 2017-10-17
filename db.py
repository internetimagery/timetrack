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
        s.struct["user"] = "TEXT" # Username
        s.struct["software"] = "TEXT" # Software running
        s.struct["file"] = "TEXT" # File loaded in software
        s.struct["status"] = "TEXT" # Status of user (ie active/idle/etc)
        s.struct["note"] = "TEXT" # Additional information

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

    def write(s, cursor, *values):
        """ Write into DB stuff """
        num = len(s.struct)
        if len(values) != num:
            raise RuntimeError("Not enough values provided.")
        cursor.execute("INSERT INTO timesheet VALUES ({})".format(",".join("?" for _ in range(num))), values)
        return cursor.lastrowid

    def read(s, cursor, query, *values):
        """ Read query and return formatted response """
        return ({k: v for k, v in zip(s.struct, r)} for r in cursor.execute("SELECT * FROM timesheet WHERE ({})".format(query), values))

    def poll(s, user, software, file_path, status, note=""):
        """ Poll the database to show activity """
        with s.connect() as db:
            return s.write(db, None, time.time(), user, software, file_path, status, note)

    def read_all(s):
        """ Quick way to grab all data from the database """
        with s.connect() as db:
            for row in s.read(db, "id != 0"):
                yield row

    def read_time(s, timeago):
        """ Grab records from the DB that have a start date greater than the provided time. """
        with s.connect() as db:
            for row in s.read(db, "checkin >= ?", timeago):
                yield row

if __name__ == '__main__':
    import test
    import os
    with test.temp(".db") as f:
        os.unlink(f)
        db = DB(f)
        assert list(db.read_all()) == []
        # Add entries
        db.poll("me", "python", "path/to/file", "active", "first test")
        db.poll("you", "python", "path/to/file", "active", "second test")
        db.poll("me", "python", "path/to/other/file", "idle", "third test")
        assert len(list(db.read_all())) == 3
        assert len(list(db.read_time(time.time() - 1000))) == 3
