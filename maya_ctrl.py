# Track for idle cues in maya.
from __future__ import print_function
import time
import getpass
import activity
import traceback
import functools
import threading
import maya.cmds as cmds
import maya.utils as utils

class Monitor(activity.Monitor):
    def __init__(s):
        activity.Monitor.__init__(s, "maya", getpass.getuser())
        s.checkin()

    def start(s):
        """ Get running! """
        activity.Monitor.start(s)
        cmds.scriptJob(e=("SelectionChanged", s.checkin))
        cmds.scriptJob(e=("timeChanged", s.checkin))
        cmds.scriptJob(e=("ToolChanged", s.checkin))
        s.idle_job = functools.partial(cmds.scriptJob, ie=s.idle_callback, ro=True)
        s.sem = threading.BoundedSemaphore(1)
        s.idle = False
        threading.Thread(target=s.idle_loop).start()

    def idle_loop(s):
        """ Loop and watch idle states """
        while s.active:
            if not s.idle:
                utils.executeDeferred(s.checkin)
            s.idle = False
            s.sem.acquire()
            utils.executeDeferred(s.idle_job)
            time.sleep(0.1)

    def idle_callback(s):
        """ Respond to idle check """
        s.idle = True
        s.sem.release()

    def checkin(s):
        """ Record activity state """
        try:
            print("ACTIVE!")
            s.set_path(cmds.file(q=True, sn=True) or "")
            activity.Monitor.checkin(s)
        except Exception as err:
            traceback.print_exc()
            raise err

if __name__ == '__main__':
    import test
    import os
    import time
    with test.temp(".db") as tmp:
        os.unlink(tmp)
        maya = Monitor(tmp)
        maya.interval = 1 # speed interval to one second
        maya.set_note("Hello")
        print("Polling please wait...")
        maya.start()
        time.sleep(3)
        maya.stop()
        res = list(maya.db.read_all())
        assert len(res) == 3
        assert res[0]["note"] == "HI THERE"
