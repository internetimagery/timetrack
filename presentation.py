# Query and present data in a nice format.
from __future__ import print_function
import db
import assets
import timestamp
import collections



class Display(object):
    """ Load and display timesheet data in a nice format """
    def __init__(s, db_path):
        s.db = db.DB(db_path)
        s.assets = assets.Assets()

    def query(s, from_, to_, grace=timestamp.MINUTE * 11.0):
        """ Query active entries betweem date amd date. Break into parts whenever data changes. """
        result = collections.defaultdict(list)
        similar = s.db.struct.keys()[4:]
        with s.db:
            for row in s.db.read("status != ? AND checkin BETWEEN ? AND ?", "idle", from_, to_):
                try:
                    last = result[row["session"]][-1]
                    if row["checkin"] < last["checkout"] + grace: # Check we haven't skipped a beat
                        for key in similar:
                            if row[key] != last[key]:
                                break
                        else:
                            last["checkout"] = row["checkin"] + row["period"]
                            last["period"] = row["period"]
                            continue
                except IndexError:
                    pass

                res = {k: row[k] for k in similar}
                res["period"] = row["period"]
                res["checkin"] = row["checkin"]
                res["checkout"] = row["checkin"] + row["period"]
                result[row["session"]].append(res)
            return result

    def parse_note(s, from_, to_):
        """ Query DB, format and parse out favouring notes """
        data = s.query(from_, to_)
        result = {}
        for k in data:
            for row in data[k]:
                try:
                    d = result[row["note"]]
                    d["time"] += row["checkout"] - row["checkin"]
                    d["files"].add(row["file"])
                except KeyError:
                    result[row["note"]] = {
                        "time" : row["checkout"] - row["checkin"],
                        "files" : set([row["file"]]),
                        "software": row["software"],
                        "user": row["user"]}
        return result

    def view_note(s):
        """ View notes """
        # TEMPORARY FUNCTION FOR TESTING
        data = assets.Plotly({"This is a test!!!": s.parse_note(timestamp.now() - 99999, timestamp.now())})
        ass = assets.Assets()
        ass.view(title="TEST PLOT!", plot=data)

if __name__ == '__main__':
    import os
    import test
    import time
    import pprint
    with test.temp() as tmp:
        os.unlink(tmp)
        tmp_db = db.DB(tmp)
        tmp_db.poll(1, "me", "python", "path/to/file", "active", "first entry")
        tmp_db.poll(1, "you", "python", "path/to/file", "idle", "second entry")
        tmp_db.poll(1, "us", "python", "path/to/file", "active", "third entry")
        tmp_db.poll(1, "us", "python", "path/to/file", "active", "third entry")
        disp = Display(tmp)
        res = disp.query(time.time() - 10.0, time.time() + 10., ["note"])
        for session in res:
            assert len(res[session]) == 2
            # pprint.pprint(res[session])
