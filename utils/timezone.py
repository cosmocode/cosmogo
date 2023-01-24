import calendar
import datetime

from django.utils import timezone


def create(year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0, tz=None):
    value = datetime.datetime(year, month, day, hour, minute, second, microsecond)

    return timezone.make_aware(value, timezone=tz)


def timestamp(value: datetime.datetime) -> float:
    """
    Helper to convert a datetime to a unix timestamp.
    """

    value = timezone.localtime(value, timezone=timezone.utc)
    timetuple = value.utctimetuple()

    return calendar.timegm(timetuple)
