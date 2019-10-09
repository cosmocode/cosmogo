import mimetypes
import posixpath

from urllib.parse import urlsplit, urlparse

from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.files.storage import default_storage
from django.template.loader import render_to_string
from django.utils.lru_cache import lru_cache

from weasyprint import HTML, CSS, default_url_fetcher


EMPTY = ''


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
    if name.startswith(settings.STATIC_URL):
        # we let the staticfiles_storage create the final url
        # this makes sure urls that need to be processed by the
        # storage first (e.g. adding a hash) still work properly
        name = name.replace(staticfiles_storage.base_url, EMPTY)
        url = staticfiles_storage.url(name)

        name = url.replace(staticfiles_storage.base_url, EMPTY)
        return finders.find(name)

    if name.startswith(settings.MEDIA_URL):
        name = name.replace(default_storage.base_url, EMPTY)
        return default_storage.path(name)

    raise ValueError(
        f'The relative URL {name} does not point to a location beginning '
        f'with {settings.STATIC_URL} or {settings.MEDIA_URL}.'
    )


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
