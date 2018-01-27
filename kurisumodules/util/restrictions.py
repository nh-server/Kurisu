from datetime import datetime
from typing import Generator, Tuple

from discord.utils import snowflake_time, time_snowflake

from kurisu2 import Kurisu2
from .dbcommon import DatabaseManager


class RestrictionsManager(DatabaseManager):
    """Manages user restrictions."""

    def __init__(self, bot: Kurisu2, database_path: str):
        super().__init__('restrictions', bot, database_path)
        self._create_tables((('snowflake', 'integer'), ('user_id', 'integer'), ('restriction', 'text')))

    def add_restriction(self, user_id: int, restriction: str) -> bool:
        """Add a restriction to the user id."""
        # TODO: check if the role exists in this function
        assert isinstance(user_id, int)
        now = time_snowflake(datetime.now())
        res = self._insert(snowflake=now, user_id=user_id, restriction=restriction)
        if res:
            self.log.info('Added restriction to user id %d: %s', user_id, restriction)
        return res

    def remove_restriction(self, user_id: int, restriction: str) -> bool:
        """Remove a restriction from the user id."""
        assert isinstance(user_id, int)
        res = self._delete(user_id=user_id, restriction=restriction)
        if res:
            self.log.info('Removed restriction from user id %d: %s', user_id, restriction)
        return res

    def get_restrictions(self, user_id: int) -> Generator[Tuple, None, None]:
        pass  # TODO: get_restrictions
