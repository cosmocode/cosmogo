from django.utils import six

YES_NO = {
    '1': True,
    'y': True,
    'Y': True,
    'yes': True,
    'YES': True,
    '0': False,
    'n': False,
    'N': False,
    'no': False,
    'NO': False,
}


def ask(question, default=False):
    response = six.moves.input(question).strip()

    return YES_NO.get(response, default)
