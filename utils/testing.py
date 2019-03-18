from typing import Union, List

from django.test import SimpleTestCase
from django.urls import reverse

Data = Union[List[dict], dict]
Args = Union[tuple, list]


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


def request(test_case: SimpleTestCase, url: str, status_code: int = None, expected_url: str = None,
            args: Args = None, kwargs: dict = None, headers: dict = None, msg: str = None, **data):
    """
    A helper to make a request with the test case's http client.

    The given args and kwargs are used to reverse the url
    but not the expected url. When expected url needs
    args/kwargs pass an absolute url instead.

    All additional kwargs are passed as post parameters.
    When posting without parameters just pass post=True.
    """

    url = get_url(url, args, kwargs)
    headers = headers or {}

    if data:
        response = test_case.client.post(url, data=data, **headers)
    else:
        response = test_case.client.get(url, **headers)

    status_code = status_code or 200
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
