from typing import Generator, Tuple

from kurisu2 import Kurisu2
from .dbcommon import DatabaseManager


class RestrictionsManager(DatabaseManager):
    """Manages user restrictions."""

    def __init__(self, bot: Kurisu2, database_path: str):
        super().__init__('restrictions', bot, database_path)
        self._create_tables(user_id='integer', restriction='text')

    def add_restriction(self, user_id: int, restriction: str) -> bool:
        """Add a restriction to the user id."""
        # TODO: check if the role exists in this function
        assert isinstance(user_id, int)
        res = self._insert(user_id=user_id, restriction=restriction)
        if res:
            self.log.info('Added restriction to user id %d: %s', user_id, restriction)
        return res

    def remove_restriction(self, snowflake: int) -> bool:
        """Remove a restriction from the user id."""
        assert isinstance(snowflake, int)
        res = self._delete(snowflake=snowflake)
        if res:
            self.log.info('Removed restriction from user id %d: %s', user_id, restriction)
        return res

    def get_restrictions(self, user_id: int) -> Generator[Tuple, None, None]:
        """Get restrictions for a user id."""""
        assert isinstance(user_id, int)
        yield from self._select(user_id=user_id)
