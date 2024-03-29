from django.urls import path

from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ViewSetMixin


class Router(DefaultRouter):
    """
    Custom default router that implements a register decorator.
    """

    def __init__(self, *args, version=None, **kwargs):
        self.version = f'{version or 1}'
        self.urlpatterns = []

        DefaultRouter.__init__(self, *args, **kwargs)

    def get_urls(self):
        """
        We use the tuple approach like the admin does.
        """

        return DefaultRouter.get_urls(self) + self.urlpatterns, 'api', self.version

    def register(self, prefix, viewset=None, basename=None):
        """
        A register method that can be used as a decorator.
        """

        if viewset is None:
            def inner(cls):
                self.register(prefix=prefix, viewset=cls, basename=basename)
                return cls
            return inner
        elif issubclass(viewset, ViewSetMixin):
            DefaultRouter.register(self, prefix=prefix, viewset=viewset, basename=basename)
        else:
            self.urlpatterns.append(
                path(f'{prefix}{self.trailing_slash}', viewset.as_view(), name=basename),
            )
