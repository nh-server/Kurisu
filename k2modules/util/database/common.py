import os.path
import sqlite3
from typing import TYPE_CHECKING

from ..tools import connwrap

if TYPE_CHECKING:
    from typing import Dict, Generator, Iterable, KeysView, Tuple
    from kurisu2 import Kurisu2

    Tables = Dict[str, Dict[str, str]]

# noinspection PyUnreachableCode
if __debug__:
    from itertools import chain


class DatabaseManagerError(Exception):
    """General exception class for BaseDatabaseManager classes."""


class ColumnValueFormatter:
    def __init__(self, columns: 'Iterable', values: 'Iterable'):
        self.columns = tuple(columns)
        self.values = tuple(values)

    def __repr__(self):
        return f'ColumnValueFormatter({self.columns}, {self.values})'

    def __str__(self):
        return ', '.join(f'({x!r}, {y!r})' for x, y in zip(self.columns, self.values))


class BaseDatabaseManager:
    """Manages sqlite3 connections and operations for Kurisu2."""

    tables: 'Tables' = None

    def __init__(self, bot: 'Kurisu2'):
        self.bot = bot
        self.log = bot.log
        self.conn = bot.dbcon

        if bot.db_create_tables:
            # create columns
            c: sqlite3.Cursor
            with connwrap(self.conn) as c:
                for tn, cl in self.tables.items():
                    cols = ', '.join(f'`{c}` {v}' for c, v in cl.items())
                    try:
                        c.execute(f'CREATE TABLE {tn} ({cols})')
                    except sqlite3.OperationalError as e:
                        # table likely exists
                        self.log.debug('Failed to create %s: %s: %s', tn, type(e), e, exc_info=e)
                    else:
                        self.log.info('%s table created', tn)

    # until PyCharm recognizes __init_subclass__ properly, these inspections must be disabled
    # noinspection PyMethodOverriding,PyArgumentList
    def __init_subclass__(cls, *, tables: 'Tables', **kwargs):
        cls.tables = tables

    def _format_select_vars(self, keys: 'KeysView[str]') -> str:
        assert not self.bot.db_closed
        assert all(k in chain.from_iterable(x.keys() for x in self.tables.values()) for k in keys)

        if len(keys) == 0:
            return ''
        return 'WHERE ' + ' AND '.join(f'`{c}` = :{c}' for c in keys)

    def _format_insert_vars(self, keys: 'KeysView[str]') -> str:
        assert not self.bot.db_closed
        assert keys
        assert all(k in chain.from_iterable(x.keys() for x in self.tables.values()) for k in keys)

        return ', '.join(f':{c}' for c in keys)

    def _format_cols(self, keys: 'KeysView[str]') -> str:
        assert not self.bot.db_closed
        assert keys
        assert all(k in chain.from_iterable(x.keys() for x in self.tables.values()) for k in keys)

        return ', '.join(f'`{c}`' for c in keys)

    def _select(self, table: str, **values) -> 'Generator[Tuple, None, None]':
        assert not self.bot.db_closed
        assert self.tables
        assert table in self.tables
        assert all(k in self.tables[table].keys() for k in values.keys())

        c: sqlite3.Connection
        with connwrap(self.conn) as c:
            query = f'SELECT * FROM {table} {self._format_select_vars(values.keys())}'
            res = c.execute(query, values)
            self.log.debug('Executed SELECT query with parameters %s',
                           ColumnValueFormatter(self.tables[table], values))
            yield from res

    def _row_count(self, table: str, **values) -> int:
        assert not self.bot.db_closed
        assert self.tables
        assert table in self.tables
        assert all(k in self.tables[table].keys() for k in values.keys())

        c: sqlite3.Connection
        with connwrap(self.conn) as c:
            query = f'SELECT COUNT(*) FROM {table} {self._format_select_vars(values.keys())}'
            res = c.execute(query, values)
            self.log.debug('Executed SELECT COUNT() query with parameters %s',
                           ColumnValueFormatter(self.tables[table], values))
            return res.fetchone()[0]

    def _insert(self, table: str, **values):
        assert not self.bot.db_closed
        assert self.tables
        assert table in self.tables
        assert values
        assert all(k in self.tables[table].keys() for k in values.keys())

        c: sqlite3.Connection
        with connwrap(self.conn) as c:
            query = (f'INSERT INTO {table} ({self._format_cols(values.keys())}) '
                     f'VALUES ({self._format_insert_vars(values.keys())})')
            # TODO: catch an exception here, but what?
            c.execute(query, values)
            self.log.debug('Executed SELECT query with parameters %s',
                           ColumnValueFormatter(self.tables[table], values))

    def _delete(self, table: str, **values) -> int:
        assert not self.bot.db_closed
        assert self.tables
        assert table in self.tables
        assert values
        assert all(k in self.tables[table].keys() for k in values.keys())

        c: sqlite3.Connection
        with connwrap(self.conn) as c:
            query = f'DELETE FROM {table} {self._format_select_vars(values.keys())}'
            # TODO: catch some exception here, probably
            # (DELETE shouldn't raise unless something has gone horribly wrong)
            res = c.execute(query, values)
            self.log.debug('Executed DELETE query with parameters %s',
                           ColumnValueFormatter(self.tables[table], values))
            return res.rowcount
