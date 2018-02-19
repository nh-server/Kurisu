import os.path
import sqlite3
from typing import Iterable, Tuple, Generator, KeysView, Dict, List

import kurisu2
from .tools import connwrap


class DatabaseManagerException(Exception):
    """General exception class for DatabaseManager classes."""


class ColumnValueFormatter:
    def __init__(self, columns: Iterable, values: Iterable):
        self.columns = tuple(columns)
        self.values = tuple(values)

    def __repr__(self):
        return f'ColumnValueFormatter({self.columns}, {self.values})'

    def __str__(self):
        return ", ".join(f"({x!r}, {y!r})" for x, y in zip(self.columns, self.values))


class DatabaseManager:
    """Manages sqlite3 connections and operations for Kurisu2."""

    _db_closed = False
    _columns: List[str] = None
    _full_columns: Dict[str, str] = None

    def __init__(self, bot: kurisu2.Kurisu2, database_path: str):
        self.bot = bot
        self.log = bot.log
        self.log.debug('Initializing %s', type(self).__name__)
        self.dbpath = os.path.join(bot.config_directory, database_path)
        self.log.debug('Loading sqlite3 database: %s', self.dbpath)
        self.conn = sqlite3.connect(self.dbpath)

        self._create_columns()

    # until PyCharm recognizes __init_subclass__ properly, these inspections must be disabled
    # noinspection PyMethodOverriding,PyArgumentList
    def __init_subclass__(cls, table: str, columns: Dict[str, str], **kwargs):
        super().__init_subclass__(**kwargs)
        cls.table = table
        cls._columns = list(columns.keys())
        cls._full_columns = columns

    def _create_columns(self):
        """Create the table, if it does not already exist."""
        try:
            c: sqlite3.Cursor
            with connwrap(self.conn) as c:
                cols = ', '.join(f'`{c}` {v}' for c, v in self._full_columns.items())
                c.execute(f'CREATE TABLE {self.table} ({cols})')
        except sqlite3.OperationalError:
            # table likely exists
            pass
        else:
            self.log.info('%s table created in %s', self.table, self.dbpath)

    def _format_select_vars(self, keys: KeysView[str]) -> str:
        assert all(k in self._columns for k in keys)
        if len(keys) == 0:
            return ''
        return 'WHERE ' + ' AND '.join(f'`{c}` = :{c}' for c in keys)

    def _format_insert_vars(self, keys: KeysView[str]) -> str:
        assert keys
        assert all(k in self._columns for k in keys)
        return ', '.join(f':{c}' for c in keys)

    def _format_cols(self, keys: KeysView[str]) -> str:
        assert keys
        assert all(k in self._columns for k in keys)
        return ', '.join(f'`{c}`' for c in keys)

    def _select(self, **values) -> Generator[Tuple, None, None]:
        assert not self._db_closed
        assert self._columns
        assert all(k in self._columns for k in values.keys())
        assert values
        c: sqlite3.Connection
        with connwrap(self.conn) as c:
            query = f'SELECT * FROM {self.table} {self._format_select_vars(values.keys())}'
            yield from c.execute(query, values)

    def _insert(self, *, allow_duplicates: bool = False, **values) -> bool:
        """Insert a row into the table."""
        assert not self._db_closed
        assert self._columns
        assert all(k in self._columns for k in values.keys())
        assert values
        c: sqlite3.Connection
        with connwrap(self.conn) as c:
            if not allow_duplicates:
                query = f'SELECT * FROM {self.table} {self._format_select_vars(values.keys())}'
                res = c.execute(query, values)
                if res.fetchone() is not None:
                    return False
            query = (f'INSERT INTO {self.table} ({self._format_cols(values.keys())}) '
                     f'VALUES ({self._format_insert_vars(values.keys())})')
            # TODO: catch an exception here, but what?
            c.execute(query, values)
            return True

    def _delete(self, **values) -> bool:
        """Delete a row from the table."""
        assert not self._db_closed
        assert self._columns
        assert all(k in self._columns for k in values.keys())
        assert values
        c: sqlite3.Connection
        with connwrap(self.conn) as c:
            query = f'DELETE FROM {self.table} {self._format_select_vars(*values.keys())}'
            # TODO: catch some exception here, probably
            # (DELETE shouldn't raise unless something has gone horribly wrong)
            res = c.execute(query, values)
            self.log.debug('Executed DELETE query with parameters %s', ColumnValueFormatter(self._columns, values))
            return bool(res.rowcount)

    def close(self):
        """Close the connection to the database."""
        if self._db_closed:
            return
        try:
            self.conn.commit()
            self.conn.close()
            self._db_closed = True
            self.log.debug('Unloaded sqlite3 database: %s', self.dbpath)
        except sqlite3.ProgrammingError:
            pass

    def __del__(self):
        # this will only occur during shutdown if I screwed up
        # noinspection PyBroadException
        try:
            self.close()
        except Exception:
            pass
