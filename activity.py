# Keep track of activity in software.
from __future__ import print_function
import db
import time
import date
import os.path
import threading

class Borg(object):
    """ Maintain singleton status """
    _shared_state = {}
    def __init__(s):
        s.__dict__ = s._shared_state

class Monitor(Borg):
    """ Monitor status and periodically poll DB """
    def __init__(s, software, user, db_path=os.path.expanduser("~/timesheet.db")):
        Borg.__init__(s)
        # Create database and set its structure
        s.db = db.DB(db_path)

        # Set variables
        s.active = True # Keep polling? Stop?
        s.period = date.MINUTE * 5 # Poll how often?
        s.last_active = date.timestamp() # Last checkin
        s.note = ""
        s.software = software
        s.user = user
        s.path = ""

    def start(s):
        """ Begin polling """
        s.active = True
        threading.Thread(target=s.poll).start()

    def stop(s):
        """ Stop polling for whatever reason """
        s.active = False

    def poll(s):
        """ Update DB with activity """
        while s.active:
            last_active = (date.timestamp() - s.last_active) <= s.period
            s.db.poll(s.period, s.user, s.software, s.path, "active" if last_active else "idle", s.note)
            time.sleep(s.period)

    def checkin(s):
        """ Check in to show activity with software """
        s.last_active = date.timestamp()

    def query(s, from_, to_):
        """ Query active entries betweem date amd date """
        with s.db:
            for row in s.db.read("status = ? AND checkin BETWEEN ? AND ?", "active", from_, to_):
                yield row

    def set_note(s, note):
        s.note = note
    def set_path(s, path):
        s.path = path

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
        curr = date.timestamp()
        res = list(mon.query(curr - 10, curr))
        assert len(res) == 2
        assert res[0]["file"] == "path/to/file"
        assert res[0]["note"] == "HI THERE"
