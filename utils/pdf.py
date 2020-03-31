import mimetypes
import posixpath

from functools import lru_cache
from urllib.parse import urlsplit, urlparse

from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.files.storage import default_storage
from django.template.loader import render_to_string

EMPTY = ''

try:
    from weasyprint import HTML, CSS, default_url_fetcher
except ImportError:
    if not settings.DEBUG:
        # make sure missing WeasyPrint installation is
        # noticed early in production environments
        raise

    # WeasyPrint has a lot of requirements so
    # it's okay to not have it in development
    HTML = CSS = default_url_fetcher = None


def is_local(url):
    parsed = urlparse(url)

    if parsed.netloc:
        # we treat a network location that points to us as local
        return url.startswith(settings.BASE_URL)

    if parsed.scheme and parsed.scheme not in ['http', 'https']:
        # exclude e.g. "data:" and "file:" URIs
        return False

    return True


def get_filepath(name):
    if name.startswith(settings.MEDIA_URL):
        name = get_name(name, default_storage)

        return default_storage.path(name)

    # if it's not a media url we assume it is a static file

    # we let the staticfiles_storage create the final url
    # this makes sure urls that need to be processed by the
    # storage first (e.g. adding a hash) still work properly
    name = get_name(name)
    url = staticfiles_storage.url(name)
    name = get_name(url)

    return finders.find(name)


def get_name(url, storage=None, empty=EMPTY):
    storage = storage or staticfiles_storage

    return url.replace(storage.base_url, empty)


def get_url_description(url):
    result = urlsplit(url)
    filepath = get_filepath(result.path)
    filename = posixpath.basename(filepath)
    mime_type, encoding = mimetypes.guess_type(filepath)

    return filepath, dict(
        mime_type=mime_type,
        encoding=encoding,
        filename=filename,
    )


if not settings.DEBUG:
    get_filepath = lru_cache(maxsize=None)(get_filepath)
    get_url_description = lru_cache(maxsize=None)(get_url_description)


def url_fetcher(url):
    if is_local(url):
        filepath, description = get_url_description(url)
        file_obj = open(filepath, 'rb')

        return dict(description, file_obj=file_obj)

    return default_url_fetcher(url)


def render(template, context, style=None, request=None, target=None, **options):
    assert HTML and CSS, 'WeasyPrint is not installed. You cannot use any print features.'

    options.setdefault('base_url', settings.BASE_URL)
    options.setdefault('url_fetcher', url_fetcher)

    document = HTML(string=render_to_string(template, context, request=request), **options)

    if style:
        stylesheets = [CSS(filename=get_filepath(style), **options)]
    else:
        stylesheets = None

    if target is False:
        return document.render(stylesheets=stylesheets)

    return document.write_pdf(target=target, stylesheets=stylesheets)
