# Track for idle cues in maya.
from __future__ import print_function
import time
import getpass
import activity
import traceback
import functools
import threading
import presentation
import maya.cmds as cmds
import maya.utils as utils

class Window(object):
    def __init__(s):
        s.mon = Monitor()
        win = cmds.window(t="TimeTrack Monitor")
        cmds.columnLayout(adj=True)
        s.status = cmds.textFieldGrp(l="Status:", ed=False)
        s.note = cmds.textFieldGrp(l="Note:", cc=s.update_note)
        s.active = cmds.checkBoxGrp(l="Start/Stop:", cc=s.toggle)
        cmds.button(l="View Timesheet", c=lambda _: presentation.Display(s.mon.db.path).view_note())
        cmds.showWindow(win)
        s.update()

    def update(s):
        active = s.mon.active
        cmds.textFieldGrp(s.status, e=True, tx="Active" if active else "Idle")
        cmds.checkBoxGrp(s.active, e=True, v1=active)
        cmds.textFieldGrp(s.note, e=True, tx=s.mon.note)

    def toggle(s, value):
        s.mon.start() if value else s.mon.stop()
        s.update()

    def update_note(s, text):
        s.mon.set_note(text)

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
        s.idle_job = functools.partial(cmds.scriptJob, e=("idle", s.idle_callback), ro=True) # Lower priority than "idleEvent"
        s.sem = threading.BoundedSemaphore(1)
        s.idle = False
        threading.Thread(target=s.idle_loop).start()
        threading.Thread(target=s.busy_loop).start()

    def idle_loop(s):
        """ Loop and watch idle states """
        while s.active:
            if not s.idle:
                s.checkin()
            s.idle = False
            s.sem.acquire() # Throttle our requests
            utils.executeDeferred(s.idle_job)
            time.sleep(0.3) # Further throttle our checks. Doesn't catch everything, but catches enough to be reliable.

    def busy_loop(s):
        """ Loop looking for long periods of business. Such as playblasts etc """
        while s.active:
            if not s.idle:
                s.checkin()
            time.sleep(30) # Sleep for a decent length of time.

    def idle_callback(s):
        """ Respond to idle check """
        s.idle = True
        s.set_path(cmds.file(q=True, sn=True) or "")
        s.sem.release()

    def checkin(s):
        """ Record activity state """
        try:
            activity.Monitor.checkin(s)
        except Exception as err:
            utils.executeDeferred(traceback.print_exc)
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
