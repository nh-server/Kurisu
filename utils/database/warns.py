from datetime import datetime, timedelta
from typing import NamedTuple, TYPE_CHECKING

import asyncpg
from discord.utils import time_snowflake, snowflake_time

from .common import BaseDatabaseManager

if TYPE_CHECKING:
    from typing import Tuple, AsyncGenerator, Optional


class ValidWarnEntry(NamedTuple):
    warn_id: int
    user_id: int
    issuer_id: int
    reason: str
    deletion_time: None
    deletion_reason: None
    deleter: None
    state: int
    type: int

    @property
    def date(self):
        return snowflake_time(self.warn_id)


class DeletedWarnEntry(NamedTuple):
    warn_id: int
    user_id: int
    issuer_id: int
    reason: str
    deletion_time: datetime
    deletion_reason: str
    deleter: int
    state: int
    type: int

    @property
    def date(self):
        return snowflake_time(self.warn_id)


tables = {'warns': ['id', 'user_id', 'issuer_id', 'reason', 'deletion_time', 'deletion_reason', 'deleter', 'state', 'type']}


class WarnsDatabaseManager(BaseDatabaseManager, tables=tables):
    """Manages the warns database."""

    async def add_warning(self, user_id: int, issuer: int, reason: 'Optional[str]', warn_type: int) -> 'Tuple[int, int]':
        """Add a warning to the user id."""
        assert isinstance(user_id, int), type(user_id)
        assert isinstance(reason, (str, type(None))), type(str)
        await self.bot.configuration.add_member(user_id)
        now = time_snowflake(datetime.now())
        await self._insert('warns', id=now, user_id=user_id, issuer_id=issuer, reason=reason, type=warn_type)
        self.log.debug('Added warning %d to user id %d, %r', now, user_id, reason)
        count = await self.get_warnings_count(user_id=user_id)
        return now, count

    async def get_warnings(self, user_id: int) -> 'AsyncGenerator[ValidWarnEntry, None]':
        """Get valid warnings for a user id."""
        assert isinstance(user_id, int)
        conn: asyncpg.Connection

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                query = 'SELECT * FROM warns WHERE user_id = $1 AND state = 0'
                async for record in conn.cursor(query, user_id):
                    yield ValidWarnEntry(*record)

    async def get_deleted_warnings(self, user_id: int) -> 'AsyncGenerator[DeletedWarnEntry, None]':
        """Get warnings for a user id."""
        assert isinstance(user_id, int)
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                query = ('SELECT id, user_id, issuer_id, reason, type, state, deletion_time, '
                         'deletion_reason, deleter FROM warns WHERE user_id = $1 AND state IN (1,2)')
                async for record in conn.cursor(
                        query, user_id):
                    yield DeletedWarnEntry(*record)

    async def get_warning(self, warn_id: int) -> 'Optional[ValidWarnEntry|DeletedWarnEntry]':
        """Get a specific warning based on warn id."""
        res = await self._select_one('warns', id=warn_id)
        if res is None:
            return res
        if res['state'] != 0:
            return DeletedWarnEntry(*res)
        else:
            return ValidWarnEntry(*res)

    async def get_warnings_count(self, user_id: int) -> int:
        """Get a specific warning based on warn id."""
        assert isinstance(user_id, int)
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                conn: asyncpg.Connection
                query = 'SELECT COUNT(*) FROM warns WHERE user_id = $1 AND state = 0'
                value: int | None = await conn.fetchval(query, user_id)
        return value if value is not None else 0

    async def delete_warning(self, warn_id: int, deleter: 'Optional[int]', reason: 'Optional[str]', deletion_type: int) -> int:
        """Remove a warning based on warn id."""
        assert isinstance(warn_id, int)
        res = await self._update('warns',
                                 {'state': deletion_type, 'deletion_time': datetime.now(), 'deletion_reason': reason, 'deleter': deleter},
                                 id=warn_id)
        if res:
            self.log.debug('Removed warning %d', warn_id)
        return res

    async def delete_deleted_warning(self, warn_id: int) -> int:
        """Remove a warning based on warn id."""
        assert isinstance(warn_id, int)
        res = await self._delete('warns', id=warn_id)
        return res

    async def delete_all_warnings(self, user_id: int, deleter: int, reason: 'Optional[str]') -> int:
        """Delete all warnings for a user id."""
        assert isinstance(user_id, int)
        query = "UPDATE warns SET deletion_time = $1, deletion_reason = $2, deleter = $3, state = $4 WHERE user_id = $5 AND state not in (1,2)"
        args = (datetime.now(), reason, deleter, 1, user_id)
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                res = await conn.execute(query, *args)
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
            warns.append((snowflake, destination, w.issuer_id, w.reason, w.type))
        query = "INSERT INTO warns VALUES ($1,$2,$3,$4,$5) ON CONFLICT (id) DO UPDATE SET id = excluded.id+1"
        conn: asyncpg.Connection
        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    await conn.executemany(query, warns)
        except asyncpg.UniqueViolationError:
            self.log.error("Error when copying warns", exc_info=True)
            return 0
        return len(warns)

    async def get_all_ephemeral_warnings(self):
        """Get warnings for a user id."""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                query = 'SELECT * FROM warns WHERE type = 1 AND state = 0'
                async for record in conn.cursor(
                        query):
                    yield ValidWarnEntry(*record)

    async def restore_warning(self, warn_id: int):
        return await self._update('warns', {"deletion_time": None, "deletion_reason": None, "deleter": None, "state": 0, "type": 0}, id=warn_id)

    async def unpin_warning(self, warn_id):
        return await self._update('warns', {"type": 1}, id=warn_id)

    async def pin_warning(self, warn_id):
        return await self._update('warns', {"type": 0}, id=warn_id)

    async def get_warning_number(self, warn_id) -> 'Optional[int]':
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                conn: asyncpg.Connection
                query = "SELECT warn_num FROM ( SELECT id, user_id, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY id) AS warn_num FROM warns where state=0) subquery WHERE id = $1;"
                res = await conn.fetchval(query, warn_id)
                return res
