# Keep track of activity in software.
from __future__ import print_function
import db
import time
import os.path
import threading
import timestamp

# https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python#6798042
class _Singleton(type):
    """ A metaclass that creates a Singleton base class when called. """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Singleton(_Singleton('SingletonMeta', (object,), {})): pass

# class Monitor(object):
class Monitor(Singleton):
    # __metaclass__ = Singleton
    """ Monitor status and periodically poll DB """
    def __init__(s, software, user, db_path=os.path.expanduser("~/timesheet.db")):
        # Create database and set its structure
        s.db = db.DB(db_path)

        # Set variables
        s._active = False # Keep polling? Stop?
        s._period = timestamp.MINUTE * 5 # Poll how often?
        s._last_active = timestamp.now() # Last checkin
        s._note = ""
        s._software = software
        s._user = user
        s._path = ""

    def start(s):
        """ Begin polling """
        if not s._active:
            s._active = True
            threading.Thread(target=s.poll_loop).start()

    def stop(s):
        """ Stop polling for whatever reason """
        s._active = False

    def poll_loop(s):
        """ Periodically update DB """
        while s._active:
            if timestamp.now() - s._last_active <= s._period: # Check if we are idle...
                s.poll()
            time.sleep(s._period)

    def poll(s):
        """ Update DB with activity """
        if s._active:
            s.db.poll(s._period, s._user, s._software, s._path, "active", s._note)

    def checkin(s):
        """ Check in to show activity with software """
        s._last_active = timestamp.now()

    def query(s, from_, to_):
        """ Query active entries betweem timestamp amd timestamp """
        with s.db:
            for row in s.db.read("status = ? AND checkin BETWEEN ? AND ?", "active", from_, to_):
                yield row

    def set_var(s, var, val):
        """ Set variable only on changes and poll, generic. """
        val = val.strip()
        if val != getattr(s, var):
            setattr(s, var, val)
            s.poll()

    def set_note(s, val):
        s.set_var("_note", val)
    def get_note(s):
        return s._note
    def set_path(s, val):
        s.set_var("_path", val)
    def get_path(s):
        return s._path

    def get_status(s):
        return s._active

if __name__ == '__main__':
    import test
    import os
    with test.temp(".db") as tmp:
        os.unlink(tmp)
        mon = Monitor("python", "ME!", tmp)
        mon._period = 1 # speed period to one second
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
