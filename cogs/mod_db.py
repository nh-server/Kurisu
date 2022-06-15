from __future__ import annotations

import discord

from discord.ext import commands
from typing import TYPE_CHECKING
from utils.checks import is_staff

if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.context import KurisuContext, GuildContext


class ModDB(commands.Cog):
    """
    Database management commands.
    """

    NOT_FOUND = 'Flag was not found in the database. ⚠️'

    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.emoji = discord.PartialEmoji.from_str('💾‍')
        self.configuration = self.bot.configuration

    async def cog_check(self, ctx: KurisuContext):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        return True

    @is_staff('Owner')
    @commands.command()
    async def addflag(self, ctx: GuildContext, name: str, value: bool):
        """Adds a config flag to the database. Owners only."""
        await self.configuration.add_flag(name, value)
        await ctx.send('Flag added to the database. ✅')

    @is_staff('Owner')
    @commands.command()
    async def delflag(self, ctx: GuildContext, name: str):
        """Removes a config flag from the database. Owners only."""
        if await self.configuration.get_flag(name):
            await self.configuration.delete_flag(name)
            await ctx.send('Flag removed from the database. ✅')
        else:
            await ctx.send(self.NOT_FOUND)

    @is_staff('Owner')
    @commands.command()
    async def getflag(self, ctx: GuildContext, name: str):
        """Retrieves a config flag from the database. Owners only."""
        flag = await self.configuration.get_flag(name)
        if flag is not None:
            await ctx.send(f'{name} is set to: {flag[1]}.')
        else:
            await ctx.send(self.NOT_FOUND)


async def setup(bot):
    await bot.add_cog(ModDB(bot))
