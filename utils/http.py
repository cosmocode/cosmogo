from calendar import timegm
from typing import Optional

from django.http import HttpResponseBase

from .filepath import FilePath, last_modified as get_last_modified

try:
    from django.utils.http import content_disposition_header as get_content_disposition_header
except ImportError:
    def get_content_disposition_header(as_attachment, filename):
        disposition = 'attachment' if as_attachment else 'inline'

        if filename:
            return f'{disposition}; filename="{filename}"'
        elif as_attachment:
            return disposition


def last_modified(filepath: FilePath) -> Optional[int]:
    if timestamp := get_last_modified(filepath):
        return timegm(timestamp.utctimetuple())


def add_content_disposition_header(response: HttpResponseBase, filename: str = None,
                                   as_attachment: bool = True) -> Optional[str]:
    if header := get_content_disposition_header(as_attachment, filename):
        response['Content-Disposition'] = header

    return header
