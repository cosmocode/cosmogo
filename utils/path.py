import os

from contextlib import contextmanager

from .filepath import FilePath


@contextmanager
def working_directory(path: FilePath):
    current = os.getcwd()

    yield os.chdir(path)

    os.chdir(current)


def ensure_directory(filepath: FilePath):
    directory = os.path.dirname(filepath)

    os.makedirs(directory, exist_ok=True)

    return directory
