"""
CI*Fields are deprecated as of Django 4.2 and removed in Django 5.1. They should be replaced by using a
case-insensitive collation. But this still has some drawbacks, so we reimplemented the fields here.
"""

from django.db.models import CharField, EmailField


class CIText:

    def get_internal_type(self):
        return 'CI' + super().get_internal_type()

    def db_type(self, connection):
        return 'citext'


class CICharField(CIText, CharField):
    pass


class CIEmailField(CIText, EmailField):
    pass
