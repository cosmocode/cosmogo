# Django Helpers from CosmoCode

## init-db

To use the init-db command create an init-db.py file in your app's command module.
Import the `InitDBCommand` class and create a class `Command` inherting from the `InitDBCommand`.
You can add your needed fixtures or overwrite the defaults for the parameters like so:

```
from cosmogo.commad import InitDBCommand


class Command(InitDBCommand):
    FIXTURES = (
        'fixture-one.json',
        ...
    )
    DEFAULTS = {
        'interactive': False,
        ...
    }
```
