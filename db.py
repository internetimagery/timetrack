# Persist data!
from __future__ import print_function
import contextlib
import sqlite3
import os.path
import time

class DB(object):
    """ Access and store records in a DB. Manage updates. """
    def __init__(s, path):
        s.path = path

    def create(s):
        """ Create a fresh database """
        db = sqlite3.connect(s.path)
        db.cursor().execute("CREATE TABLE timesheet (id INTEGER PRIMARY KEY, start NUMBER, end NUMBER, user TEXT, software TEXT, file TEXT, status TEXT, notes TEXT)")
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
            yield cursor.execute
            db.commit()
        finally:
            db.close()

    def poll(s, user, software, file_path, status, notes=""):
        """ Poll the database to show activity """
        with s.connect() as db:
            db("INSERT INTO timesheet VALUES (null, ?, ?, ?, ?, ?, ?, ?)", (time.time(), time.time(), user, software, file_path, status, notes))

    def read_all(s):
        """ Quick way to grab all data from the database """
        with s.connect() as db:
            return [r for r in db("SELECT * FROM timesheet")]


if __name__ == '__main__':
    import test
    with test.temp(".db") as f:
        db = DB(f)
        print(db.read_all())
        db.poll("me", "python", "path/to/file", "active", "first test")
        print(db.read_all())
