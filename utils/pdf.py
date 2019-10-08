import mimetypes
import posixpath

from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import render_to_string
from django.utils.lru_cache import lru_cache

from weasyprint import HTML, CSS, default_url_fetcher


EMPTY = ''


def get_name(url, empty=EMPTY):
    return url.replace(staticfiles_storage.base_url, empty)


def get_filepath(name):
    url = staticfiles_storage.url(name)
    name = get_name(url)

    return finders.find(name)


def get_url_description(url):
    result = urlsplit(url)
    name = get_name(result.path)
    filepath = get_filepath(name)
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
    if url.startswith(settings.BASE_URL):
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