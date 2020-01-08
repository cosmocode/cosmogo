import json

from django.conf import settings

try:
    from django.utils.lru_cache import lru_cache
except ImportError:
    from functools import lru_cache

KEY = 'assetsByChunkName'


def get_assets(path, key=KEY, **kwargs):
    """
    Returns a dictionary of chunks and their assets
    from the given webpack stats file path.
    """

    try:
        with open(path, 'r') as fp:
            data = json.load(fp, **kwargs)
    except (IOError, ValueError):
        if settings.DEBUG:
            raise IOError('%s not found. Please generate assets with webpack.' % path)

        return {}

    return data.get(key) or {}


if not settings.DEBUG:
    get_assets = lru_cache(maxsize=None)(get_assets)


def get_asset(name, extension, path=None):
    """
    Returns the asset path from a given chunk for the requested file extension.
    """

    assets = get_assets(path=path or settings.WEBPACK_STATS_PATH)
    chunk = assets.get(name)

    if not chunk:
        return None

    elif isinstance(chunk, (tuple, list)):
        for filepath in chunk:
            if filepath.endswith(extension):
                return filepath

    elif chunk.endswith(extension):
        return chunk

    return None
