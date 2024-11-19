import os
import subprocess


def get_commit(path, *, short=False, revision='HEAD', env_key='CI_COMMIT_SHA'):
    if ci_commit_sha := os.getenv(env_key):
        return ci_commit_sha

    command = ['git', 'rev-parse', revision]

    if short:
        command.insert(2, '--short')

    path = os.path.abspath(path)

    if os.path.isfile(path):
        path = os.path.dirname(path)

    output = subprocess.check_output(command, cwd=path, encoding='utf-8')

    return str.strip(output)


def get_commit_short(path, *, revision='HEAD'):
    return get_commit(path, short=True, revision=revision, env_key='CI_COMMIT_SHORT_SHA')
