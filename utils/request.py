from django.conf import settings


def get_ip_address(request, default='0.0.0.0'):
    if getattr(settings, 'USE_X_FORWARDED_FOR', False):
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR')

        if forwarded:
            client, *proxys = forwarded.split(',', 1)

            if client:
                return client

    return request.META.get('REMOTE_ADDR') or default
