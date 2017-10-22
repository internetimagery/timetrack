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
        similar = list(s.db.struct.keys())[4:]
        with s.db:
            for row in s.db.read("status != ? AND checkin BETWEEN ? AND ?", "idle", from_, to_):
                try:
                    last = result[row["session"]][-1]
                    if row["checkin"] < last["checkout"]: # Early checkin
                        last["checkout"] = row["checkin"]
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

    def rearrange(s, primary, data):
        """ Rearrange times to match new keys. Helping to visualize better. """
        blacklist = set(list(s.db.struct.keys())[:4]) | set(["checkin", "checkout", "time", "period"])
        result = {}
        for session in data:
            for row in data[session]:
                try:
                    d = result[row[primary]]
                    d["time"] += row["checkout"] - row["checkin"]
                    d["session"].add(session)
                    for k in row:
                        if k not in blacklist:
                            d[k].add(row[k])
                except KeyError:
                    d = {k: set([v]) for k, v in row.items() if k not in blacklist}
                    d["time"] = row["checkout"] - row["checkin"]
                    d["session"] = set([session])
                    result[row[primary]] = d
        return result

    def view_note(s, column, past=0):
        """ View notes. TEMPORARY FUNCTION for very specific display. """
        title = "{} weeks ago.".format(past) if past else "Current week."

        current_stamps = collections.OrderedDict((k, (v[0] - timestamp.WEEK * past, v[1] - timestamp.WEEK * past)) for k, v in timestamp.week("sunday").items())

        ord_current_stamps = collections.OrderedDict((k, s.rearrange(column, s.query(*v))) for k, v in current_stamps.items())

        curr_data = assets.Plotly(ord_current_stamps)
        curr_table = assets.Table(ord_current_stamps)

        ass = assets.Assets()
        ass.view(
            title=title,
            plot1=curr_data,
            table=curr_table,
            comp=timestamp.datetime.datetime.now().strftime("Created on %a %m %Y %M:%S")
            )

if __name__ == '__main__':
    import os
    import test
    import time
    from pprint import pprint
    with test.temp() as tmp:
        os.unlink(tmp)
        tmp_db = db.DB(tmp)
        tmp_db.poll(1, "me", "python", "path/to/file", "active", "first entry")
        tmp_db.poll(1, "you", "python", "path/to/file", "idle", "second entry")
        tmp_db.poll(1, "us", "python", "path/to/file", "active", "third entry")
        tmp_db.poll(1, "us", "python", "path/to/file", "active", "third entry")
        disp = Display(tmp)
        # res = disp.query(time.time() - 10.0, time.time() + 10.0)
        # pprint(res)
        # pprint(disp.rearrange("note", res))
        # pprint(disp.parse_note(time.time() - 10.0, time.time() + 10.0))

        # for session in res:
        #     assert len(res[session]) == 2
            # pprint.pprint(res[session])
        disp.view_note()
