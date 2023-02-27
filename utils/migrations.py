from contextlib import contextmanager
from typing import Type, Union

from django.db import models


def get_queryset(apps, schema_editor, *model):
    return apps.get_model(*model).objects.using(schema_editor.connection.alias)


@contextmanager
def disable_auto_now(model: Type[models.Model], field: Union[str, models.DateField]):
    if isinstance(field, str):
        field = getattr(model, '_meta').get_field(field)

    assert isinstance(field, models.DateField), f'{field.name} is no date field.'

    auto_now, auto_now_add = field.auto_now, field.auto_now_add
    field.auto_now = field.auto_now_add = False

    try:
        yield auto_now, auto_now_add
    finally:
        field.auto_now, field.auto_now_add = auto_now, auto_now_add
