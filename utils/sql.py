from typing import Type

from django.db import DEFAULT_DB_ALIAS, connections
from django.db.models import Model


def table(model: Type[Model], using: str = None) -> str:
    """
    Returns an quoted table name suitable to be used in a raw query.
    """

    opts = model._meta
    db_table = opts.db_table

    return quote(db_table, using)


def column(model: Type[Model], field: str, using: str = None) -> str:
    """
    Returns an absolute quoted column name suitable to be used in a raw query.
    """

    opts = model._meta
    db_table = opts.db_table
    db_field = opts.pk if field == 'pk' else opts.get_field(field)
    db_column = db_field.column

    return '{table}.{column}'.format(
        table=quote(db_table, using),
        column=quote(db_column, using),
    )


def quote(name: str, using: str = None) -> str:
    """
    Quotes a name using the connection with the given alias.
    """

    connection = connections[using or DEFAULT_DB_ALIAS]

    return connection.ops.quote_name(name)


def clean(sql: str, delimiter: str = ' ') -> str:
    """
    Cleans a given sql string and normalizes all whitespace.
    """

    return delimiter.join(filter(None, map(str.strip, sql.split())))
