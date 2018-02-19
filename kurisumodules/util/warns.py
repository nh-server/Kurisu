from datetime import datetime

from discord.utils import time_snowflake

from kurisu2 import Kurisu2
from .dbcommon import DatabaseManager


class WarnsManager(DatabaseManager):
    """Manages user warnings."""

    def __init__(self, bot: Kurisu2, database_path: str):
        super().__init__('warns', bot, database_path)
        self._create_tables((('snowflake', 'blob'), ('user_id', 'integer'), ('reason', 'text')))

    # TODO: WarnsManager

    def add_warning(self, user_id: int, reason: str):
        """Add a warning to the user id."""
        assert isinstance(user_id, int)
        now = time_snowflake(datetime.now())
        res = self._insert(allow_duplicates=True, snowflake=now.to_bytes(8, 'big'), user_id=user_id, reason=reason)
        if res:
            self.log.info('Added warning to user id %d, %r', user_id, reason)
        return res
