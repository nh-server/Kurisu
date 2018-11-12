from collections import OrderedDict
from datetime import datetime
from typing import NamedTuple, TYPE_CHECKING

from discord.utils import time_snowflake, snowflake_time

from ..tools import u2s, s2u
from .common import BaseDatabaseManager

if TYPE_CHECKING:
    from typing import Tuple, Generator, Optional


class WarnEntry(NamedTuple):
    user_id: int
    warn_id: int
    date: datetime
    issuer: int
    reason: str


tables = {'warns': OrderedDict((('warn_id', 'int'), ('user_id', 'int'), ('issuer', 'int'), ('reason', 'text')))}


class WarnsDatabaseManager(BaseDatabaseManager, tables=tables):
    """Manages the warns database."""

    def add_warning(self, user_id: int, issuer: int, reason: str) -> 'Tuple[int, int]':
        """Add a warning to the user id."""
        assert isinstance(user_id, int), type(user_id)
        assert isinstance(reason, str), type(str)
        now = time_snowflake(datetime.now())
        self._insert('warns', warn_id=u2s(now), user_id=u2s(user_id), issuer=u2s(issuer), reason=reason)
        self.log.debug('Added warning %d to user id %d, %r', now, user_id, reason)
        count = self._row_count('warns', user_id=u2s(user_id))
        return now, count

    def get_warnings(self, user_id: int) -> 'Generator[WarnEntry, None, None]':
        """Get warnings for a user id."""
        assert isinstance(user_id, int)
        for warn_id, w_user_id, issuer, reason in self._select('warns', user_id=u2s(user_id)):
            yield WarnEntry(user_id=s2u(w_user_id),
                            warn_id=s2u(warn_id),
                            date=snowflake_time(s2u(warn_id)),
                            issuer=s2u(issuer),
                            reason=reason)

    def get_warning(self, warn_id: int) -> 'Optional[WarnEntry]':
        """Get a specific warning based on warn id."""
        assert isinstance(warn_id, int)
        try:
            res = next(self._select('warns', warn_id=u2s(warn_id)))
        except StopIteration:
            return
        return WarnEntry(user_id=s2u(res[1]),
                         warn_id=s2u(res[0]),
                         date=snowflake_time(s2u(res[0])),
                         issuer=s2u(res[2]),
                         reason=res[3])

    def delete_warning(self, warn_id: int) -> 'Tuple[int, Optional[WarnEntry]]':
        """Remove a warning based on warn id."""
        assert isinstance(warn_id, int)
        res_warning = self.get_warning(warn_id=warn_id)
        if res_warning is None:
            return False, None
        res_delete = self._delete('warns', warn_id=u2s(warn_id))
        if res_delete:
            self.log.debug('Removed warning %d', warn_id)
        return res_delete, res_warning

    def delete_all_warnings(self, user_id: int) -> int:
        """Delete all warnings for a user id."""
        assert isinstance(user_id, int)
        res = self._delete('warns', user_id=u2s(user_id))
        if res:
            self.log.debug('Removed all warnings for %d', user_id)
        return res
