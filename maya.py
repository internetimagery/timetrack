# Track for idle cues in maya.
import getpass
import activity
import traceback
import maya.cmds as cmds

class Maya(object):
    def __init__(s, db_path):
        s.monitor = activity.Monitor(db_path, "maya", getpass.getuser())

    def start(s):
        """ Get running! """
        cmds.scriptJob(e=("SelectionChanged", s.poll))
        cmds.scriptJob(e=("timeChanged", s.poll))
        cmds.scriptJob(e=("ToolChanged", s.poll))
        s.monitor.start()

    def note(s, note):
        """ Set / Change note """
        s.monitor.note = note

    def poll(s):
        """ Record activity state """
        try:
            s.monitor.path = cmds.file(q=True, sn=True)
            s.monitor.checkin()
    except Exception as err:
            traceback.print_exc()
            raise err
