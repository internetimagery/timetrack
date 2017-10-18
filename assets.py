# Load assets and do things with them.
from __future__ import print_function

import webbrowser
import os.path
import json
import os
import re

ASSET_ROOT = os.path.join(os.path.dirname(__file__), "assets")
TMP_TIMESHEET = os.path.expanduser("~/timesheet.tmp.html")


plot = [
  {
    "x": ["monday", "tuesday", "wednesday"],
    "y": [8, 7, 2],
    "type": "bar",
    "name": "shot1",
    "text": ["extra information","more info","some info about shot"]
  },
  {
    "x": ["monday", "tuesday", "wednesday"],
    "y": [2, 3, 5],
    "type": "bar",
    "name": "shot2",
    "text": ["I have info for you...","stuff to say","info here"]
  },
   {
     "x": ["monday", "tuesday", "wednesday"],
     "y": [5, 4, 2],
     "type": "bar",
     "name": "shot3",
     "text": ["Maybe filepath here","things","ok nice"]
   }
]
plot = json.dumps(plot)


class Asset(object):
    """ Manage assets for presentation """
    def __init__(s):
        # Load our assets in
        s.assets = {}
        s.vars = {}
        for root, dirs, files in os.walk(ASSET_ROOT):
            rel_root = os.path.relpath(root, ASSET_ROOT)
            for f in files:
                with open(os.path.join(root, f), "r") as data:
                    s.assets[os.path.normpath(os.path.join(rel_root, f)).replace("\\", "/")] = data.read()

    def compile(s, title="TITLE"):
        """ Build our page with all our assets combined """
        index = s.assets["index.html"]
        s.vars["title"] = "MY TITLE!"
        s.vars["plot"] = plot

        for m in reversed(tuple(re.finditer(r"{{(?P<action>\w+)\s+(?P<var>[\w_-]+)}}", index))):
            act = m.group("action")
            if act == "replace":
                index = index[:m.start(0)] + s.vars.get(m.group("var"), "") + index[m.end(0):]

        for m in reversed(tuple(re.finditer(r"<\s*(?P<tag>\w+).+?(?P<quote>'|\")(?P<asset>[-_\w\s\./]+\.\w+)(?P=quote).+", index))):
            tag = m.group("tag")
            if tag == "link": # CSS sheet
                repl = "<style media=\"screen\">\n{}</style>".format(s.assets[m.group("asset")])
            elif tag == "script":
                repl = "<script type=\"text/javascript\">\n{}</script>".format(s.assets[m.group("asset")])
            else:
                repl = m.group(0)
            index = index[:m.start(0)] + repl + index[m.end(0):]
        return index

    def view(s):
        """ View timesheet with up to date information. """
        with open(TMP_TIMESHEET, "w") as f:
            f.write(s.compile())
            webbrowser.open("file://{}".format(TMP_TIMESHEET))

if __name__ == '__main__':
    a = Asset()
    # print(a.compile())
    a.view()
