import hashlib

from django.utils.http import urlencode

HOST = 'https://gravatar.com'


def get_gravatar_url(email, size=40, default=None):
    email = email.lower().encode('utf-8')
    identifier = hashlib.md5(email).hexdigest()
    params = {'s': size}

    if default:
        params['d'] = default

    return '%s/avatar/%s?%s' % (HOST, identifier, urlencode(params))
