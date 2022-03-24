import string

# We use uppercase letters
ALPHABET = string.digits + string.ascii_uppercase


def encode(value, alphabet=ALPHABET):
    """
    Encodes a given number in base 36.
    """

    assert isinstance(value, int), 'value must be an integer'
    assert not len(alphabet) < 36, 'the alphabet is too short'
    assert not len(alphabet) > 36, 'the alphabet is too long'
    assert value >= 0, 'value must be greater zero'

    encoded = ''

    while value:
        value, index = divmod(value, 36)
        encoded = alphabet[index] + encoded

    return encoded or alphabet[0]


def decode(value):
    """
    Decodes a given string in base 36.
    """

    return int(value, 36)
