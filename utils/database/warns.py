from datetime import datetime, timedelta
from typing import NamedTuple, TYPE_CHECKING

import asyncpg
from discord.utils import time_snowflake, snowflake_time

from .common import BaseDatabaseManager

if TYPE_CHECKING:
    from typing import Tuple, AsyncGenerator, Optional


class WarnEntry(NamedTuple):
    user_id: int
    warn_id: int
    date: datetime
    issuer_id: int
    reason: str


tables = {'warns': ['id', 'user_id', 'issuer_id', 'reason']}


class WarnsDatabaseManager(BaseDatabaseManager, tables=tables):
    """Manages the warns database."""

    async def add_warning(self, user_id: int, issuer: int, reason: 'Optional[str]') -> 'Tuple[int, int]':
        """Add a warning to the user id."""
        assert isinstance(user_id, int), type(user_id)
        assert isinstance(reason, (str, type(None))), type(str)
        await self.bot.configuration.add_member(user_id)
        now = time_snowflake(datetime.now())
        await self._insert('warns', id=now, user_id=user_id, issuer_id=issuer, reason=reason)
        self.log.debug('Added warning %d to user id %d, %r', now, user_id, reason)
        count = await self._row_count('warns', user_id=user_id)
        return now, count

    async def get_warnings(self, user_id: int) -> 'AsyncGenerator[WarnEntry, None]':
        """Get warnings for a user id."""
        assert isinstance(user_id, int)
        async for warn_id, w_user_id, issuer, reason in self._select('warns', user_id=user_id):
            yield WarnEntry(user_id=w_user_id,
                            warn_id=warn_id,
                            date=snowflake_time(warn_id),
                            issuer_id=issuer,
                            reason=reason)

    async def get_warning(self, warn_id: int) -> 'Optional[WarnEntry]':
        """Get a specific warning based on warn id."""
        try:
            res = await self._select('warns', warn_id=warn_id).__anext__()
        except StopIteration:
            return
        return WarnEntry(user_id=res[1],
                         warn_id=res[0],
                         date=snowflake_time(res[0]),
                         issuer_id=res[2],
                         reason=res[3])

    async def get_warnings_count(self, user_id: int) -> int:
        """Get a specific warning based on warn id."""
        return await self._row_count('warns', user_id=user_id)

    async def delete_warning(self, warn_id: int) -> int:
        """Remove a warning based on warn id."""
        assert isinstance(warn_id, int)
        res = await self._delete('warns', id=warn_id)
        if res:
            self.log.debug('Removed warning %d', warn_id)
        return res

    async def delete_all_warnings(self, user_id: int) -> int:
        """Delete all warnings for a user id."""
        assert isinstance(user_id, int)
        res = await self._delete('warns', user_id=user_id)
        if res:
            self.log.debug('Removed all warnings for %d', user_id)
        return res

    async def copy_all_warnings(self, origin: int, destination: int):
        """Copies all warnings from a user id to another user id"""
        warns = []
        await self.bot.configuration.add_member(destination)
        assert (await self.get_warnings_count(origin)) + (await self.get_warnings_count(destination)) <= 5

        async for w in self.get_warnings(origin):
            snowflake = w.warn_id
            while snowflake == w.warn_id:
                time = snowflake_time(snowflake)
                snowflake = time_snowflake(time + timedelta(milliseconds=1))
            warns.append((snowflake, destination, w.issuer_id, w.reason))
        query = "INSERT INTO warns VALUES ($1,$2,$3,$4) ON CONFLICT (id) DO UPDATE SET id = excluded.id+1"
        conn: asyncpg.Connection
        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    await conn.executemany(query, warns)
        except asyncpg.UniqueViolationError:
            self.log.error("Error when copying warns", exc_info=True)
            return 0
        return len(warns)
