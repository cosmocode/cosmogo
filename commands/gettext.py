import os

from pathlib import Path
from typing import List

import polib

from django.conf import settings
from django.core.management import BaseCommand, call_command
from django.core.management.commands.compilemessages import Command as CompileMessagesCommand


class GetTextCommandMixin:
    APPLICATION: str
    LOCALE_DIR = Path('locale')

    @property
    def language_codes(self) -> List[str]:
        return [code for code, name in settings.LANGUAGES]

    @classmethod
    def get_filepath(cls, language, domain) -> str:
        """
        Returns the path for a pofile with the supplied
        domain in the specified language.
        """

        return str(cls.LOCALE_DIR / language / 'LC_MESSAGES' / f'{domain}.po')

    @staticmethod
    def key(entry) -> tuple:
        return entry.msgid, entry.msgid_plural


class UpdateTranslationsCommand(GetTextCommandMixin, BaseCommand):
    requires_system_checks = False

    IGNORE = [
        'static',
        'test-data',
    ]

    DOMAINS = [
        ('django', None),
        ('djangojs', None),
    ]

    META = {
        'Content-Type',
        'Plural-Forms',
        'Language',
    }

    WRAP_WIDTH = 0  # no wrap

    def add_arguments(self, parser):
        parser.add_argument('-l', dest='languages', action='append', choices=self.language_codes)
        parser.add_argument('-d', dest='domains', action='append', choices=list(dict(self.DOMAINS)))

    def handle(self, languages, domains, **options):
        """
        Creates and cleans the translation files
        for every domain and configured language.
        """

        # We will create translation files
        # in the app dir and not globally.
        os.chdir(self.APPLICATION)

        # The locale dir isn't created automatically by makemessages.
        os.makedirs(self.LOCALE_DIR, exist_ok=True)

        languages = self.get_languages(languages)
        domains = self.get_domains(domains)

        for domain, extensions in domains:
            self.call_command(
                locale=languages,
                domain=domain,
                extensions=extensions,
                ignore_patterns=self.IGNORE,
                no_wrap=self.WRAP_WIDTH == 0,
                no_location=True,
                symlinks=True,
                **options
            )

        for language in languages:
            for domain, extensions in domains:
                self.clean(language, domain)

    def get_languages(self, languages):
        """
        When no language is given assume all languages.
        """

        return languages or self.language_codes

    def get_domains(self, domains):
        """
        Assume all extensions for given domains.
        """

        return domains and [(domain, None) for domain in domains] or self.DOMAINS

    @staticmethod
    def call_command(**kwargs):
        return call_command('makemessages', **kwargs)

    @classmethod
    def clean(cls, language, domain):
        """
        We use the polib library to parse the output
        file and remove all unnecessary meta data.
        """

        filepath = cls.get_filepath(language, domain)

        if not os.path.isfile(filepath):
            return False

        pofile = polib.pofile(filepath, wrapwidth=cls.WRAP_WIDTH)

        cls.set_meta_language(pofile, language)

        for key in list(pofile.metadata):
            if key not in cls.META:
                pofile.metadata.pop(key)

        pofile.save(filepath)

        return True

    @staticmethod
    def set_meta_language(pofile, language, key='Language'):
        if not pofile.metadata.get(key):
            pofile.metadata[key] = language


class CompileTranslationsCommand(GetTextCommandMixin, CompileMessagesCommand):
    """
    This command eases the process of compiling translations
    for a project by avoid compiling message files in the
    virtualenv directory.
    """

    def handle(self, **options):
        """
        Changes to the application directory before compiling translation files.
        """

        os.chdir(self.APPLICATION)

        return super(CompileTranslationsCommand, self).handle(**options)
