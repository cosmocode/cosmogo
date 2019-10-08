from django.utils.translation import gettext_lazy


def trans(string):
    """
    This is just an alias for gettext lazy with the difference that
    words tagged with it won't be found by gettext but are still
    translated by existing translation files containing the word.
    This is useful to use standard translations from django for
    words that we copied from django.
    """

    return gettext_lazy(string)
