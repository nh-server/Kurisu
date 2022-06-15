from datetime import datetime
from typing import TYPE_CHECKING

from discord import Member, User
from discord.utils import format_dt

from .managerbase import BaseManager

if TYPE_CHECKING:
    from typing import Union, Optional
    from . import OptionalMember

action_messages = {
    'warn': ('\N{WARNING SIGN}', 'Warn', 'warned', {'mod-logs'}),
    'ban': ('\N{NO ENTRY}', 'Ban', 'banned', {'mod-logs'}),
    'kick': ('\N{WOMANS BOOTS}', 'Kick', 'kicked', {'mod-logs'}),
    'timeout': ('\N{SPEAKER WITH CANCELLATION STROKE}', 'Timeout', 'timed out', {'mod-logs'}),
    'no-timeout': ('\N{SPEAKER}', 'Timeout Removed', 'removed a timeout from', {'mod-logs'}),
    # specific role changes
    'mute': ('\N{SPEAKER WITH CANCELLATION STROKE}', 'Mute', 'muted', {'mod-logs'}),
    'unmute': ('\N{SPEAKER}', 'Unmute', 'unmuted', {'mod-logs'}),
    'time-mute': ('\N{SPEAKER WITH CANCELLATION STROKE}', 'Time Mute', 'muted', {'mod-logs'}),
    'take-help': ('\N{NO ENTRY SIGN}', 'Help access taken', 'took help access from', {'mod-logs', 'helpers'}),
    'give-help': ('\N{HEAVY LARGE CIRCLE}', 'Help access restored', 'restored help access for', {'mod-logs'}),
    'meta-mute': ('\N{SPEAKER WITH CANCELLATION STROKE}', 'Meta muted', 'meta muted', {'mod-logs'}),
    'meta-unmute': ('\N{SPEAKER}', 'Meta unmute', 'meta unmuted', {'mod-logs'}),
    'appeals-mute': ('\N{SPEAKER WITH CANCELLATION STROKE}', 'Appeals muted', 'appeals muted', {'mod-logs'}),
    'appeals-unmute': ('\N{SPEAKER}', 'Appeals unmute', 'appeals unmuted', {'mod-logs'}),

    'help-mute': ('\N{SPEAKER WITH CANCELLATION STROKE}', 'Help mute', 'removed speak access in help channels from', {'mod-logs'}),
    'help-unmute': ('\N{SPEAKER}', 'Appeals unmute', 'help unmuted', {'mod-logs'}),

    'give-art': ('\N{HEAVY LARGE CIRCLE}', 'Art access restore', 'restored art access for', {'mod-logs'}),
    'take-art': ('\N{NO ENTRY SIGN}', 'Art access taken', 'took art access from', {'mod-logs'}),

    'give-tech': ('\N{HEAVY LARGE CIRCLE}', 'Tech access restore', 'restored tech access for', {'mod-logs'}),
    'take-tech': ('\N{NO ENTRY SIGN}', 'Tech access taken', 'took tech access from', {'mod-logs'}),

    'give-elsewhere': ('\N{HEAVY LARGE CIRCLE}', 'Elsewhere access restored', 'restored elsewhere access for', {'mod-logs'}),
    'take-elsewhere': ('\N{NO ENTRY SIGN}', 'Elsewhere access taken', 'took elsewhere access from', {'mod-logs'}),

    'no-embed': ('\N{HEAVY LARGE CIRCLE}', 'Permission Taken', 'removed embed permissions from', {'mod-logs'}),
    'embed': ('\N{NO ENTRY SIGN}', 'Permission Restored', 'restored embed permissions for', {'mod-logs'}),

    'probate': ('\N{HEAVY LARGE CIRCLE}', 'Probated', 'probated', {'mod-logs'}),
    'unprobate': ('\N{NO ENTRY SIGN}', 'Un-probated', 'un-probated', {'mod-logs'}),

    'tempstream': ('\N{HEAVY LARGE CIRCLE}', 'Permission Granted', 'granted streaming permissions to', {'mod-logs'}),
    'no-tempstream': ('\N{NO ENTRY SIGN}', 'Permission Revoked', 'revoked streaming permissions from', {'mod-logs'}),

    'take-memes': ('\N{NO ENTRY SIGN}', 'Permission Revoked', 'revoked meme permissions from', {'mod-logs'}),

    # non-specific role changes
    'add-perm-role': ('\N{BLACK QUESTION MARK ORNAMENT}', 'Add role', 'added a permanent role to', {'mod-logs'}),
    'add-temp-role': ('\N{BLACK QUESTION MARK ORNAMENT}', 'Add role', 'added a temporary role to', {'mod-logs'}),
    'remove-role': ('\N{BLACK QUESTION MARK ORNAMENT}', 'Remove role', 'removed a role from', {'mod-logs'}),
    'test': ('\N{BLACK QUESTION MARK ORNAMENT}', 'Test action', 'performed a test action on', {'helpers'})
}

actions_extra = {
}

general_messages = {
    'member_update': 'Member Update',
}


class UserLogManager(BaseManager):
    """Manages posting logs."""

    async def post_action_log(self, author: 'Union[Member, User, OptionalMember]',
                              target: 'Union[Member, User, OptionalMember]', kind: str, reason: 'Optional[str]' = None,
                              until: 'Optional[datetime]' = None):
        member = target if isinstance(target, (Member, User)) else target.member
        emoji, action, action_description, send_channels = action_messages[kind]
        msg = [f'{emoji} **{action}**: <@!{author.id}> {action_description} <@!{target.id}>']
        if member:
            msg[0] += ' | ' + str(member)
        if until:
            now = datetime.now()
            msg[0] += f"for {until - now}, until {format_dt(until)}"
        if reason:
            msg.append(f'\N{PENCIL} __Reason__: {reason}')
        else:
            msg.append('\N{PENCIL} ___No reason provided__')
        msg_final = '\n'.join(msg)
        for m in send_channels:
            await self.bot.channels[m].send(msg_final)
