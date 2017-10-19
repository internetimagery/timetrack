# Query and present data in a nice format.
from __future__ import print_function
import db
import assets
import datetime
import collections

# datetime.date.fromtimestamp(time.time())

class Display(object):
    """ Load and display timesheet data in a nice format """
    def __init__(s, db_path):
        s.db = db.DB(db_path)
        s.assets = assets.Assets()

    def query(s, from_, to_):
        """ Query active entries betweem date amd date. Break into parts whenever data changes. """
        result = collections.defaultdict(list)
        similar = s.db.struct.keys()[4:]
        with s.db:
            for row in s.db.read("status = ? AND checkin BETWEEN ? AND ?", "active", from_, to_):
                try:
                    last = result[row["session"]][-1]
                    for key in similar:
                        if row[key] != last[key]:
                            break
                    else:
                        last["end"] = row["checkin"] + row["period"]
                        continue
                except IndexError:
                    pass
                res = {k: row[k] for k in similar}
                res["start"] = row["checkin"]
                res["end"] = row["checkin"] + row["period"]
                result[row["session"]].append(res)
            return result            

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
