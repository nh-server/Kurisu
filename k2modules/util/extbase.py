from functools import wraps
from typing import TYPE_CHECKING
from . import OptionalMember

from discord.ext.commands import Cog

if TYPE_CHECKING:
    from discord import Member
    from discord.ext.commands import Context
    from kurisu2 import Kurisu2
    from . import MemberOrID


def caller_as_default(func):
    """Return the command caller for the member argument if none was provided."""
    @wraps(func)
    async def decorator(self, ctx: 'Context', member: 'Member' = None, *args, **kwargs):
        if member is None:
            member = ctx.message.author
        return await func(self, ctx, member, *args, **kwargs)
    return decorator


def caller_id_as_default(func):
    """Return the command caller for the member argument if none was provided."""
    @wraps(func)
    async def decorator(self, ctx: 'Context', member: 'MemberOrID' = None, *args, **kwargs):
        if member is None:
            member = OptionalMember(ctx.message.author.id, ctx.message.author)
        return await func(self, ctx, member, *args, **kwargs)
    return decorator


class Extension(Cog):
    """Base class for Kurisu2 extensions."""

    def __init__(self, bot: 'Kurisu2'):
        """Initialize the extension."""
        bot.log.debug('Initializing extension %s', type(self).__name__)

        self.bot = bot
        self.log = bot.log

        self.restrictions = bot.restrictions
        self.warns = bot.warns
        self.configuration = bot.configuration
