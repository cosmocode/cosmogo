import calendar
import datetime

from django.utils import timezone


def timestamp(value: datetime.datetime) -> float:
    """
    Helper to convert a datetime to a unix timestamp.
    """

    value = timezone.localtime(value, timezone=timezone.utc)
    timetuple = value.utctimetuple()

    return calendar.timegm(timetuple)
