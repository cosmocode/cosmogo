import shutil
import tempfile

from contextlib import contextmanager


@contextmanager
def maketempdir(onerror=None, **kwargs):
    directory = tempfile.mkdtemp(**kwargs)

    yield directory

    shutil.rmtree(directory, ignore_errors=onerror is None, onerror=onerror)
