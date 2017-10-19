# Persist data!
from __future__ import print_function
import collections
import contextlib
import sqlite3
import os.path
import uuid
import time

# Helpers to work with times
SECOND = 1.0
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7
WORK_WEEK = DAY * 5
YEAR = DAY * 365

UUID = str(uuid.uuid4())

class DB(object):
    """ Access and store records in a DB. Manage updates. """
    def __init__(s, path):
        s.path = path
        s.struct = collections.OrderedDict()
        s.struct["id"] = "INTEGER PRIMARY KEY" # Entry ID
        s.struct["checkin"] = "NUMBER" # Time entry was logged
        s.struct["session"] = "TEXT" # ID for software session
        s.struct["period"] = "NUMBER" # Period of time this chunk covers
        s.struct["user"] = "TEXT" # Username
        s.struct["software"] = "TEXT" # Software running
        s.struct["file"] = "TEXT" # File loaded in software
        s.struct["status"] = "TEXT" # Status of user (ie active/idle/etc)
        s.struct["note"] = "TEXT" # Additional information

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

    def poll(s, period, user, software, file, status, note=""):
        """ Poll the database to show activity """
        with s:
            return s.write(None, time.time(), UUID, period, user, software, file, status, note)

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
        assert list(db.read_all()) == []
        # Add entries
        db.poll(1, "me", "python", "path/to/file", "active", "first entry")
        db.poll(1, "you", "python", "path/to/file", "idle", "second entry")
        db.poll(1, "us", "python", "path/to/file", "active", "last entry")
        res = list(db.read_all())
        assert len(res) == 3
        assert len(res[0]) == len(db.struct)
