# Load assets and do things with them.
from __future__ import print_function

import webbrowser
import os.path
import os
import re

ASSET_ROOT = os.path.join(os.path.dirname(__file__), "assets")
TMP_TIMESHEET = os.path.expanduser("~/timesheet.tmp.html")

class Asset(object):
    """ Manage assets for presentation """
    def __init__(s):
        # Load our assets in
        s.assets = {}
        for root, dirs, files in os.walk(ASSET_ROOT):
            rel_root = os.path.relpath(root, ASSET_ROOT)
            for f in files:
                with open(os.path.join(root, f), "r") as data:
                    s.assets[os.path.normpath(os.path.join(rel_root, f)).replace("\\", "/")] = data.read()

    def compile(s, title="TITLE"):
        """ Build our page with all our assets combined """
        index = s.assets["index.html"]

        for m in reversed(tuple(re.finditer(r"<\s*(?P<tag>\w+).+?(?P<quote>'|\")(?P<asset>[-_\w\s\./]+\.\w+)(?P=quote).+", index))):
            tag = m.group("tag")
            if tag == "link": # CSS sheet
                index = index.replace(m.group(0), "<style media=\"screen\">\n{}</style>".format(s.assets[m.group("asset")]))
            if tag == "script": # Javascript
                index = index.replace(m.group(0), "<script type=\"text/javascript\">\n{}</script>".format(s.assets[m.group("asset")]))

        return index

    def view(s):
        """ View timesheet with up to date information. """
        with open(TMP_TIMESHEET, "w") as f:
            f.write(s.compile())
            webbrowser.open("file://{}".format(TMP_TIMESHEET))

if __name__ == '__main__':
    a = Asset()
    a.view()
