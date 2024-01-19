from typing import Set, Type

from django.contrib.admin import site
from django.db.models import Model
from django.test import TestCase
from django.utils.timezone import localtime

from cosmogo.admin import admin_url
from cosmogo.utils.testing import create_superuser, login, request

ModelType = Type[Model]
ModelSet = Set[ModelType]


class BaseAdminTestCase(TestCase):
    exclude_models: ModelSet = set()
    exclude_models_changelist: ModelSet = set()
    exclude_models_add: ModelSet = set()
    exclude_models_change: ModelSet = set()

    @classmethod
    def setUpTestData(cls):
        cls.now = now = localtime(None)
        cls.user = user = cls.create_user(now)
        cls.models = {*site._registry} - cls.exclude_models

        cls.create_objects(user, now)

    @classmethod
    def create_user(cls, now):
        return create_superuser('admin', date_joined=now)

    @classmethod
    def create_objects(cls, user, now):
        raise NotImplementedError

    def setUp(self):
        login(self)

    def assertModelExists(self, model):
        obj = model.objects.first()

        self.assertTrue(obj, msg=(
                'Make sure to have at least one instance of each model. '
                '%s.%s does not have any objects.' % (
                    model._meta.app_label,
                    model._meta.object_name,
                )
        ))

        self.assertTrue(f'{obj}', msg='%r does not return a proper string.' % obj)

        return obj

    def helper_for_model(self, get_url, exclude: ModelSet):
        for model in (self.models - exclude):
            with self.subTest(model=model):
                obj = self.assertModelExists(model)
                url = get_url(obj)

                request(self, url)

    def test_change_lists(self):
        def get_url(model):
            return admin_url(model, 'changelist')

        return self.helper_for_model(get_url, self.exclude_models_changelist)

    def test_add_forms(self):
        def get_url(model):
            return admin_url(model, 'add')

        return self.helper_for_model(get_url, self.exclude_models_add)

    def test_change_forms(self):
        def get_url(obj):
            return admin_url(obj, 'change', obj.pk)

        return self.helper_for_model(get_url, self.exclude_models_change)
