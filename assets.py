# Load assets and do things with them.
from __future__ import print_function

import webbrowser
import os.path
import json
import timestamp
import os
import re

ASSET_ROOT = os.path.join(os.path.dirname(__file__), "assets")
TMP_TIMESHEET = os.path.expanduser("~/timesheet.tmp.html")


# plot = [
#   {
#     "x": ["monday", "tuesday", "wednesday"],
#     "y": [8, 7, 2],
#     "type": "bar",
#     "name": "shot1",
#     "text": ["extra information","more info","some info about shot"]
#   },
#   {
#     "x": ["monday", "tuesday", "wednesday"],
#     "y": [2, 3, 5],
#     "type": "bar",
#     "name": "shot2",
#     "text": ["I have info for you...","stuff to say","info here"]
#   },
#    {
#      "x": ["monday", "tuesday", "wednesday"],
#      "y": [5, 4, 2],
#      "type": "bar",
#      "name": "shot3",
#      "text": ["Maybe filepath here","things","ok nice"]
#    }
# ]
# plot = json.dumps(plot)

# { "shotname":
#     { "day": {
#         "hours": 6,
#         "note": 4
#         }
#     }
# }

def Plotly(data):
    """ Parse {day: {shot: {time: 1, note:'txt'}}} """
    result = {}
    for day in data:
        for shot in data[day]:
            try:
                result[shot]["x"].append(day)
                result[shot]["y"].append(data[day][shot]["time"] / timestamp.HOUR)
                result[shot]["text"].append(timestamp.format(data[day][shot]["time"]))
            except KeyError:
                print("shot", shot)
                result[shot] = {
                    "x": [day],
                    "y": [data[day][shot]["time"] / timestamp.HOUR],
                    "type": "bar",
                    "text": [timestamp.format(data[day][shot]["time"])],
                    "name": shot}
    # for shot in result:
    #     result[shot]["text"] = "\n".join(result[shot]["text"])
    return json.dumps([result[a] for a in result])

class Assets(object):
    """ Manage assets for presentation """
    def __init__(s):
        # Load our assets in
        s.assets = {}
        for root, dirs, files in os.walk(ASSET_ROOT):
            rel_root = os.path.relpath(root, ASSET_ROOT)
            for f in files:
                with open(os.path.join(root, f), "r") as data:
                    s.assets[os.path.normpath(os.path.join(rel_root, f)).replace("\\", "/")] = data.read()

    def compile(s, **kwargs):
        """ Build our page with all our assets combined """
        index = s.assets["index.html"]

        for m in reversed(tuple(re.finditer(r"{{(?P<action>\w+)\s+(?P<var>[\w_-]+)}}", index))):
            act = m.group("action")
            if act == "replace":
                index = index[:m.start(0)] + kwargs.get(m.group("var"), "") + index[m.end(0):]

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

    def view(s, **kwargs):
        """ View timesheet with up to date information. """
        with open(TMP_TIMESHEET, "w") as f:
            f.write(s.compile(**kwargs))
            webbrowser.open("file://{}".format(TMP_TIMESHEET))

if __name__ == '__main__':
    a = Assets()
    # print(a.compile())
    a.view()
