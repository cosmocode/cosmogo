from django.conf import settings
from django.core.management import BaseCommand, CommandError, call_command

from .initialiser import ENGINES, DatabaseInitialiserException
from .utils import ask


class InitDBCommand(BaseCommand):
    FIXTURES = ()
    DEFAULTS = {}
    ENGINES = ENGINES

    def add_arguments(self, parser):
        parser.add_argument(
            '--noinput', '--no-input',
            action='store_false',
            dest='interactive',
            default=self.DEFAULTS.get('interactive', True),
            help='Tells Django to NOT prompt the user for input of any kind.'
        )

        parser.add_argument(
            '--nodropdb', '--no-drop-db',
            action='store_false',
            dest='drop-database',
            default=self.DEFAULTS.get('drop-database', settings.DEBUG),
            help='The command will NOT drop the database.'
        )

        parser.add_argument(
            '--noloadfixtures', '--no-load-fixtures',
            action='store_false',
            dest='load-fixtures',
            default=self.DEFAULTS.get('load-fixtures', True),
            help='The command will NOT load initial fixtures.'
        )

    def handle(self, *args, **options):
        verbosity = options['verbosity']
        interactive = options['interactive']
        drop = options['drop-database']
        load = options['load-fixtures']

        self.setup_databases(drop, verbosity, interactive)
        self.load_fixtures(load, verbosity)

    @staticmethod
    def call_command(command, *args, verbosity, **kwargs):
        return call_command(command, *args, verbosity=min(0, verbosity - 1), **kwargs)

    def setup_databases(self, drop, verbosity, interactive):
        if interactive and drop and not settings.DEBUG:
            question = 'You are currently on production settings. Do you really want to wipe the database? [NO/yes]: '

            if not ask(question, default=False):
                raise CommandError('Cancelled.')

        for alias in settings.DATABASES:
            self.setup_database(alias, drop, verbosity, interactive)

    def setup_database(self, alias, drop, verbosity, interactive):
        config = settings.DATABASES[alias]
        module, engine = config['ENGINE'].rsplit('.', 1)
        initialiser = self.ENGINES.get(engine)

        if initialiser is None:
            raise CommandError('Could not set up database %s. Engine %s is currently not supported.' % (alias, engine))

        if verbosity > 0:
            self.stdout.write('Setting up database %s ...' % alias)

        try:
            with initialiser(self, alias, drop, verbosity, interactive, config):
                self.call_command('migrate', verbosity=verbosity, interactive=interactive, database=alias)
        except DatabaseInitialiserException as error:
            raise CommandError('Could not initialise database %s: %s' % (alias, error))

    def load_fixtures(self, load, verbosity):
        if not load:
            return None

        for alias in settings.DATABASES:
            if verbosity > 0:
                self.stdout.write('Loading fixtures for database %s ...' % alias)

            self.call_command('loaddata', *self.FIXTURES, verbosity=verbosity, database=alias)
