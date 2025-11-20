from django.db.models import CharField


def get_values(choices):
    for value, label in choices:
        if isinstance(label, (list, tuple)):
            yield from get_values(label)
        else:
            yield value


class ChoiceField(CharField):

    def __init__(self, verbose_name=None, *, choices, primary_key=False, unique=False, **kwargs):
        db_index = not (primary_key or unique)
        default, *values = get_values(choices)
        max_length = max(map(len, [default, *values]))

        kwargs.setdefault('max_length', max_length)
        kwargs.setdefault('default', default)
        kwargs.setdefault('db_index', db_index)

        kwargs['choices'] = choices
        kwargs['primary_key'] = primary_key
        kwargs['unique'] = unique

        super(ChoiceField, self).__init__(verbose_name=verbose_name, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = CharField.deconstruct(self)

        if not (self.primary_key or self.unique):
            # always deconstruct the db index flag,
            # or it couldn't be set to `False`
            kwargs['db_index'] = self.db_index

        return name, path, args, kwargs
