# Date utilities
from __future__ import print_function, division
import time
import datetime
import calendar
import collections

# Helpers to work with times in seconds
SECOND = 1.0
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7
WORK_WEEK = DAY * 5
YEAR = DAY * 365

# def current_week(start_day="monday"):
#     """ Output a week of datetimes """
#     today = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
#     weekday = today.weekday()
#     week = list(calendar.Calendar(getattr(calendar, start_day.upper())).iterweekdays())
#     pos = week.index(weekday)
#     return (today - datetime.timedelta(days=pos - i) for i, d in enumerate(week))

def week(start_day="monday"):
    """ Output a week of timestamps """
    today = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
    weekday = today.weekday()
    week = list(calendar.Calendar(getattr(calendar, start_day.upper())).iterweekdays())
    pos = week.index(weekday)
    week_stamp = ((today - datetime.timedelta(days=pos - i)).timestamp() for i, d in enumerate(week))
    return collections.OrderedDict(((calendar.day_name[a], (b, b + DAY)) for a, b in zip(week, week_stamp)))

def now():
    """ Current time as float timestamp """
    return time.time()

def format(timestamp):
    """ Convert to HH:MM """
    hours = timestamp / HOUR
    minutes = (timestamp % HOUR) / MINUTE
    return "{}:{} Hours:Minutes".format(int(hours), str(int(minutes)).zfill(2))
