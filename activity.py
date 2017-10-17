# Keep track of activity in software.
from __future__ import print_function
import db
import time
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
        print(db_path)
        Borg.__init__(s)
        s.active = True
        s.db = db.DB(db_path)
        s.interval = db.MINUTE * 5
        s.last_active = time.time()
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
            last_active = (time.time() - s.last_active) <= s.interval
            s.db.poll(s.user, s.software, s.path, "active" if last_active else "idle", s.note)
            time.sleep(s.interval)

    def checkin(s):
        """ Check in to show activity with software """
        s.last_active = time.time()

    def set_note(s, note):
        s.note = note
    def set_path(s, path):
        s.path = path

if __name__ == '__main__':
    import test
    import os
    import time
    with test.temp(".db") as tmp:
        os.unlink(tmp)
        mon = Monitor("python", "ME!", tmp)
        mon.interval = 1 # speed interval to one second
        mon.set_note("HI THERE")
        mon.set_path("path/to/file")
        print("Polling please wait...")
        mon.start()
        time.sleep(3)
        mon.stop()
        res = list(mon.db.read_all())
        assert len(res) == 3
        assert res[0]["file"] == "path/to/file"
        assert res[0]["note"] == "HI THERE"
