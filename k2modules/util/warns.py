from typing import TYPE_CHECKING

from discord import Member
from discord.errors import Forbidden

from . import BaseManager, ordinal
from .database import WarnsDatabaseManager

if TYPE_CHECKING:
    from . import OptionalMember
    from typing import Union
    from discord import User
    from kurisu2 import Kurisu2


# could this be made better?
def get_warn_action(count: int) -> str:
    if count <= 2:
        return 'nothing'
    elif count <= 4:
        return 'kick'
    else:
        return 'ban'


warn_extras = (
    # first warn
    None,
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


class WarnsManager(BaseManager):
    """Manages user warnings."""

    def __init__(self, bot: 'Kurisu2'):
        super().__init__(bot)
        self.db = WarnsDatabaseManager(bot, 'warns.sqlite3')

    async def add_warning(self, user: 'Union[Member, User, OptionalMember]', issuer: 'Member', reason: str = None,
                          send_dm: bool = True, do_action: bool = True) -> int:
        """Add a warning to a user."""
        res = self.db.add_warning(user_id=user.id, issuer=issuer.id, reason=reason)
        if isinstance(user, Member):
            if send_dm:
                guild = await self.bot.get_main_guild()
                to_send = f'You were warned on {guild.name}.'
                if reason is not None:
                    to_send += ' The given reason is: ' + reason
                to_send += f'\n\nPlease read the rules in #welcome-and-rules. This is your {ordinal(res)} warning.'
                try:
                    to_send += '\n\n' + warn_extras[res - 1]
                except (TypeError, IndexError):
                    # attempted to add None, or get a nonexistent extra
                    pass
                try:
                    await user.send(to_send)
                except Forbidden:
                    # user disabled DMs
                    pass

            if do_action:
                action = get_warn_action(res)
                if action == 'kick':
                    await user.kick(reason=f'Reached {res} warns')
                elif action == 'ban':
                    await user.ban(reason=f'Reached {res} warns')

        return res

    def delete_warning(self, warn_id: int):
        """Remove a warning from a user."""
        return self.db.delete_warning(warn_id=warn_id)

    def delete_all_warnings(self, user: 'Union[Member, User, OptionalMember]'):
        """Remove all warnings from a user."""
        return self.db.delete_all_warnings(user.id)

    def get_warnings(self, user: 'Union[Member, User, OptionalMember]'):
        """Get warnings for a user."""
        res = self.db.get_warnings(user_id=user.id)
        for w in res:
            yield w
