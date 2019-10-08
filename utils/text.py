from django.utils.text import slugify as django_slugify
from django.utils.translation import gettext_lazy as _

CONJUNCTION_AND = _('%(first)s and %(second)s')
CONJUNCTION_OR = _('%(first)s or %(second)s')
DELIMITER = ', '

TRANSLITERATIONS = (
    ('ä', 'ae'),
    ('ö', 'oe'),
    ('ü', 'ue'),
    ('ß', 'ss'),
)


def enumeration(words, conjunction=CONJUNCTION_AND, delimiter=DELIMITER):
    if not words:
        return ''

    *first, second = map(str, words)

    if first:
        return conjunction % dict(first=delimiter.join(first), second=second)

    return second


def slugify(value, transliterations=TRANSLITERATIONS):
    value = transliterate(value, transliterations=transliterations)

    return django_slugify(value)


def transliterate(value, transliterations=TRANSLITERATIONS):
    for character, transliteration in transliterations:
        value = value.replace(character, transliteration)

    return value
