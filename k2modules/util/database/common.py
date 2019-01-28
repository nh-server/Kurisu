import sqlite3
from typing import TYPE_CHECKING

from ..tools import connwrap

if TYPE_CHECKING:
    from typing import Generator, Iterable, KeysView, Tuple
    from kurisu2 import Kurisu2


class DatabaseManagerError(Exception):
    """General exception class for BaseDatabaseManager classes."""


class BaseDatabaseManager:
    """Manages sqlite3 connections and operations for Kurisu2."""

    def __init__(self, bot: 'Kurisu2'):
        self.bot = bot
        self.log = bot.log
        self.conn = bot.dbcon

    def _format_select_vars(self, keys: 'KeysView[str]') -> str:
        assert not self.bot.db_closed

        if len(keys) == 0:
            return ''
        return 'WHERE ' + ' AND '.join(f'`{c}` = :{c}' for c in keys)

    def _format_insert_vars(self, keys: 'KeysView[str]') -> str:
        assert not self.bot.db_closed
        assert keys

        return ', '.join(f':{c}' for c in keys)

    def _format_cols(self, keys: 'KeysView[str]') -> str:
        assert not self.bot.db_closed
        assert keys

        return ', '.join(f'`{c}`' for c in keys)

    def _select(self, table: str, **values) -> 'Generator[Tuple, None, None]':
        assert not self.bot.db_closed

        c: sqlite3.Connection
        with connwrap(self.conn) as c:
            query = f'SELECT * FROM {table} {self._format_select_vars(values.keys())}'
            res = c.execute(query, values)
            self.log.debug('Executed SELECT query on %s with parameters %s', table, values)
            yield from res

    def _row_count(self, table: str, **values) -> int:
        assert not self.bot.db_closed

        c: sqlite3.Connection
        with connwrap(self.conn) as c:
            query = f'SELECT COUNT(*) FROM {table} {self._format_select_vars(values.keys())}'
            res = c.execute(query, values)
            self.log.debug('Executed SELECT COUNT() query on %s with parameters %s', table, values)
            return res.fetchone()[0]

    def _insert(self, table: str, **values):
        assert not self.bot.db_closed
        assert values

        c: sqlite3.Connection
        with connwrap(self.conn) as c:
            query = (f'INSERT INTO {table} ({self._format_cols(values.keys())}) '
                     f'VALUES ({self._format_insert_vars(values.keys())})')
            # TODO: catch an exception here, but what?
            c.execute(query, values)
            self.log.debug('Executed INSERT query on %s with parameters %s', table, values)

    def _delete(self, table: str, **values) -> int:
        assert not self.bot.db_closed
        assert values

        c: sqlite3.Connection
        with connwrap(self.conn) as c:
            query = f'DELETE FROM {table} {self._format_select_vars(values.keys())}'
            # TODO: catch some exception here, probably
            # (DELETE shouldn't raise unless something has gone horribly wrong)
            res = c.execute(query, values)
            self.log.debug('Executed DELETE query on %s with parameters %s', table, values)
            return res.rowcount
