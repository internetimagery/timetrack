# Keep track of activity in maya.
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
        s.db = db.DB(path_to_db)
        s.poll_interval = db.MINUTE * 5
        s.last_active = time.time()
        s.notes = ""
        s.software = software
        s.user = user
        s.path = ""

    def start(s):
        """ Begin polling """
        threading.Thread(target=s.poll).start()

    def poll(s):
        """ Update DB with activity """
        while True:
            last_active = (time.time() - s.last_active) <= s.poll_interval
            s.db.poll(s.user, s.software, s.path, "active" if last_active else "idle", s.notes
            time.sleep(s.poll_interval)

    def checkin(s):
        """ Check in to show activity with software """
        s.last_active = time.time()
