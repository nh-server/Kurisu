from datetime import datetime
from typing import NamedTuple, TYPE_CHECKING

from discord.utils import time_snowflake, snowflake_time

from .common import BaseDatabaseManager

if TYPE_CHECKING:
    from typing import AsyncGenerator, Tuple, Optional


class WarnEntry(NamedTuple):
    user_id: int
    warn_id: int
    date: datetime
    issuer: int
    reason: str


class WarnsDatabaseManager(BaseDatabaseManager):
    """Manages the warns database."""

    async def add_warning(self, user_id: int, issuer: int, reason: str) -> 'Tuple[int, int]':
        """Add a warning to the user id."""
        assert isinstance(user_id, int), type(user_id)
        assert isinstance(reason, str), type(str)
        now = time_snowflake(datetime.now())
        await self._insert('warns', warn_id=now, user_id=user_id, issuer=issuer, reason=reason)
        self.log.debug('Added warning %d to user id %d, %r', now, user_id, reason)
        print('a')
        count = await self._row_count('warns', user_id=user_id)
        print('b')
        return now, count

    async def get_warnings(self, user_id: int) -> 'AsyncGenerator[WarnEntry, None]':
        """Get warnings for a user id."""
        assert isinstance(user_id, int)
        async for warn_id, w_user_id, issuer, reason in self._select('warns', user_id=user_id):
            yield WarnEntry(user_id=w_user_id,
                            warn_id=warn_id,
                            date=snowflake_time(warn_id),
                            issuer=issuer,
                            reason=reason)

    async def get_warning(self, warn_id: int) -> 'Optional[WarnEntry]':
        """Get a specific warning based on warn id."""
        assert isinstance(warn_id, int)
        async for res in self._select('warns', 1, warn_id=warn_id):
            # this should only return one
            return WarnEntry(user_id=res[1],
                             warn_id=res[0],
                             date=snowflake_time(res[0]),
                             issuer=res[2],
                             reason=res[3])

    async def delete_warning(self, warn_id: int) -> 'Tuple[int, Optional[WarnEntry]]':
        """Remove a warning based on warn id."""
        assert isinstance(warn_id, int)
        res_warning = await self.get_warning(warn_id=warn_id)
        if res_warning is None:
            return False, None
        res_delete = await self._delete('warns', warn_id=warn_id)
        if res_delete:
            self.log.debug('Removed warning %d', warn_id)
        return res_delete, res_warning

    async def delete_all_warnings(self, user_id: int) -> int:
        """Delete all warnings for a user id."""
        assert isinstance(user_id, int)
        res = await self._delete('warns', user_id=user_id)
        if res:
            self.log.debug('Removed all warnings for %d', user_id)
        return res
