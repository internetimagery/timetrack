# Date utilities
from __future__ import print_function, division
import time
import datetime
import calendar
import collections

# Helpers to work with times
SECOND = 1.0
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7
WORK_WEEK = DAY * 5
YEAR = DAY * 365

def week_timestamp(start_day="monday"):
    """ Output a week of timestamps """
    today = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
    weekday = today.weekday()
    week = list(calendar.Calendar(getattr(calendar, start_day.upper())).iterweekdays())
    pos = week.index(weekday)
    week_data = (today - datetime.timedelta(days=pos - i) for i, d in enumerate(week))
    return collections.OrderedDict([(calendar.day_name[a], (b.timestamp(), b.timestamp() + HOUR * 24)) for a, b in zip(week, week_data)])

# Helpers for weeks
mon_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
sun_week = mon_week[6:] + mon_week[:6]
work_week = mon_week[:5]


# import calendar
# print([a for a in calendar.Calendar(calendar.SUNDAY).iterweekdays()])

def current_week_mon():
    """ Week up to point, mon start """
    return current_week(mon_week)

def current_week_sun():
    """ Week up to point, sun start """
    return current_week(sun_week)

def current_week_work():
    """ Week up to point, work start """
    try:
        return current_week(work_week)
    except ValueError:
        return current_week(mon_week)

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

print(week_timestamp("wednesday"))
# import datetime
# import pprint
#
# today = datetime.date(2017, 10, 20)
# dates = [today + datetime.timedelta(days=i) for i in range(0 - today.weekday(), 7 - today.weekday())]
# pprint.pprint(dates)
