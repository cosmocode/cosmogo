import hashlib

from django.utils.http import urlencode

HOST = 'https://gravatar.com'


def get_gravatar_url(email, size=40, default=None):
    identifier = hashlib.md5(email.lower()).hexdigest()
    params = {'s': size}

    if default:
        params['d'] = default

    return '%s/avatar/%s?%s' % (HOST, identifier, urlencode(params))
