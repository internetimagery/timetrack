# Track for idle cues in maya.
from __future__ import print_function
import getpass
import activity
import traceback
import maya.cmds as cmds

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

    def checkin(s):
        """ Record activity state """
        try:
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
