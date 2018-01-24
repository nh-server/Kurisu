import os.path
import sqlite3

from typing import Iterable, Tuple

import sys

import kurisu2
from .tools import connwrap


class DatabaseManagerException(Exception):
    """General exception class for DatabaseManager classes."""


class DatabaseManager:
    """Manages sqlite3 connections and operations for Kurisu2."""

    _db_closed = False
    _columns = None

    def __init__(self, table: str, bot: kurisu2.Kurisu2, database_path: str):
        self.bot = bot
        self.log = bot.log
        self.dbpath = os.path.join(bot.config_directory, database_path)
        self.table = table
        self.log.debug('Loading sqlite3 database: %s', self.dbpath)
        self.conn = sqlite3.connect(self.dbpath)

    def _create_tables(self, columns: Iterable[Tuple[str, str]]):
        """Create the table, if it does not already exist."""
        self._columns = [c for c, _ in columns]
        try:
            c: sqlite3.Cursor
            with connwrap(self.conn) as c:
                cols = ', '.join(f'`{c}` {v}' for c, v in columns)
                c.execute(f'CREATE TABLE {self.table} ({cols})')
        except sqlite3.OperationalError:
            # table likely exists
            pass
        else:
            self.log.info('%s table created in %s', self.table, self.dbpath)

    # TODO: make _select/_insert/_delete take columns as keyword arguments

    def _format_vars(self, length: int) -> str:
        return ' AND '.join(f'`{c}` = ?' for c in self._columns[length:])

    def _select(self, *values) -> list:
        # TODO: _select
        assert not self._db_closed
        assert self._columns
        assert values

    def _insert(self, *values, allow_duplicates=False) -> bool:
        """Insert a row into the table."""
        assert not self._db_closed
        assert self._columns
        assert values
        c: sqlite3.Connection
        with connwrap(self.conn) as c:
            if not allow_duplicates:
                query = f'SELECT * FROM {self.table} WHERE {self._format_vars(len(values))}'
                res = c.execute(query, values)
                if res.fetchone() is not None:
                    return False

    def _delete(self, *values) -> bool:
        """Delete a row from the table."""
        assert not self._db_closed
        assert self._columns
        assert values
        c: sqlite3.Connection
        with connwrap(self.conn) as c:
            query = f'DELETE FROM {self.table} WHERE {self._format_vars(len(values))}'
            # TODO: catch some exception here, probably
            # (DELETE shouldn't raise unless something has gone horribly wrong)
            res = c.execute(query, values)
            # TODO: probably make the arguments in this log call get taken from a custom class
            # (since logging doesn't format the string unless it actually gets printed)
            self.log.debug('Executed DELETE query with parameters %r', [*zip(self._columns, values)])
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
