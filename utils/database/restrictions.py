from typing import TYPE_CHECKING
from datetime import datetime

import asyncpg
from discord.utils import time_snowflake

from .common import BaseDatabaseManager

if TYPE_CHECKING:
    from asyncpg import Record
    from collections.abc import AsyncGenerator


tables = {'restrictions': ['id', 'user_id', 'type', 'end_date', 'alerted'],
          'softbans': ['id', 'user_id', 'issuer_id', 'reason']}


class RestrictionsDatabaseManager(BaseDatabaseManager, tables=tables):
    """Manages the restrictions database."""

    async def add_restriction(self, restriction_id: int, user_id: int, restriction: str) -> int:
        """Add a restriction to the user id."""
        assert isinstance(user_id, int)
        await self.bot.configuration.add_member(user_id)
        query = "INSERT INTO restrictions (id, user_id, type) VALUES ($1,$2,$3) ON CONFLICT (user_id, type) " \
                "DO UPDATE SET end_date = NULL"
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                res = await conn.execute(query, restriction_id, user_id, restriction)
        if res:
            self.log.info('Added restriction to user id %d: %s', user_id, restriction)
        return self._parse_status(res)

    async def add_timed_restriction(self, restriction_id: int, user_id: int, restriction: str, end_date: datetime) -> int:
        """Add a restriction to the user id."""
        assert isinstance(user_id, int)
        await self.bot.configuration.add_member(user_id)
        query = "INSERT INTO restrictions (id, user_id, type, end_date) VALUES ($1,$2,$3, $4) ON CONFLICT (user_id, type) " \
                "DO UPDATE SET end_date = excluded.end_date RETURNING id;"
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                tr_id: int | None = await conn.fetchval(query, restriction_id, user_id, restriction, end_date)
                self.log.debug('Added timed restriction to user id %d: %s', user_id, restriction)
        return tr_id if tr_id is not None else -1

    async def remove_restriction(self, user_id: int, restriction: str) -> int:
        """Remove a restriction from the user id."""
        assert isinstance(user_id, int)
        res = await self._delete('restrictions', user_id=user_id, type=restriction)
        if res:
            self.log.debug('Removed restriction from user id %d: %s', user_id, restriction)
        return res

    async def get_restrictions_by_user(self, user_id: int) -> 'AsyncGenerator[Record, None]':
        """Get restrictions for a user id."""""
        assert isinstance(user_id, int)
        async for r in self._select('restrictions', user_id=user_id):
            yield r

    async def get_restrictions_by_type(self, type: str) -> 'AsyncGenerator[Record, None]':
        """Get restrictions for a user id."""""
        async for r in self._select('restrictions', type=type):
            yield r

    async def get_timed_restrictions(self) -> 'AsyncGenerator[Record, None]':
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                async for r in conn.cursor("SELECT * FROM restrictions WHERE end_date IS NOT NULL"):
                    yield r

    async def set_timed_restriction_alert(self, restriction_id: int):
        return await self._update('restrictions', {'alerted': True}, id=restriction_id)

    async def add_softban(self, user_id: int, issuer_id: int, reason: str):
        await self.bot.configuration.add_member(user_id)
        now = time_snowflake(datetime.now())
        return await self._insert('softbans', id=now, user_id=user_id, issuer_id=issuer_id, reason=reason)

    async def get_softbans(self):
        async for s in self._select('softbans'):
            yield s

    async def remove_softban(self, user_id: int):
        return await self._delete('softbans', user_id=user_id)
