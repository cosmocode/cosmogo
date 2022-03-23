import os
import tarfile

from pathlib import Path
from tempfile import NamedTemporaryFile

import requests

from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.utils.http import urlencode

from cosmogo.utils.settings import env


def get_value(value, key, message):
    value = value or getattr(settings, key, None) or env(key)

    if value:
        return value

    raise CommandError(message)


def get_destination(destination, *, key='GEOIP_PATH'):
    destination = get_value(destination, key, f'No GeoIP path is present. Either supply a path via argument, set '
                                              f'a {key} in the django settings or set a {key} env variable.')
    return Path(destination)


def get_license_key(license_key, *, key='MAXMIND_LICENSE_KEY'):
    return get_value(license_key, key, f'No MaxMind license key is present. Either use the --key argument, set '
                                       f'a {key} in the django settings or set a {key} env variable.')


class Command(BaseCommand):
    HOST = 'https://download.maxmind.com'
    PATH = 'app/geoip_download'
    RESOURCES = [
        'City',
        'Country',
    ]

    def add_arguments(self, parser):
        parser.add_argument('destination', nargs='?', type=Path)
        parser.add_argument('--key', dest='license_key')

    def handle(self, *args, destination=None, license_key=None, **options):
        destination = get_destination(destination)
        license_key = get_license_key(license_key)

        os.makedirs(destination, exist_ok=True)

        for resource in self.RESOURCES:
            self.fetch(resource, destination, license_key)

    def fetch(self, resource, destination, license_key):
        name = f'GeoLite2-{resource}'
        params = urlencode({
            'edition_id': name,
            'suffix': 'tar.gz',
            'license_key': license_key,
        })

        url = f'{self.HOST}/{self.PATH}?{params}'

        try:
            response = requests.get(url, stream=True)
        except requests.RequestException as error:
            return self.failure(resource, error)

        if response.ok is False:
            return self.failure(resource, f'[{response.status_code}] {response.text}')

        with NamedTemporaryFile('wb', suffix=resource) as temp:
            for chunk in response.iter_content(None):
                temp.write(chunk)

            temp.flush()

            with tarfile.open(temp.name, 'r:gz') as archive:
                path = f'{archive.firstmember.name}/{name}.mmdb'
                info = archive.getmember(path)

                info.name = f'{name}.mmdb'

                archive.extract(info, path=destination)

    def failure(self, resource, error):
        self.stderr.write(f'Failed to download resource {resource}: {error}')
