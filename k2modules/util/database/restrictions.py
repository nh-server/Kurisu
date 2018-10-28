from collections import OrderedDict
from typing import Generator, Tuple

from k2modules.util.tools import u2s
from .common import BaseDatabaseManager

tables = {'restrictions': OrderedDict((('user_id', 'int'), ('restriction', 'text')))}


class RestrictionsDatabaseManager(BaseDatabaseManager, tables=tables):
    """Manages the restrictions database."""

    def add_restriction(self, user_id: int, restriction: str) -> bool:
        """Add a restriction to the user id."""
        # TODO: check if the role exists in this function
        assert isinstance(user_id, int)
        res = self._insert('restrictions', user_id=u2s(user_id), restriction=restriction)
        if res:
            self.log.info('Added restriction to user id %d: %s', user_id, restriction)
        return res

    def remove_restriction(self, user_id: int, restriction: str) -> bool:
        """Remove a restriction from the user id."""
        assert isinstance(user_id, int)
        res = bool(self._delete('restrictions', user_id=u2s(user_id), restriction=restriction))
        if res:
            self.log.info('Removed restriction from user id %d: %s', user_id, restriction)
        return res

    def get_restrictions(self, user_id: int) -> Generator[Tuple[int, str], None, None]:
        """Get restrictions for a user id."""""
        assert isinstance(user_id, int)
        yield from self._select('restrictions', user_id=u2s(user_id))
