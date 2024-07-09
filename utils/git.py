import os
import subprocess


def get_commit(path, revision='HEAD'):
    if ci_commit_sha := os.getenv('CI_COMMIT_SHA'):
        return ci_commit_sha

    path = os.path.abspath(path)
    command = ['git', 'rev-parse', revision]

    if os.path.isfile(path):
        path = os.path.dirname(path)

    output = subprocess.check_output(command, cwd=path, encoding='utf-8')

    return str.strip(output)


def get_commit_short(path, revision='HEAD'):
    if ci_commit_short_sha := os.getenv('CI_COMMIT_SHORT_SHA'):
        return ci_commit_short_sha

    path = os.path.abspath(path)
    command = ['git', 'rev-parse', '--short', revision]

    if os.path.isfile(path):
        path = os.path.dirname(path)

    output = subprocess.check_output(command, cwd=path, encoding='utf-8')

    return str.strip(output)
