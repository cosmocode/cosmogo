import datetime
import random

from contextlib import contextmanager
from typing import Any, Iterable, Mapping, List, Union, Tuple, Optional, Protocol
from unittest.mock import patch

from django.apps import apps
from django.conf import settings
from django.core.management import call_command as django_call_command
from django.db.models import Model
from django.forms import model_to_dict
from django.http import HttpRequest, HttpResponse
from django.http.response import HttpResponseRedirectBase, StreamingHttpResponse
from django.shortcuts import resolve_url
from django.template import Context
from django.template.response import TemplateResponse
from django.test import Client, SimpleTestCase, override_settings
from django.urls import reverse, ResolverMatch
from django.utils.dateparse import parse_datetime
from django.utils.formats import get_format
from django.utils.http import urlencode
from django.utils.timezone import make_aware, is_aware

try:
    from rest_framework.response import Response as RestFrameworkResponse
except ImportError:
    from django.template.response import SimpleTemplateResponse as RestFrameworkResponse

# import for backwards compatibility
# noinspection PyUnresolvedReferences
from cosmogo.admin import admin_url

from .tempdir import maketempdir


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


def create_superuser(username: str, **kwargs):
    kwargs['is_superuser'] = True
    kwargs['is_staff'] = True

    return create_user(username, **kwargs)


class ObjectWithGetAbsoluteURLMethod(Protocol):

    def get_absolute_url(self) -> str:
        ...


URL = Union[str, ObjectWithGetAbsoluteURLMethod]
URLArgs = Union[tuple, list]
URLKwargs = dict


def get_url(url: URL, args: URLArgs = None, kwargs: URLKwargs = None) -> str:
    """
    Helper to reverse the given url name.
    """

    if args or kwargs:
        return reverse(url, args=args, kwargs=kwargs)

    return resolve_url(url)


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


FormData = dict
JSONDict = dict
JSONList = list
RequestData = Union[FormData, JSONDict, JSONList]
QueryParams = Union[Mapping[str, Any], Iterable[Tuple[str, Any]]]


class TestClientResponse:
    client: Client
    request: HttpRequest
    templates: list
    context: Context
    resolver_match: ResolverMatch

    def json(self) -> Union[list, dict]:
        pass


Response = Union[
    HttpResponse,
    HttpResponseRedirectBase,
    StreamingHttpResponse,
    TemplateResponse,
    TestClientResponse,
    RestFrameworkResponse,
]


def request(
    test_case: SimpleTestCase,
    url: URL,
    status_code: int = None,
    expected_url: URL = None,
    args: URLArgs = None,
    kwargs: URLKwargs = None,
    headers: dict = None,
    msg: str = None,
    query_params: QueryParams = None,
    method: str = None,
    data: RequestData = None,
    content_type: str = None,
    **options,
) -> Response:
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
    if content_type is not None:
        headers['content_type'] = content_type

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


FormSetData = Union[List[dict], dict]


def build_formset_data(data: FormSetData = None, prefix: str = None, total_forms: int = None, initial_forms: int = 0,
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


def build_form_data(obj: Model, prefix: str = None, **kwargs) -> dict:
    data = {**model_to_dict(obj), **kwargs}

    if prefix:
        return {f'{prefix}-{key}': serialize_form_data(value) for key, value in data.items()}

    return serialize_form_data(data)


def serialize_form_data(value):
    if value is None:
        return ''
    elif isinstance(value, dict):
        return {key: serialize_form_data(value) for key, value in value.items()}
    elif isinstance(value, list):
        return [serialize_form_data(value) for value in value]
    elif isinstance(value, Model):
        return serialize_form_data(value.pk)

    return value


def patch_now(now, *, target='django.utils.timezone.now'):
    value = parse_datetime(now) if isinstance(now, str) else now

    if not is_aware(value):
        value = make_aware(value)

    return patch(target, return_value=value)


@contextmanager
def temporary_media_storage(**kwargs):
    with maketempdir(**kwargs) as directory:
        with override_settings(MEDIA_ROOT=directory):
            yield directory


@contextmanager
def override_dns_name(new_dns_name: str, *, attr='_fqdn'):
    """
    This context manager can be used to prefill the DNS name cache to avoid long timeouts on local machines.
    """

    from django.core.mail import DNS_NAME

    old_dns_name = getattr(DNS_NAME, attr, None)

    setattr(DNS_NAME, attr, new_dns_name)

    try:
        yield old_dns_name
    finally:
        if old_dns_name:
            setattr(DNS_NAME, attr, old_dns_name)
        else:
            delattr(DNS_NAME, attr)
