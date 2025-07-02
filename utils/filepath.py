import datetime
import os

from pathlib import PurePath
from typing import Optional, Union

from django.utils import timezone

try:
    UTC = datetime.timezone.utc
except AttributeError:
    UTC = timezone.utc


FilePath = Union[PurePath, str]
Delta = Union[int, datetime.timedelta]


def last_modified(filepath: FilePath) -> Optional[datetime.datetime]:
    """
    Returns the last modified of the given filepath converted to an aware datetime.
    """

    return get_timestamp(filepath)


def get_timestamp(filepath: FilePath, *, accessor=os.path.getmtime) -> Optional[datetime.datetime]:
    """
    Calls the given accessor function on the filepath and returns an aware datetime if available.
    """

    try:
        timestamp = accessor(filepath)
    except FileNotFoundError:
        return None

    naive = datetime.datetime.utcfromtimestamp(timestamp)

    return naive.replace(tzinfo=UTC)


def is_outdated(filepath: FilePath, delta: Delta) -> bool:
    """
    Returns whether the file at the given path has been modified since
    the given delta. Returns true when the file does not exist.
    """

    timestamp = last_modified(filepath)

    if timestamp is None:
        return True

    if isinstance(delta, int):
        delta = datetime.timedelta(seconds=delta)

    now = timezone.localtime(timezone=UTC)

    return timestamp < now - delta
