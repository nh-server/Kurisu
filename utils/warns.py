from enum import IntEnum
from typing import TYPE_CHECKING

from discord import Member
from discord.errors import Forbidden

from . import BaseManager, ordinal
from .database import WarnsDatabaseManager

if TYPE_CHECKING:
    from . import OptionalMember
    from typing import Tuple, Optional, Literal
    from discord import User


# could this be made better?
def get_warn_action(count: int) -> str:
    if count <= 2:
        return 'nothing'
    elif count <= 4:
        return 'kick'
    else:
        return 'ban'


class WarnType(IntEnum):
    Pinned = 0
    Ephemeral = 1


class WarnState(IntEnum):
    Valid = 0
    Deleted = 1
    Expired = 2


warn_extras = (
    # first warn
    '',
    # second warn
    'The next warn will automatically kick.',
    # third warn
    'You were kicked because of this warning. You can join again right away. Two more warnings will result in an '
    'automatic ban.',
    # fourth warn
    'You were kicked because of this warning. This is your final warning. You can join again, but **one more warn will '
    'result in a ban**.'
    # fifth warn
    'You were automatically banned due to five warnings.'
)


class WarnsManager(BaseManager, db_manager=WarnsDatabaseManager):
    """Manages user warnings."""

    db: WarnsDatabaseManager

    async def add_warning(self, user: 'Member | User | OptionalMember', issuer: 'Member', reason: 'Optional[str]' = None,
                          warn_type: WarnType = WarnType.Ephemeral, send_dm: bool = True, do_action: bool = True) -> 'Tuple[int, int]':
        """Add a warning to a user."""
        warn_id, count = await self.db.add_warning(user_id=user.id, issuer=issuer.id, reason=reason, warn_type=warn_type)
        if isinstance(user, Member):
            if send_dm:
                guild = self.bot.guild
                to_send = f'You were warned on {guild.name}.'
                if reason is not None:
                    to_send += ' The given reason is: ' + reason
                to_send += f'\n\nPlease read the rules in {self.bot.channels["welcome-and-rules"]}. This is your {ordinal(count)} warning.'
                try:
                    to_send += '\n\n' + warn_extras[count - 1]
                except (TypeError, IndexError):
                    # attempted to add None, or get a nonexistent extra
                    pass
                try:
                    await user.send(to_send)
                except Forbidden:
                    # user disabled DMs
                    pass

            if do_action:
                action = get_warn_action(count)
                if action == 'kick':
                    self.bot.actions.append(f"wk:{user.id}")
                    await user.kick(reason=f'Reached {count} warns')
                elif action == 'ban':
                    self.bot.actions.append(f"wb:{user.id}")
                    await user.ban(reason=f'Reached {count} warns', delete_message_days=0)

        return warn_id, count

    async def delete_warning(self, warn_id: int, deleter: 'Optional[int]', reason: 'Optional[str]', deletion_type: 'Literal[WarnState.Deleted, WarnState.Expired]' = WarnState.Deleted):
        """Remove a warning from a user."""
        return await self.db.delete_warning(warn_id=warn_id, deleter=deleter, reason=reason, deletion_type=deletion_type)

    async def delete_deleted_warning(self, warn_id: int):
        """Remove a deleted warning from a user permanently."""
        return await self.db.delete_deleted_warning(warn_id=warn_id)

    async def delete_all_warnings(self, user: 'Member | User | OptionalMember', deleter: Member, reason: 'Optional[str]'):
        """Remove all warnings from a user."""
        return await self.db.delete_all_warnings(user.id, deleter.id, reason)

    async def get_warnings(self, user: 'Member | User | OptionalMember'):
        """Get warnings for a user."""
        async for w in self.db.get_warnings(user_id=user.id):
            yield w

    async def get_all_ephemeral_warnings(self):
        """Gets all ephemeral warnings."""
        async for w in self.db.get_all_ephemeral_warnings():
            yield w

    async def get_deleted_warnings(self, user: 'Member | User | OptionalMember'):
        """Get deleted warnings for a user."""
        async for w in self.db.get_deleted_warnings(user_id=user.id):
            yield w

    async def get_warnings_count(self, user: 'Member | User | OptionalMember') -> int:
        """Get warnings count for a user."""
        return await self.db.get_warnings_count(user.id)

    async def copy_warnings(self, origin: 'Member | User | OptionalMember', destination: 'Member | User | OptionalMember') -> int:
        """Copy warning from a user to another user"""
        return await self.db.copy_all_warnings(origin.id, destination.id)
