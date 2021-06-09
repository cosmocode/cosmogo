import os
import subprocess


def get_commit(path, revision='HEAD'):
    if 'CI_COMMIT_SHA' in os.environ:
        return os.environ.get('CI_COMMIT_SHA')

    path = os.path.abspath(path)
    command = ['git', 'rev-parse', revision]

    if os.path.isfile(path):
        path = os.path.dirname(path)

    output = subprocess.check_output(command, cwd=path, encoding='utf-8')

    return str.strip(output)
