import kurisu2  # for type hinting
from .dbcommon import DatabaseManager


class RestrictionsManager(DatabaseManager):
    """Manages user restrictions."""

    def __init__(self, bot: kurisu2.Kurisu2, database_path: str):
        self.log.debug('Initializing %s', type(self).__name__)
        super().__init__('restrictions', bot, database_path)
        self._create_tables((('user id', 'integer'), ('restriction', 'text')))

    def add_restriction(self, user_id: int, restriction: str) -> bool:
        """Add a restriction to the user id."""
        # TODO: check if the role exists in this function
        assert isinstance(user_id, int)
        res = self._insert(user_id, restriction)
        if res:
            self.log.info('Added restriction to user id %d: %s', user_id, restriction)
        return res

    def remove_restriction(self, user_id: int, restriction: str) -> bool:
        """Remove a restriction from the user id."""
        assert isinstance(user_id, int)
        res = self._delete(user_id, restriction)
        if res:
            self.log.info('Removed restriction from user id %d: %s', user_id, restriction)
        return res
