import time
import json
from datetime import datetime, timedelta

from typing import List, Dict, Tuple


def wait_for_input(wait: bool = True):
    if wait:
        cmd = input("please press enter to continue ... ")


def date_string(dt: datetime = None, fmt: str = "%Y%m%d") -> str:
    if dt is None:
        return datetime.now().strftime(fmt)
    else:
        return dt.strftime(fmt)


def time_string(dt: datetime = None, fmt: str = "%H:%M:%S") -> str:
    if dt is None:
        return datetime.now().strftime(fmt)
    else:
        return dt.strftime(fmt)


def datetime_string(dt: datetime = None, fmt: str = "%Y-%m-%d %H:%M:%S.%f") -> str:
    """
    :param fmt: "%Y-%m-%d %H:%M:%S.%f"
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime(fmt)


def date_time_string(ts: int, date_fmt: str = "%Y%m%d", time_fmt: str = "%H:%M:%S") -> Tuple[str, str]:
    dt = datetime.fromtimestamp(ts)
    return date_string(dt), time_string(dt)


def simple_datetime_string(date: str, time: str) -> str:
    return f"{date[0:4]}-{date[4:6]}-{date[6:8]} {time}"


def today() -> str:
    return date_string()


def current_time(fmt: str = '%Y%m%d %H:%M:%S') -> str:
    return datetime_string(fmt=fmt)


def date_before_days(end: str, days: int) -> str:
    end_date = get_datetime(end, "%Y%m%d")
    start_date = end_date - timedelta(days=days)
    return datetime_string(start_date, "%Y%m%d")


def date_after_days(start: str, days: int) -> str:
    start_date = get_datetime(start, "%Y%m%d")
    end_date = start_date + timedelta(days=days)
    return datetime_string(end_date, "%Y%m%d")


def date_before_hours(end: str, hours: int) -> str:
    end_date = get_datetime(end, "%Y%m%d")
    start_date = end_date - timedelta(hours=hours)
    return datetime_string(start_date, "%Y%m%d")


def date_after_hours(start: str, hours: int) -> str:
    start_date = get_datetime(start, "%Y%m%d")
    end_date = start_date + timedelta(hours=hours)
    return datetime_string(end_date, "%Y%m%d")


def time_before_hours(start: str, hours: int) -> str:
    start_time = get_datetime(start, "%H:%M:%S")
    end_time = start_time - timedelta(hours=hours)
    return datetime_string(end_time, "%H:%M:%S")


def time_before_minutes(start: str, minutes: int) -> str:
    start_time = get_datetime(start, "%H:%M:%S")
    end_time = start_time - timedelta(minutes=minutes)
    return datetime_string(end_time, "%H:%M:%S")


def time_before_seconds(start: str, seconds: int) -> str:
    start_time = get_datetime(start, "%H:%M:%S")
    end_time = start_time - timedelta(seconds=seconds)
    return datetime_string(end_time, "%H:%M:%S")


def time_after_hours(start: str, hours: int) -> str:
    start_time = get_datetime(start, "%H:%M:%S")
    end_time = start_time + timedelta(hours=hours)
    return datetime_string(end_time, "%H:%M:%S")


def time_after_minutes(start: str, minutes: int) -> str:
    start_time = get_datetime(start, "%H:%M:%S")
    end_time = start_time + timedelta(minutes=minutes)
    return datetime_string(end_time, "%H:%M:%S")


def time_after_seconds(start: str, seconds: int) -> str:
    start_time = get_datetime(start, "%H:%M:%S")
    end_time = start_time + timedelta(seconds=seconds)
    return datetime_string(end_time, "%H:%M:%S")


def get_datetime(datetime_str: str, fmt: str = "%Y%m%d %H:%M:%S") -> datetime:
    return datetime.strptime(datetime_str, fmt)


def datetime_after_hours(datetime_str: str, hours: int,
                         fmt: str = "%Y%m%d %H:%M:%S") -> datetime:
    return get_datetime(datetime_str, fmt) + timedelta(hours=hours)


def datetime_after_minutes(datetime_str: str, minutes: int,
                           fmt: str = "%Y%m%d %H:%M:%S") -> datetime:
    return get_datetime(datetime_str, fmt) + timedelta(minutes=minutes)


def datetime_after_seconds(datetime_str: str, seconds: int,
                           fmt: str = "%Y%m%d %H:%M:%S") -> datetime:
    return get_datetime(datetime_str, fmt) + timedelta(seconds=seconds)


def check_date(date_string: str) -> bool:
    if date_string.isdigit() == False or len(date_string) != 8:
        return False
    try:
        datetime.strptime(date_string, '%Y%m%d')
    except Exception as e:
        return False
    return True


def check_time(time_string: str) -> bool:
    if len(time_string) != 8:
        return False
    try:
        datetime.strptime(time_string, '%H:%M:%S')
    except Exception as e:
        return False
    return True


def json_string(object) -> str:
    return json.dumps(dict(object), ensure_ascii=False, separators=(',', ':'))
