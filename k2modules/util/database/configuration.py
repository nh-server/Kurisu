from typing import TYPE_CHECKING

from .common import BaseDatabaseManager

if TYPE_CHECKING:
    from typing import AsyncGenerator, Dict, Set, Tuple


class ConfigurationDatabaseManager(BaseDatabaseManager):
    """Manages the configuration database."""

    def set_flag(self, key: str, value: bool):
        pass

    async def get_all_flags(self) -> 'AsyncGenerator[Tuple[str, bool], None]':
        async for k, v in self._select('flags'):
            yield k, bool(v)

    async def set_staff_level(self, user_id: int, level: str):
        pass

    async def delete_staff(self, user_id: int):
        pass

    async def get_all_staff_levels(self) -> 'Dict[int, str]':
        ret = {}
        async for snowflake, level in self._select('staff'):
            ret[snowflake] = level
        return ret

    async def add_nofilter_channel(self, channel_id: int):
        pass

    async def get_all_nofilter_channels(self) -> 'Set[int]':
        return set()
