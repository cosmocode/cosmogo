import os
import shutil

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test.runner import DiscoverRunner

from cosmogo.utils.testing import override_dns_name


class CosmoCodeTestRunner(DiscoverRunner):

    def setup_test_environment(self, **kwargs):
        if settings.MEDIA_ROOT == settings.BASE_DIR / 'media':
            raise ImproperlyConfigured(
                f'Make sure to set MEDIA_ROOT to a directory distinct from the '
                f'default MEDIA_ROOT when using {self.__class__.__name__}'
            )

        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        DiscoverRunner.setup_test_environment(self, **kwargs)

    def teardown_test_environment(self, **kwargs):
        DiscoverRunner.teardown_test_environment(self, **kwargs)
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    if DNS_NAME := getattr(settings, 'TEST_RUNNER_OVERRIDE_DNS_NAME', None):
        def run_tests(self, test_labels, extra_tests=None, **kwargs):
            with override_dns_name(self.DNS_NAME):
                return DiscoverRunner.run_tests(self, test_labels, extra_tests=extra_tests, **kwargs)
