from datetime import datetime
from typing import TYPE_CHECKING, NamedTuple

from discord.utils import time_snowflake, snowflake_time

from ..tools import u2s, s2u
from .common import BaseDatabaseManager

if TYPE_CHECKING:
    from typing import Generator, Optional


class ActionEntry(NamedTuple):
    entry_id: int
    user_id: int
    target_id: int
    date: datetime
    kind: str
    description: 'Optional[str]'
    extra: 'Optional[str]'


class ActionsLogDatabaseManager(BaseDatabaseManager):
    """Manages the actions_log database."""

    def add_entry(self, user_id: int, target_id: int, kind: str, description: str = None, extra: str = None,
                  custom_entry_id: int = None) -> int:
        """Add an action entry."""
        now = custom_entry_id or time_snowflake(datetime.now())
        self._insert('actions_log', entry_id=u2s(now), user_id=u2s(user_id), target_id=u2s(target_id),
                     kind=kind, description=description, extra=extra)
        return now

    def get_entries(self, *, entry_id: int = None, user_id: int = None, target_id: int = None,
                    kind: str = None) -> 'Generator[ActionEntry, None, None]':
        """Get action entries."""
        values = {}
        if entry_id:
            values['entry_id'] = u2s(entry_id)
        if user_id:
            values['user_id'] = u2s(user_id)
        if target_id:
            values['target_id'] = u2s(target_id)
        if kind:
            values['kind'] = kind
        for action_id, user_id, target_id, kind, description, extra in self._select('actions_log', **values):
            yield ActionEntry(entry_id=s2u(action_id),
                              user_id=s2u(user_id),
                              target_id=s2u(target_id),
                              date=snowflake_time(s2u(action_id)),
                              kind=kind,
                              description=description,
                              extra=extra)

    def add_attachment(self, entry_id: int, url: str):
        """Add an attachment to an action entry."""
        self._insert('attachments', entry_id=u2s(entry_id), url=url)

    def get_attachments(self, entry_id: int) -> 'Generator[str, None, None]':
        """Get attachments for an action entry."""
        yield from (x[1] for x in self._select('attachments', entry_id=u2s(entry_id)))

    def clear_attachments(self, entry_id: int):
        """Clear attachments for an action entry."""
        self._delete('attachments', entry_id=u2s(entry_id))
