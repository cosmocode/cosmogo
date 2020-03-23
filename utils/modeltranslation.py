from typing import Type, List

from django.db.models import Model

from modeltranslation.manager import get_translatable_fields_for_model
from modeltranslation.utils import get_translation_fields as base_get_translation_fields


def get_translation_fields(model: Type[Model]) -> List[str]:
    return [
        field
        for field in get_translatable_fields_for_model(model)
        for field in base_get_translation_fields(field)
    ]
