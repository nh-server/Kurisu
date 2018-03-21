from datetime import datetime
from typing import Tuple, Generator, NamedTuple, Optional

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
            self.log.debug('Added warning %d to user id %d, %r', now, user_id, reason)
        count = self._row_count(user_id=user_id.to_bytes(8, 'big'))
        return res, count

    def get_warnings(self, user_id: int) -> Generator[WarnEntry, None, None]:
        """Get warnings for a user id."""
        assert isinstance(user_id, int)
        res = self._select(user_id=user_id)
        for snowflake, w_user_id, issuer, reason in self._select(user_id=user_id.to_bytes(8, 'big')):
            yield WarnEntry(user_id=int.from_bytes(w_user_id, 'big'), warn_id=int.from_bytes(snowflake, 'big'),
                            date=snowflake_time(int.from_bytes(snowflake, 'big')), issuer=int.from_bytes(issuer, 'big'),
                            reason=reason)

    def get_warning(self, warn_id: int) -> Optional[WarnEntry]:
        """Get a specific warning based on warn id."""
        assert isinstance(warn_id, int)
        try:
            res = next(self._select(snowflake=warn_id.to_bytes(8, 'big')))
        except StopIteration:
            return None
        return WarnEntry(user_id=int.from_bytes(res[1], 'big'), warn_id=int.from_bytes(res[0], 'big'),
                         date=snowflake_time(int.from_bytes(res[0], 'big')), issuer=int.from_bytes(res[2], 'big'),
                         reason=res[3])

    def delete_warning(self, warn_id: int) -> Tuple[bool, Optional[WarnEntry]]:
        """Remove a warning based on warn id."""
        assert isinstance(warn_id, int)
        res_warning = self.get_warning(warn_id=warn_id)
        if res_warning is None:
            return False, None
        res_delete = self._delete(snowflake=warn_id.to_bytes(8, 'big'))
        if res_delete:
            self.log.debug('Removed warning %d', warn_id)
        return res_delete, res_warning

    def delete_all_warnings(self, user_id: int) -> bool:
        """Delete all warnings for a user id."""
        assert isinstance(user_id, int)
        res = self._delete(user_id=user_id.to_bytes(8, 'big'))
        if res:
            self.log.debug('Removed all warnings for %d', user_id)
        return res
