import os

from pathlib import Path
from typing import List

import django
import polib

from django.conf import settings
from django.core.management import BaseCommand, call_command
from django.core.management.commands.compilemessages import Command as CompileMessagesCommand
from django.utils.translation import to_locale

from cosmogo.utils.path import cd


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

        return str(cls.LOCALE_DIR / to_locale(language) / 'LC_MESSAGES' / f'{domain}.po')

    @staticmethod
    def key(entry: polib.POEntry):
        return entry.msgid_with_context


class UpdateTranslationsCommand(GetTextCommandMixin, BaseCommand):
    requires_system_checks = False if django.VERSION < (3, 2) else []

    IGNORE = [
        'static',
        'test-data',
    ]

    DOMAINS = [
        ('django', [
            'html', 'txt', 'py',  # default
            'plain', 'subject',  # mails
        ]),
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
        parser.add_argument('--no-fuzzy', dest='fuzzy', action='store_true', default=False)

    def handle(self, languages, domains, fuzzy=False, **options):
        """
        Creates and cleans the translation files
        for every domain and configured language.
        """

        # We will create translation files
        # in the app dir and not globally.
        with cd(self.APPLICATION):
            return self.run(languages, domains, fuzzy, **options)

    def run(self, languages, domains, fuzzy, **options):
        # The locale dir isn't created automatically by makemessages.
        os.makedirs(self.LOCALE_DIR, exist_ok=True)

        languages = self.get_languages(languages)
        locales = self.get_locales(languages)
        domains = self.get_domains(domains)

        for domain, extensions in domains:
            self.call_command(
                locale=locales,
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
                self.clean(language, domain, fuzzy=fuzzy)

    def get_languages(self, languages):
        """
        When no language is given assume all languages.
        """

        return languages or self.language_codes

    @staticmethod
    def get_locales(languages):
        """
        Convert language codes to locale codes.
        """

        return [to_locale(language) for language in languages]

    def get_domains(self, domains):
        """
        Assume all extensions for given domains.
        """

        return domains and [(domain, dict(self.DOMAINS).get(domain)) for domain in domains] or self.DOMAINS

    @staticmethod
    def call_command(**kwargs):
        kwargs.pop('skip_checks', None)  # makemessages doesn't take this argument

        return call_command('makemessages', **kwargs)

    @classmethod
    def clean(cls, language, domain, fuzzy=False):
        """
        We use the polib library to parse the output
        file and remove all unnecessary meta data.
        """

        filepath = cls.get_filepath(language, domain)

        if not os.path.isfile(filepath):
            return False

        pofile = polib.pofile(filepath, wrapwidth=cls.WRAP_WIDTH)

        cls.set_meta_language(pofile, language)
        cls.set_header(pofile, language, domain)

        for key in list(pofile.metadata):
            if key not in cls.META:
                pofile.metadata.pop(key)

        if fuzzy:
            for entry in pofile:
                if entry.fuzzy:
                    cls.clean_fuzzy(entry)

        pofile.save(filepath)

        return True

    @staticmethod
    def clean_fuzzy(entry: polib.POEntry):
        entry.flags.remove('fuzzy')
        entry.msgstr = ''
        entry.msgstr_plural = {count: '' for count in entry.msgstr_plural}
        entry.previous_msgctxt = None
        entry.previous_msgid = None
        entry.previous_msgid_plural = None

    @staticmethod
    def set_meta_language(pofile, language, key='Language'):
        if not pofile.metadata.get(key):
            pofile.metadata[key] = language

    @classmethod
    def set_header(cls, pofile, language, domain):
        pass  # hook to set the header of the pofile


class CompileTranslationsCommand(GetTextCommandMixin, CompileMessagesCommand):
    """
    This command eases the process of compiling translations
    for a project by avoid compiling message files in the
    virtualenv directory.
    """

    def add_arguments(self, parser):
        super(CompileTranslationsCommand, self).add_arguments(parser)
        parser.add_argument('--directory', '-d', default=self.APPLICATION)

    def handle(self, *, directory, **options):
        """
        Changes to the application directory before compiling translation files.
        """

        with cd(directory):
            return super(CompileTranslationsCommand, self).handle(**options)
