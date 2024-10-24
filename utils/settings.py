import os

from django.conf import global_settings as default_settings
from django.core.exceptions import ImproperlyConfigured

from .confirmation import TRUTHY
from .git import get_commit


def env(key, default=None, parser=None):
    value = os.environ.get(key)

    if value is None:
        return default

    if parser is None:
        if default is None:
            return value
        else:
            parser = type(default)

    if parser is bool:
        return truthy(value, default)

    return parser(value)


def setdefault(key, default, value: str = None, parser=None):
    if value is None:
        value = f'{default}'

    value = os.environ.setdefault(key, value)

    if parser is None:
        parser = type(default)

    if parser is bool:
        return truthy(value, default)

    return parser(value)


def truthy(value, default=False):
    return TRUTHY.get(value, default)


def debug_toolbar(apps, middleware, active=True, **config):
    """
    Returns configured settings when debug toolbar is available.
    """

    try:
        import debug_toolbar
    except ImportError:
        debug_toolbar = active = False

    ips = ['localhost', '127.0.0.1'] + ['192.168.0.%i' % ip for ip in range(1, 256)]

    if active:
        apps = apps + [getattr(debug_toolbar, 'default_app_config', 'debug_toolbar')]
        middleware = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + middleware
        config = dict(
            # Hide the debug toolbar by default.
            SHOW_COLLAPSED=True,

            # We disable the rarely used panels
            # by default to improve performance.
            DISABLE_PANELS={
                'debug_toolbar.panels.versions.VersionsPanel',
                'debug_toolbar.panels.timer.TimerPanel',
                'debug_toolbar.panels.settings.SettingsPanel',
                'debug_toolbar.panels.headers.HeadersPanel',
                'debug_toolbar.panels.request.RequestPanel',
                'debug_toolbar.panels.staticfiles.StaticFilesPanel',
                'debug_toolbar.panels.templates.TemplatesPanel',
                'debug_toolbar.panels.cache.CachePanel',
                'debug_toolbar.panels.signals.SignalsPanel',
                'debug_toolbar.panels.logging.LoggingPanel',
                'debug_toolbar.panels.redirects.RedirectsPanel',
            },
        )

    return apps, middleware, ips, active, config


def django_extensions(apps, active=True):
    try:
        import django_extensions
    except ImportError:
        active = False

    if active:
        apps += ['django_extensions']

    return apps


def default_from_email(address=default_settings.DEFAULT_FROM_EMAIL, name=None):
    address = env('DEFAULT_FROM_EMAIL_ADDRESS', address)

    if name := env('DEFAULT_FROM_EMAIL_NAME', name):
        address = f'{name} <{address}>'

    address = env('DEFAULT_FROM_EMAIL', address)

    return validate_from_email(address)


def validate_from_email(address):
    """
    See django.core.mail.message.sanitize_address for reference.
    """

    from email.headerregistry import parser

    try:
        token, rest = parser.get_mailbox(address)
    except Exception as error:
        message = f'{error}'
    else:
        if rest:
            message = f'only "{token}" could be parsed from "{address}".'
        else:
            return address

    raise ImproperlyConfigured(f'Invalid from email: {message}')


def password_validators(*validators):
    return list(_parse_password_validators(validators))


def _parse_password_validators(validators):
    for validator in validators:
        if isinstance(validator, (tuple, list)):
            validator, options = validator
        else:
            validator, options = validator, {}

        if '.' not in validator:
            validator = 'django.contrib.auth.password_validation.%s' % validator

        yield dict(NAME=validator, OPTIONS=options)


def get_git_commit(path, revision='HEAD'):
    return get_commit(path, revision=revision)


def configure_sentry(dsn, environment, release, celery=False, **kwargs):
    from sentry_sdk import init
    from sentry_sdk.integrations.django import DjangoIntegration

    integrations = [DjangoIntegration()]

    if celery:
        from sentry_sdk.integrations.celery import CeleryIntegration

        integrations.append(CeleryIntegration())

    kwargs['integrations'] = integrations

    return init(dsn=dsn, environment=environment, release=release, **kwargs)


REDIS_DEFAULTS = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
}


def redis(*, prefix='REDIS', **kwargs):
    defaults = dict(REDIS_DEFAULTS, **kwargs)

    for name in list(defaults):
        default = defaults.get(name)
        variable = str.upper(f'{prefix}_{name}')
        defaults[name] = env(variable, default)

    return 'redis://%(host)s:%(port)s/%(db)s' % defaults
