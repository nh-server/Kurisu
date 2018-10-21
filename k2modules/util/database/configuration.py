from collections import OrderedDict
from typing import TYPE_CHECKING

from ..tools import s2i
from .common import BaseDatabaseManager

if TYPE_CHECKING:
    from typing import Generator, Tuple

# I can't really think of a use for this... maybe I'll remove it if nothing happens.

tables = {'flags': OrderedDict((('key', 'text'), ('value', 'bool'))),
          'staff': OrderedDict((('user_id', 'blob'), ('level', 'text'))),
          'nofilter': OrderedDict((('channel_id', 'blob'),))}


class ConfigurationDatabaseManager(BaseDatabaseManager, tables=tables):
    """Manages the configuration database."""

    def set_flag(self, key: str, value: bool):
        pass

    def get_all_flags(self) -> 'Generator[Tuple[str, bool], None, None]':
        for k, v in self._select('flags'):
            yield k, bool(v)

    def set_staff_level(self, user_id: int, level: str):
        pass

    def delete_staff(self, user_id: int):
        pass

    def get_all_staff_levels(self) -> 'Generator[Tuple[int, str], None, None]':
        for snowflake, level in self._select('staff'):
            yield s2i(snowflake), level

    def add_nofilter_channel(self, channel_id: int):
        pass

    def get_all_nofilter_channels(self) -> 'Generator[int, None, None]':
        yield 0
