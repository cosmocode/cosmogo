
from django.core.management import BaseCommand


class Command(BaseCommand):

    @property
    def tasks(self):
        from celery.app import default_app

        return default_app.tasks

    def add_arguments(self, parser):
        parser.add_argument('name', choices=sorted(self.tasks))

    def handle(self, *, name, **options):
        result = self.tasks[name].delay()

        self.stdout.write(f'Started task {name} with ID {result}.')
