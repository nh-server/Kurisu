from datetime import datetime
from typing import TYPE_CHECKING, NamedTuple

from discord.utils import time_snowflake, snowflake_time

from .common import BaseDatabaseManager

if TYPE_CHECKING:
    from typing import AsyncGenerator, Optional


class ActionEntry(NamedTuple):
    entry_id: int
    user_id: int
    target_id: int
    date: datetime
    kind: str
    description: 'Optional[str]'
    extra: 'Optional[str]'


action_ids = [
    'ban',   # 0
    'kick',  # 1
    'warn',  # 2
]


class ActionsLogDatabaseManager(BaseDatabaseManager):
    """Manages the actions_log database."""

    async def add_entry(self, user_id: int, target_id: int, kind: str, description: str = None, extra: str = None,
                        custom_entry_id: int = None) -> int:
        """Add an action entry."""
        now = custom_entry_id or time_snowflake(datetime.now())
        await self._insert('actions_log', entry_id=now, created_at=snowflake_time(now), user_id=user_id,
                           target_id=target_id, kind=action_ids.index(kind), description=description, extra=extra)
        return now

    async def get_entries(self, *, entry_id: int = None, user_id: int = None, target_id: int = None,
                          kind: str = None) -> 'AsyncGenerator[ActionEntry, None]':
        """Get action entries."""
        values = {}
        if entry_id:
            values['entry_id'] = entry_id
        if user_id:
            values['user_id'] = user_id
        if target_id:
            values['target_id'] = target_id
        if kind:
            values['kind'] = kind
        async for action_id, user_id, target_id, kind, description, extra in self._select('actions_log', **values):
            yield ActionEntry(entry_id=(action_id),
                              user_id=(user_id),
                              target_id=(target_id),
                              date=snowflake_time(action_id),
                              kind=kind,
                              description=description,
                              extra=extra)

    async def add_attachment(self, entry_id: int, url: str):
        """Add an attachment to an action entry."""
        await self._insert('attachments', entry_id=entry_id, url=url)

    async def get_attachments(self, entry_id: int) -> 'AsyncGenerator[str, None]':
        """Get attachments for an action entry."""
        async for x in self._select('attachments', entry_id=entry_id):
            yield x[1]

    async def clear_attachments(self, entry_id: int):
        """Clear attachments for an action entry."""
        await self._delete('attachments', entry_id=entry_id)
