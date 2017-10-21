# Keep track of activity in software.
from __future__ import print_function
import db
import time
import os.path
import threading
import timestamp


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Monitor(object):
    __metaclass__ = Singleton
    """ Monitor status and periodically poll DB """
    def __init__(s, software, user, db_path=os.path.expanduser("~/timesheet.db")):
        # Create database and set its structure
        s.db = db.DB(db_path)

        # Set variables
        s.active = False # Keep polling? Stop?
        s.period = timestamp.MINUTE * 5 # Poll how often?
        s.last_active = timestamp.now() # Last checkin
        s.note = ""
        s.software = software
        s.user = user
        s.path = ""

    def start(s):
        """ Begin polling """
        if not s.active:
            s.active = True
            threading.Thread(target=s.poll_loop).start()

    def stop(s):
        """ Stop polling for whatever reason """
        s.active = False

    def poll_loop(s):
        """ Periodically update DB """
        while s.active:
            if timestamp.now() - s.last_active <= s.period: # Check if we are idle...
                s.poll()
            time.sleep(s.period)


    def poll(s):
        """ Update DB with activity """
        if s.active:
            s.db.poll(s.period, s.user, s.software, s.path, "active", s.note)

    def checkin(s):
        """ Check in to show activity with software """
        s.last_active = timestamp.now()

    def query(s, from_, to_):
        """ Query active entries betweem timestamp amd timestamp """
        with s.db:
            for row in s.db.read("status = ? AND checkin BETWEEN ? AND ?", "active", from_, to_):
                yield row

    def set_note(s, note):
        note = note.strip()
        if note != s.note:
            s.note = note
            s.poll()

    def set_path(s, path):
        path = path.strip()
        if path != s.path:
            s.path = path
            s.poll()

if __name__ == '__main__':
    import test
    import os
    with test.temp(".db") as tmp:
        os.unlink(tmp)
        mon = Monitor("python", "ME!", tmp)
        mon.period = 1 # speed period to one second
        mon.set_note("HI THERE")
        mon.set_path("path/to/file")
        print("Polling please wait...")
        mon.start()
        time.sleep(1) # One active
        mon.checkin()
        time.sleep(2) # One active, one idle
        mon.stop()
        curr = timestamp.now()
        res = list(mon.query(curr - 10, curr))
        assert len(res) == 2
        assert res[0]["file"] == "path/to/file"
        assert res[0]["note"] == "HI THERE"
