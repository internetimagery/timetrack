# Date utilities
from __future__ import print_function, division
import time
import datetime

# Helpers to work with times
SECOND = 1.0
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7
WORK_WEEK = DAY * 5
YEAR = DAY * 365

# Helpers for weeks
mon_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
sun_week = mon_week[6:] + mon_week[:6]
work_week = mon_week[:5]

def current_week_mon():
    """ Week up to point, mon start """
    return current_week(mon_week)

def current_week_sun():
    """ Week up to point, sun start """
    return current_week(sun_week)

def current_week(week):
    """ Week up to this point """
    curr = current_day()
    pos = week.index(curr.strftime("%A"))
    return [curr - datetime.timedelta(days=a) for a in range(pos + 1)][::-1]

def current_day():
    """ Get current day """
    curr = current() # Current time.
    return curr - datetime.timedelta(
        hours=curr.hour,
        minutes=curr.minute,
        seconds=curr.second,
        microseconds=curr.microsecond)

def timestamp():
    """ Current time as float timestamp """
    return time.time()

def current():
    """ Current time in datetime """
    return datetime.datetime.now()

def to_time(timestamp):
    """ Convert to HH:MM """
    hours = timestamp / HOUR
    minutes = (timestamp % HOUR) / MINUTE
    return "{}:{} Hours:Minutes".format(int(hours), str(int(minutes)).zfill(2))

print(current_week(mon_week))
