import re

from django import VERSION, forms
from django.db import IntegrityError
from django.db.transaction import get_connection, Atomic


class IntegrityToValidationError(Atomic):
    """
    To atomically create a model with unique constraints you have to insert it into
    the database and catch the integrity error. The integrity error is quite
    unhandy to work with since it doesn't report you the exact model field of the
    failed constraint. That's no problem unless you have multiple fields with
    unique constraints on it. To properly report the failed model field to the user
    this class can convert an integrity error into a proper validation error.
    """

    patterns = {
        'postgresql': re.compile(r'Key \((?P<field>.+)\)=\((?P<value>.+)\) already exists\.', re.M | re.U | re.I),
        'sqlite': re.compile(r'UNIQUE constraint failed: (?P<table>.+)\.(?P<field>.+)', re.U | re.I),
    }

    def __init__(self, messages, values=None, *, using=None, durable=False):
        kwargs = {'using': using, 'savepoint': True}

        if VERSION >= (3, 2):
            kwargs['durable'] = durable

        super(IntegrityToValidationError, self).__init__(**kwargs)

        connection = get_connection(using)
        pattern = self.patterns.get(connection.vendor)

        self.messages = messages
        self.pattern = pattern
        self.values = values or {}

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(IntegrityToValidationError, self).__exit__(exc_type, exc_val, exc_tb)

        if isinstance(exc_val, IntegrityError):
            raise self.convert_integrity_error(f'{exc_val}')

    def convert_integrity_error(self, error: str):
        match = self.pattern.search(error)

        if match:
            field = match.group('field')

            try:
                value = match.group('value')
            except IndexError:
                value = self.values.get(field)

            code = 'duplicate-%s' % field
            message = self.messages.get(field)
            params = {field: value, 'value': value}

            if isinstance(message, dict):
                message = message.get(code)

            raise forms.ValidationError({
                field: forms.ValidationError(
                    message=message,
                    params=params,
                    code=code,
                ),
            })

        raise forms.ValidationError(
            message=error,
            code='duplicate',
        )
