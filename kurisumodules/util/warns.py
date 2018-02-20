from datetime import datetime
from typing import Tuple, Generator, NamedTuple

from discord.utils import time_snowflake, snowflake_time

from .dbcommon import DatabaseManager


class WarnEntry(NamedTuple):
    user_id: int
    warn_id: int
    date: datetime
    issuer: int
    reason: str


class WarnsManager(DatabaseManager, table='warns', columns={'snowflake': 'blob', 'user_id': 'integer',
                                                            'issuer': 'text', 'reason': 'text'}):
    """Manages user warnings."""

    # TODO: WarnsManager

    def add_warning(self, user_id: int, issuer: int, reason: str) -> Tuple[bool, int]:
        """Add a warning to the user id."""
        assert isinstance(user_id, int)
        assert isinstance(reason, str)
        now = time_snowflake(datetime.now())
        res = self._insert(allow_duplicates=True, snowflake=now.to_bytes(8, 'big'), user_id=user_id.to_bytes(8, 'big'),
                           issuer=issuer.to_bytes(8, 'big'), reason=reason)
        if res:
            self.log.info('Added warning to user id %d, %r', user_id, reason)
        count = self._row_count(user_id=user_id.to_bytes(8, 'big'))
        return res, count

    def get_warnings(self, user_id: int) -> Generator[WarnEntry, None, None]:
        assert isinstance(user_id, int)
        res = self._select(user_id=user_id)
        for snowflake, user_id, issuer, reason in self._select(user_id=user_id):
            yield WarnEntry(user_id=int.from_bytes(user_id), warn_id=int.from_bytes(snowflake, 'big'), date=snowflake_time(snowflake),
                            issuer=issuer, reason=reason)


