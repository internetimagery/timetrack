# Date utilities
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
mon_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
sun_week = mon_week[6:] + mon_week[:6]
work_week = mon_week[:5]

def timestamp():
    """ Current time as float timestamp """
    return time.time()

def current():
    """ Current time in datetime """
    return datetime.datetime.now()

print work_week
