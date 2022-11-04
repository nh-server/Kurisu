from typing import TYPE_CHECKING

import asyncpg

import logging

if TYPE_CHECKING:
    from typing import AsyncGenerator, KeysView, Optional
    from kurisu import Kurisu
    Tables = dict[str, list[str]]

# noinspection PyUnreachableCode
if __debug__:
    from itertools import chain


class DatabaseManagerError(Exception):
    """General exception class for BaseDatabaseManager classes."""


class ColumnValueFormatter:
    def __init__(self, values: dict):
        self.columns = tuple(values.keys())
        self.values = tuple(values.values())

    def __repr__(self):
        return f'ColumnValueFormatter({self.columns}, {self.values})'

    def __str__(self):
        return ', '.join(f'({x!r}, {y!r})' for x, y in zip(self.columns, self.values))


logger = logging.getLogger(__name__)


class BaseDatabaseManager:
    """Manages operations for Kurisu."""

    tables: 'Tables'

    def __init__(self, bot: 'Kurisu'):
        self.bot = bot
        self.log = logger
        self.pool = bot.pool

    # until PyCharm recognizes __init_subclass__ properly, these inspections must be disabled
    # noinspection PyMethodOverriding,PyArgumentList
    def __init_subclass__(cls, *, tables: 'Tables', **kwargs):
        cls.tables = tables

    def _generate_id(self):
        return

    def _parse_status(self, res: str) -> int:
        split = res.split(' ')
        if len(split) == 3:
            # An insert
            _, _, row_count = split
        else:
            _, row_count = res.split(' ')
        try:
            rows = int(row_count)
        except ValueError:
            return 0
        return rows

    def _format_select_vars(self, keys: 'KeysView[str]', *, start: int = 1) -> str:
        assert not self.bot.db_closed
        assert all(k in chain.from_iterable(x for x in self.tables.values()) for k in keys)

        if len(keys) == 0:
            return ''
        return 'WHERE ' + ' AND '.join(f'{c} = ${n}' for n, c in enumerate(keys, start=start))

    def _format_insert_vars(self, keys: 'KeysView[str]', *, start: int = 1) -> str:
        assert not self.bot.db_closed
        assert keys
        assert all(k in chain.from_iterable(x for x in self.tables.values()) for k in keys)

        return ', '.join(f'${n}' for n, c in enumerate(keys, start=start))

    def _format_update_vars(self, keys: 'KeysView[str]', start: int = 1):
        assert not self.bot.db_closed
        assert keys
        assert all(k in chain.from_iterable(x for x in self.tables.values()) for k in keys)

        return 'SET ' + ', '.join(f'{c} = ${n}' for n, c in enumerate(keys, start=start))

    def _format_cols(self, keys: 'KeysView[str]') -> str:
        assert not self.bot.db_closed
        assert keys
        assert all(k in chain.from_iterable(x for x in self.tables.values()) for k in keys)

        return ', '.join(f'{c}' for c in keys)

    async def _select(self, table: str, **values) -> 'AsyncGenerator[tuple, None]':
        assert not self.bot.db_closed
        assert self.tables
        assert table in self.tables
        assert all(k in self.tables[table] for k in values.keys())

        conn: asyncpg.Connection

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                query = f'SELECT * FROM {table} {self._format_select_vars(values.keys())}'
                self.log.debug(f'Executed SELECT query in table {table} with parameters %s',
                               ColumnValueFormatter(values))
                async for record in conn.cursor(query, *values.values()):
                    yield record

    async def _select_one(self, table: str, **values) -> 'Optional[tuple]':
        assert not self.bot.db_closed
        assert self.tables
        assert table in self.tables
        assert all(k in self.tables[table] for k in values.keys())

        conn: asyncpg.Connection

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                query = f'SELECT * FROM {table} {self._format_select_vars(values.keys())}'
                self.log.debug(f'Executed SELECT query in table {table} with parameters %s',
                               ColumnValueFormatter(values))
                return await conn.fetchrow(query, *values.values())

    async def _row_count(self, table: str, **values) -> int:
        assert not self.bot.db_closed
        assert self.tables
        assert table in self.tables
        assert all(k in self.tables[table] for k in values.keys())

        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                query = f'SELECT COUNT(*) FROM {table} {self._format_select_vars(values.keys())}'
                record = await conn.fetchrow(query, *values.values())
                self.log.debug(f'Executed SELECT COUNT() query in table {table} with parameters %s',
                               ColumnValueFormatter(values))
                return record[0]

    async def _insert(self, table: str, **values) -> int:
        assert not self.bot.db_closed
        assert self.tables
        assert table in self.tables
        assert values
        assert all(k in self.tables[table] for k in values.keys())

        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                query = (f'INSERT INTO {table} ({self._format_cols(values.keys())}) '
                         f'VALUES ({self._format_insert_vars(values.keys())})')
                try:
                    res = await conn.execute(query, *values.values())
                except asyncpg.IntegrityConstraintViolationError:
                    self.log.error(f'Exception when inserting values into table {table}', exc_info=True)
                    return 0
                self.log.debug(f'Executed SELECT query in table {table} with parameters %s',
                               ColumnValueFormatter(values))
        return self._parse_status(res)

    async def _update(self, table: str, values: dict, **conditions) -> int:
        assert not self.bot.db_closed
        assert self.tables
        assert table in self.tables
        assert values
        assert all(k in self.tables[table] for k in values.keys())
        assert all(k in self.tables[table] for k in conditions.keys())
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                query = (f'UPDATE {table} {self._format_update_vars(values.keys())} '
                         f'{self._format_select_vars(conditions.keys(), start=len(values) + 1)}')
                try:
                    res = await conn.execute(query, *values. values(), *conditions.values())
                except asyncpg.IntegrityConstraintViolationError:
                    self.log.error(f'Exception when updating values in table {table}', exc_info=True)
                    return False
                self.log.debug(f'Executed UPDATE query in table {table} with parameters %s and conditions %s',
                               ColumnValueFormatter(values), ColumnValueFormatter(conditions))
        return self._parse_status(res)

    async def _delete(self, table: str, **values) -> int:
        assert not self.bot.db_closed
        assert self.tables
        assert table in self.tables
        assert all(k in self.tables[table] for k in values.keys())

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                query = f'DELETE FROM {table} {self._format_select_vars(values.keys())}'
                try:
                    res = await conn.execute(query, *values.values())
                except asyncpg.IntegrityConstraintViolationError:
                    self.log.error(f'Exception when deleting rows in table {table}', exc_info=True)
                    return 0
                self.log.debug(f'Executed DELETE query in table {table} with parameters %s',
                               ColumnValueFormatter(values))
        return self._parse_status(res)
