import os

from contextlib import contextmanager


@contextmanager
def working_directory(path):
    current = os.getcwd()

    yield os.chdir(path)

    os.chdir(current)
