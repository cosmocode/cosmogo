from django.db.models import Model, QuerySet


class ModelTestMixin:
    """
    Model test helpers.
    """

    def assertExists(self, model: type[Model] | QuerySet, msg: str = None, **filter_kwargs):
        self.assertTrue(getattr(model, '_default_manager', model).filter(**filter_kwargs).exists(), msg=msg)

    def assertNotExists(self, model: type[Model] | QuerySet, msg: str = None, **filter_kwargs):
        self.assertFalse(getattr(model, '_default_manager', model).filter(**filter_kwargs).exists(), msg=msg)
