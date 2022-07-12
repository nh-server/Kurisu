from __future__ import annotations

import discord

from discord.ext import commands
from typing import TYPE_CHECKING
from utils.checks import is_staff
from utils.utils import send_dm_message

if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.context import KurisuContext


class Blah(commands.Cog):
    """
    Custom Cog to make announcements.
    """
    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.emoji = discord.PartialEmoji.from_str('🗣️')

    @is_staff("OP")
    @commands.command()
    async def announce(self, ctx: KurisuContext, *, message: str):
        """Posts a message to the announcement channel."""
        await self.bot.channels['announcements'].send(message, allowed_mentions=discord.AllowedMentions(everyone=True, roles=True))

    @is_staff("OP")
    @commands.command()
    async def speak(self, ctx: KurisuContext, channel: discord.TextChannel, *, message: str):
        """Sends a message to a channel."""
        await channel.send(message, allowed_mentions=discord.AllowedMentions(everyone=True, roles=True))

    @is_staff("OP")
    @commands.command()
    async def sendtyping(self, ctx: KurisuContext, channel: discord.TextChannel = commands.CurrentChannel):
        """Triggers typing on a channel."""
        await channel.typing()

    @is_staff("Owner")
    @commands.command()
    async def dm(self, ctx: KurisuContext, member: discord.Member, *, message: str):
        """Sends a message to the member."""
        await send_dm_message(member, message, ctx)


async def setup(bot):
    await bot.add_cog(Blah(bot))
