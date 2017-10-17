# Keep track of activity in software.
from __future__ import print_function
import db
import time
import threading

class Borg(object):
    """ Maintain singleton status """
    _shared_state = {}
    def __init__(s):
        s.__dict__ = s._shared_state

class Monitor(Borg):
    """ Monitor status and periodically poll DB """
    def __init__(s, path_to_db, software, user):
        Borg.__init__(s)
        s.active = True
        s.db = db.DB(path_to_db)
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

if __name__ == '__main__':
    import test
    import os
    import time
    import pprint
    with test.temp(".db") as tmp:
        os.unlink(tmp)
        mon = Monitor(tmp, "python", "ME!")
        mon.interval = 1 # speed interval to one second
        mon.note = "HI THERE"
        mon.path = "path/to/file"
        mon.start()
        time.sleep(3)
        pprint.pprint(list(mon.db.read_all()))
        mon.stop()
