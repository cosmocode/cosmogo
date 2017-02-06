from .base import DatabaseInitialiserException
from .postgres import PostgresInitialiser
from .sqlite import SQLiteInitialiser

__all__ = [
    'ENGINES',
    'DatabaseInitialiserException',
]

ENGINES = {
    'postgresql': PostgresInitialiser,
    'postgresql_psycopg2': PostgresInitialiser,
    'postgis': PostgresInitialiser,
    'sqlite3': SQLiteInitialiser,
}
