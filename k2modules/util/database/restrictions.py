from typing import Generator, Tuple

from .common import BaseDatabaseManager


class RestrictionsDatabaseManager(BaseDatabaseManager):
    """Manages the restrictions database."""

    async def add_restriction(self, user_id: int, role_id: str) -> bool:
        """Add a restriction to the user id."""
        # TODO: check if the role exists in this function
        assert isinstance(user_id, int)
        assert isinstance(role_id, int)
        res = await self._insert('permanent_roles', user_id=user_id, restriction=role_id)
        if res:
            self.log.info('Added permanent role to user id %d: %s', user_id, role_id)
        return res

    async def remove_restriction(self, user_id: int, role_id: int) -> bool:
        """Remove a restriction from the user id."""
        assert isinstance(user_id, int)
        res = await self._delete('permanent_roles', user_id=user_id, restriction=role_id)
        if res:
            self.log.info('Removed permanent role from user id %d: %s', user_id, role_id)
        return bool(res)

    async def get_restrictions(self, user_id: int) -> Generator[Tuple[int, int], None, None]:
        """Get restrictions for a user id."""""
        assert isinstance(user_id, int)
        async for r in self._select('permanent_roles', user_id=user_id):
            yield r
