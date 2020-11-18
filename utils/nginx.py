from __future__ import annotations

import os
import posixpath

from functools import lru_cache
from typing import Type, Union

from django.conf import settings
from django.http import HttpResponse, FileResponse


class XAccelRedirect(HttpResponse):
    root: str
    location: str

    def __init__(self, filepath, *, as_attachment=False, filename=None, content_type=''):
        filename = filename or os.path.basename(filepath)

        super(XAccelRedirect, self).__init__(content_type=content_type)

        self['X-Accel-Redirect'] = self.get_url(filepath)

        if as_attachment:
            self['Content-Disposition'] = f'attachment; filename="{filename}"'
        else:
            self['Content-Disposition'] = 'inline'

    @classmethod
    def get_url(cls, filepath):
        relative = os.path.relpath(filepath, cls.root)
        segments = relative.split(os.path.sep)

        return posixpath.join(cls.location, *segments)

    @classmethod
    @lru_cache(maxsize=None)
    def get_subclass(cls, prefix, root, location) -> Type[XAccelRedirect]:
        # noinspection PyTypeChecker
        return type(f'{prefix}{cls.__name__}', (cls,), {'root': root, 'location': location})


class DjangoFileResponse(FileResponse):

    def __init__(self, filepath, **kwargs):
        fh = open(filepath, 'rb')

        super(DjangoFileResponse, self).__init__(fh, **kwargs)


ResponseType = Union[
    Type[XAccelRedirect],
    Type[DjangoFileResponse],
]


def get_response_class(name, root=None, location='/') -> ResponseType:
    if settings.DEBUG:  # pragma: no cover
        return DjangoFileResponse

    return XAccelRedirect.get_subclass(name, root or settings.BASE_DIR, location)
