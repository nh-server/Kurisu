from typing import TYPE_CHECKING

from .managerbase import BaseManager
from .database import ActionsLogDatabaseManager

if TYPE_CHECKING:
    from typing import Union
    from discord import Member, User
    from .conv import OptionalMember


class ActionsLogManager(BaseManager, db_manager=ActionsLogDatabaseManager, db_filename='actions.sqlite3'):
    """Manages the action log."""

    db: ActionsLogDatabaseManager

    async def add_action_log(self, author: 'Union[Member, User, OptionalMember]',
                             target: 'Union[Member, User, OptionalMember]', kind: str, description: str = None,
                             extra: str = None, custom_entry_id: int = None, add_to_db: bool = True,
                             post_log: bool = True):
        if add_to_db:
            entry_id = self.db.add_entry(user_id=author.id, target_id=target.id, kind=kind, description=description,
                                         extra=extra, custom_entry_id=custom_entry_id)
        else:
            entry_id = None
        # logging should be in a separate module
        # but i need to figure out the best way of doing it
        if post_log:
            await self.bot.userlog.post_action_log(author=author, target=target, kind=kind, reason=description,
                                                   action_id=entry_id)
