import string

from dataclasses import dataclass

from django.utils.crypto import get_random_string

CONFUSING = {'0', 'O', '1', 'I', 'l'}
CHARS = string.ascii_uppercase + string.digits
DEFAULT_CHARS = ''.join(sorted(set(CHARS) - CONFUSING))


@dataclass
class Identifier:
    parts: int = 4
    parts_length: int = 4
    delimiter: str = '-'
    chars: str = DEFAULT_CHARS

    @property
    def length(self):
        return self.parts * self.parts_length + (self.parts - 1) * len(self.delimiter)

    @property
    def count(self):
        return len(self.chars) ** (self.parts * self.parts)

    @property
    def part(self):
        return get_random_string(self.parts_length, self.chars)

    @property
    def rnd(self):
        return self.delimiter.join(self.part for _ in range(self.parts))

    def __str__(self):
        return self.rnd
