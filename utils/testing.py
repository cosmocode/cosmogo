import datetime
import random

from contextlib import contextmanager
from typing import Any, Iterable, Mapping, List, Union, Tuple, Type, Optional
from unittest.mock import patch

from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.core.management import call_command as django_call_command
from django.db.models import Model
from django.http import HttpResponse
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from django.utils.formats import get_format
from django.utils.http import urlencode
from django.utils.timezone import make_aware, is_aware

from .tempdir import maketempdir

Data = Union[List[dict], dict]
Args = Union[tuple, list]
QueryParams = Union[Mapping[str, Any], Iterable[Tuple[str, Any]]]


def call_command(*args, **kwargs):
    """
    Silence all output of commands.
    """

    with open('/dev/null', 'w') as devnull:
        defaults = dict(stdout=devnull, stderr=devnull)
        defaults.update(kwargs)

        return django_call_command(*args, **defaults)


def create_user(username: str, *, model=None, **kwargs):
    model = model or apps.get_model(settings.AUTH_USER_MODEL)
    password = kwargs.setdefault('password', 'P4sSW0rD')

    kwargs.setdefault('email', f'{username}@test.case')
    kwargs.setdefault(model.USERNAME_FIELD, username)

    user = model.objects.create_user(**kwargs)

    user.raw_password = password

    return user


def get_url(url: str, args: Args = None, kwargs: dict = None) -> str:
    """
    Helper to reverse the given url name.
    """

    return url if url.startswith('/') else reverse(url, args=args, kwargs=kwargs)


def login(test_case: SimpleTestCase, user=None, password: str = None) -> bool:
    """
    Logs in the user trying to use the raw password or the given password.
    Force logs in the user when no password is found.
    """

    user = user or getattr(test_case, 'user')
    password = password or getattr(user, 'raw_password', password)

    if password is None:
        return test_case.client.force_login(user=user) or True

    return test_case.client.login(username=user.username, password=password)


def get_handler(test_case: SimpleTestCase, method: str = None, data=None):
    if data:
        method = str.lower(method or 'POST')
    else:
        method = str.lower(method or 'GET')

    return getattr(test_case.client, method)


def request(
    test_case: SimpleTestCase,
    url: str,
    status_code: int = None,
    expected_url: str = None,
    args: Args = None,
    kwargs: dict = None,
    headers: dict = None,
    msg: str = None,
    query_params: QueryParams = None,
    method: str = None,
    data: dict = None,
    **options,
) -> HttpResponse:
    """
    A helper to make a request with the test case's http client.

    The given args and kwargs are used to reverse the url
    but not the expected url. When expected url needs
    args/kwargs pass an absolute url instead.

    All additional kwargs are passed as post parameters.
    When posting without parameters just pass post=True.
    """

    data = data or options or None
    handler = get_handler(test_case, method, data)
    url = get_url(url, args, kwargs)

    if query_params:
        url = f'{url}?%s' % urlencode(query_params, doseq=True)

    headers = headers or {}
    status_code = status_code or 200
    response = handler(url, data=data, **headers)
    msg = msg or getattr(response, 'content', None)

    if expected_url:
        test_case.assertRedirects(
            response=response,
            expected_url=get_url(expected_url),
            target_status_code=status_code,
        )
    else:
        test_case.assertEqual(response.status_code, status_code, msg=msg)

    return response


def build_split_datetime_field_data(value: Optional[datetime.datetime], field: str, prefix: str = None) -> dict:
    """
    Methods builds date & time data in a format the `SplitDateTimeWidget` expects it.
    """

    data = {}

    if not value:
        return data

    formats = ('DATE_INPUT_FORMATS', 'TIME_INPUT_FORMATS')
    template = prefix and f'{prefix}-{field}_%d' or f'{field}_%d'

    for index, fmt in enumerate(formats):
        fmts = get_format(fmt)
        fmt = random.choice(fmts)
        bit = value.strftime(fmt)
        data[template % index] = bit

    return data


def build_formset_data(data: Data = None, prefix: str = None, total_forms: int = None, initial_forms: int = 0,
                       max_forms: int = 1000, min_forms: int = 0) -> dict:
    """
    Method builds a dictionary of key value pairs needed for posting a complete formset.
    """

    if data is None:
        data = []
    elif isinstance(data, dict):
        data = [data]

    if total_forms is None:
        total_forms = len(data)

    prefix = prefix or 'form'

    management_form_data = {
        f'{prefix}-INITIAL_FORMS': initial_forms,
        f'{prefix}-TOTAL_FORMS': total_forms,
        f'{prefix}-MAX_NUM_FORMS': max_forms,
        f'{prefix}-MIN_NUM_FORMS': min_forms,
    }

    forms_data = {
        f'{prefix}-{index}-{field}': value
        for index, dataset in enumerate(data)
        for field, value in dataset.items()
    }

    return {**management_form_data, **forms_data}


def admin_url(model: Type[Model], view: str, *args, site=None, **kwargs) -> str:
    """
    Return an url to an admin view.
    """

    opts = model._meta
    site = site or admin.site
    info = site.name, opts.app_label, opts.model_name, view

    return reverse('%s:%s_%s_%s' % info, args=args, kwargs=kwargs)


def patch_now(now):
    value = parse_datetime(now)

    if not is_aware(value):
        value = make_aware(value)

    return patch('django.utils.timezone.now', return_value=value)


@contextmanager
def temporary_media_storage(**kwargs):
    with maketempdir(**kwargs) as directory:
        with override_settings(MEDIA_ROOT=directory):
            yield directory
