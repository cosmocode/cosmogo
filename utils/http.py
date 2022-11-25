from calendar import timegm
from typing import Optional

from .filepath import FilePath, last_modified as get_last_modified


def last_modified(filepath: FilePath) -> Optional[int]:
    if timestamp := get_last_modified(filepath):
        return timegm(timestamp.utctimetuple())
