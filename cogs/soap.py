from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

import discord
from discord.ext import commands

from utils.checks import is_staff, check_staff, InsufficientStaffRank

if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.context import GuildContext

logger = logging.getLogger(__name__)


class Soap(commands.Cog):
    """
    command group related to soaps
    """

    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.soaps_category: Optional[discord.CategoryChannel] = None
        self.bot.loop.create_task(self.setup_soap())

    async def cog_check(self, ctx: GuildContext):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        author = ctx.author
        if not check_staff(self.bot, 'Helper', author.id) and not check_staff(self.bot, 'Staff', author.id) and (self.bot.roles['crc'] not in author.roles):
            raise InsufficientStaffRank("You can't use this command.")
        return True

    async def setup_soap(self):
        await self.bot.wait_until_all_ready()
        db_channel = await self.bot.configuration.get_channel_by_name('soaps')
        if db_channel:
            channel = self.bot.guild.get_channel(db_channel[0])
            if channel and channel.type == discord.ChannelType.category:
                self.soaps_category = channel

    @is_staff('OP')
    @commands.guild_only()
    @commands.command()
    async def setsoaps(self, ctx: GuildContext, category: discord.CategoryChannel):
        """Sets the soaps category for creating channels. OP+ only."""
        await self.bot.configuration.add_channel('soaps', category)
        self.soaps_category = category
        await ctx.send("Soaps category set.")

    @commands.guild_only()
    @commands.command(aliases=["soup", "soap"])
    async def createsoap(self, ctx: GuildContext, helpee: discord.Member):
        """Creates a 🧼 help channel for a user. crc, small help, helper+ only."""
        if not self.soaps_category:
            return await ctx.send("The soaps category is not set.")
        await ctx.send("Soaps are unavailable at this time.")

    @is_staff('Helper')
    @commands.guild_only()
    @commands.command(aliases=["rinse"])
    async def deletesoap(self, ctx: GuildContext, channels: commands.Greedy[discord.TextChannel]):
        """Deletes a :soap: help channel. helper+ only."""
        if not self.soaps_category:
            return await ctx.send("The soaps category is not set.")
        await ctx.send("Soaps are unavailable at this time.")


async def setup(bot):
    await bot.add_cog(Soap(bot))
