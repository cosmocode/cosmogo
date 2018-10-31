import shutil
import tempfile

from contextlib import contextmanager

try:
    from pathlib import Path
except ImportError:
    Path = str


@contextmanager
def maketempdir(onerror=None, **kwargs):
    directory = tempfile.mkdtemp(**kwargs)

    yield Path(directory)

    shutil.rmtree(directory, ignore_errors=onerror is None, onerror=onerror)
