from typing import List

from celery import Celery


def configure(name: str, *, packages: List[str] = None, **kwargs) -> Celery:
    kwargs.setdefault('main', name)
    kwargs.setdefault('namespace', 'CELERY')

    app = Celery(**kwargs)
    packages = packages or [app.main, 'cosmogo']

    app.config_from_object('django.conf:settings')
    app.autodiscover_tasks(packages=packages)

    return app
