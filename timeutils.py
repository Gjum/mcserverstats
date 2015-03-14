from datetime import datetime, timedelta
import os
import time

midnight_str = '00:00:00'
date_str_sep = ' '
date_str_fmt = '%Y-%m-%d' + date_str_sep + '%H:%M:%S'

def date_str_to_epoch(date_str, time_str=midnight_str):
    if date_str is None:
        return None
    date_str = ensure_full_date(date_str, time_str)
    epoch = int(time.mktime(time.strptime(date_str, date_str_fmt)))
    return epoch

def epoch_to_date_str(epoch, fmt=date_str_fmt):
    date_str = time.strftime(fmt, time.localtime(epoch))
    return date_str

def ensure_full_date(date_str, time_str=midnight_str):
    if date_str_sep not in date_str:
        date_str += date_str_sep + time_str
    return date_str

def ensure_day_only(date_str):
    """
    `Y-M-D H:M:S` -> `Y-M-D`
    `Y-M-D` -> `Y-M-D`
    `None` -> `None`
    """
    if date_str and date_str_sep in date_str:
        date_str = date_str.split(date_str_sep, 1)[0]
    return date_str

def latest_log_date_str(logs_dir):
    return time.strftime(date_str_fmt, time.localtime(os.path.getmtime(logs_dir + '/latest.log')))

def add_to_date_str(date_str, **kwargs):
    date_str = ensure_full_date(date_str)
    return time.strftime(
        date_str_fmt, (
            datetime.strptime(date_str, date_str_fmt)
            + timedelta(**kwargs)
        ).timetuple()
    )

def human_date_str(date_str):
    """
    `Y-M-D 00:00:00` -> `Y-M-D`
    `Y-M-D HH:MM:SS` -> `Y-M-D HH:MM:SS`
    `None` -> `None`
    """
    if date_str and date_str.endswith(midnight_str):
        date_str = date_str[:-9]
    return date_str

def human_time(seconds):
    return str(timedelta(seconds=seconds))
