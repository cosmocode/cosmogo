from django.conf import settings


def get_ip_address(request, default='0.0.0.0', *, use_x_forwarded_for=False):
    if getattr(settings, 'USE_X_FORWARDED_FOR', use_x_forwarded_for):
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR')

        if forwarded:
            client, *proxys = forwarded.split(',', 1)
            client = str.strip(client)

            if client:
                return client

    return request.META.get('REMOTE_ADDR') or default
