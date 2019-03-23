from typing import TYPE_CHECKING

import aiopg

if TYPE_CHECKING:
    from typing import AsyncGenerator, KeysView, Tuple
    from kurisu2 import Kurisu2


class DatabaseManagerError(Exception):
    """General exception class for BaseDatabaseManager classes."""


class CursorManager:
    conn: aiopg.Connection
    cursor: aiopg.Cursor
    cursor_ctx = None

    def __init__(self, conn):
        self.conn = conn

    async def __aenter__(self):
        self.cursor_ctx = self.conn.cursor()
        self.cursor = await self.cursor_ctx.__aenter__()
        return self.cursor

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.cursor_ctx.__aexit__(exc_type, exc_val, exc_tb)


class ConnectionManager:
    conn: aiopg.Connection

    def __init__(self, dsn: str):
        self.dsn = dsn

    async def prepare(self):
        self.conn = await aiopg.connect(self.dsn)

    def get_cursor(self):
        return CursorManager(self.conn)


class BaseDatabaseManager:
    """Manages sqlite3 connections and operations for Kurisu2."""

    def __init__(self, bot: 'Kurisu2'):
        self.bot = bot
        self.log = bot.log
        self.db_pool = bot.db_conn

    def _format_select_vars(self, keys: 'KeysView[str]') -> str:
        assert not self.bot.db_closed

        if len(keys) == 0:
            return ''
        return 'WHERE ' + ' AND '.join(f'"{c}" = %({c})s' for c in keys)

    def _format_insert_vars(self, keys: 'KeysView[str]') -> str:
        assert not self.bot.db_closed
        assert keys

        return ', '.join(f'%({c})s' for c in keys)

    def _format_cols(self, keys: 'KeysView[str]') -> str:
        assert not self.bot.db_closed
        assert keys

        return ', '.join(f'"{c}"' for c in keys)

    async def _select(self, table: str, limit: int = None, **values) -> 'AsyncGenerator[Tuple, None]':
        assert not self.bot.db_closed

        async with self.db_pool.get_cursor() as c:
            query = f'SELECT * FROM {table} {self._format_select_vars(values.keys())}'
            if limit:
                query += ' LIMIT %i' % (limit,)
            await c.execute(query, values)
            self.log.debug('Executed SELECT query on %s with parameters %s', table, values)
            for _ in range(c.rowcount):
                yield await c.fetchone()

    async def _row_count(self, table: str, **values) -> int:
        assert not self.bot.db_closed

        async with self.db_pool.get_cursor() as c:
            query = f'SELECT COUNT(*) FROM {table} {self._format_select_vars(values.keys())}'
            await c.execute(query, values)
            self.log.debug('Executed SELECT COUNT() query on %s with parameters %s', table, values)
            return (await c.fetchone())[0]

    async def _insert(self, table: str, **values):
        assert not self.bot.db_closed
        assert values

        async with self.db_pool.get_cursor() as c:
            query = (f'INSERT INTO {table} ({self._format_cols(values.keys())}) '
                     f'VALUES ({self._format_insert_vars(values.keys())})')
            # TODO: catch an exception here, but what?
            await c.execute(query, values)
            self.log.debug('Executed INSERT query on %s with parameters %s', table, values)

    async def _delete(self, table: str, **values) -> int:
        assert not self.bot.db_closed
        assert values

        async with self.db_pool.get_cursor() as c:
            query = f'DELETE FROM {table} {self._format_select_vars(values.keys())}'
            # TODO: catch some exception here, probably
            # (DELETE shouldn't raise unless something has gone horribly wrong)
            await c.execute(query, values)
            self.log.debug('Executed DELETE query on %s with parameters %s', table, values)
            return c.rowcount
