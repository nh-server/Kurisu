from datetime import datetime
from typing import Tuple

from discord.utils import time_snowflake

from .dbcommon import DatabaseManager


class WarnsManager(DatabaseManager, table='warns', columns={'snowflake': 'blob', 'user_id': 'integer',
                                                            'reason': 'text'}):
    """Manages user warnings."""

    # TODO: WarnsManager

    def add_warning(self, user_id: int, reason: str) -> Tuple[bool, int]:
        """Add a warning to the user id."""
        assert isinstance(user_id, int)
        now = time_snowflake(datetime.now())
        res = self._insert(allow_duplicates=True, snowflake=now.to_bytes(8, 'big'), user_id=user_id, reason=reason)
        if res:
            self.log.info('Added warning to user id %d, %r', user_id, reason)
        count = self._row_count(user_id=user_id)
        return res, count

