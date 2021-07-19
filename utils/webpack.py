import json

from functools import lru_cache

from django.conf import settings
from django.contrib.staticfiles.finders import find as find_static_file
from django.core.exceptions import ImproperlyConfigured, SuspiciousFileOperation


def get_mapping(path):
    """
    Returns the asset mapping on the given path.
    """

    try:
        filepath = find_static_file(path) or path
    except SuspiciousFileOperation:
        raise ImproperlyConfigured(
            'Your WebPack assets map file is configured with an absolute path. '
            'Please move it into a static directory and use a relative path.'
        )

    try:
        with open(filepath, 'r') as fp:
            return json.load(fp)
    except FileNotFoundError:
        if settings.DEBUG:
            raise ImproperlyConfigured(f'{filepath} not found. Please generate assets with WebPack.')

        return {}


if not settings.DEBUG:
    get_mapping = lru_cache(maxsize=None)(get_mapping)


def get_asset(name, path=None):
    """
    Returns the asset path for a given asset name.
    """

    return get_mapping(path or getattr(settings, 'WEBPACK_ASSETS_MAP_PATH', None) or 'assets.map.json').get(f'{name}')
