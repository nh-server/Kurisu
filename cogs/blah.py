from __future__ import annotations

import discord

from discord.ext import commands
from typing import TYPE_CHECKING
from utils.checks import is_staff
from utils.utils import send_dm_message

if TYPE_CHECKING:
    from kurisu import Kurisu


class Blah(commands.Cog):
    """
    Custom Cog to make announcements.
    """
    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.emoji = discord.PartialEmoji.from_str('🗣️')

    speak_blacklist = [
        647348710602178560,  # #minecraft-console
    ]

    @is_staff("OP")
    @commands.command()
    async def announce(self, ctx: commands.Context, *, inp):
        """Posts a message to the announcement channel."""
        await self.bot.channels['announcements'].send(inp, allowed_mentions=discord.AllowedMentions(everyone=True, roles=True))

    @is_staff("OP")
    @commands.command()
    async def speak(self, ctx: commands.Context, channel: discord.TextChannel, *, inp):
        """Sends a message to a channel."""
        if channel.id in self.speak_blacklist:
            await ctx.send(f'You cannot send a message to {channel.mention}.')
            return
        await channel.send(inp, allowed_mentions=discord.AllowedMentions(everyone=True, roles=True))

    @is_staff("OP")
    @commands.command()
    async def sendtyping(self, ctx: commands.Context, channel: discord.TextChannel = commands.CurrentChannel):
        """Triggers typing on a channel."""
        if channel.id in self.speak_blacklist:
            await ctx.send(f'You cannot send a message to {channel.mention}.')
            return
        await channel.typing()

    @is_staff("Owner")
    @commands.command()
    async def dm(self, ctx: commands.Context, member: discord.Member, *, inp):
        """Sends a message to the member."""
        await send_dm_message(member, inp, ctx)


async def setup(bot):
    await bot.add_cog(Blah(bot))
