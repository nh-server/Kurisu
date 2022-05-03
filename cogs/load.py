from __future__ import annotations

import discord

from discord.ext import commands
from typing import TYPE_CHECKING
from utils.checks import is_staff

if TYPE_CHECKING:
    from kurisu import Kurisu


class Load(commands.Cog):
    """
    Load commands.
    """
    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.emoji = discord.PartialEmoji.from_str('⌨')

    async def cog_check(self, ctx: commands.Context):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        return True

    @is_staff("OP")
    @commands.command(hidden=True)
    async def load(self, ctx: commands.Context, *, module: str):
        """Loads a Cog."""
        try:
            if module[0:7] != "cogs.":
                module = "cogs." + module
            await self.bot.load_extension(module)
            await ctx.send('✅ Extension loaded.')
        except Exception as e:
            await ctx.send(f'💢 Failed!\n```\n{type(e).__name__}: {e}\n```')

    @is_staff("OP")
    @commands.command(hidden=True)
    async def unload(self, ctx: commands.Context, *, module: str):
        """Unloads a Cog."""
        try:
            if module[0:7] != "cogs.":
                module = "cogs." + module
            if module == "cogs.load":
                await ctx.send("❌ I don't think you want to unload that!")
            else:
                await self.bot.unload_extension(module)
                await ctx.send('✅ Extension unloaded.')
        except Exception as e:
            await ctx.send(f'💢 Failed!\n```\n{type(e).__name__}: {e}\n```')

    @is_staff("OP")
    @commands.command(name='reload')
    async def _reload(self, ctx: commands.Context, *, module: str):
        """Reloads a Cog."""
        try:
            if module[0:7] != "cogs.":
                module = "cogs." + module
            await self.bot.reload_extension(module)
            await ctx.send('✅ Extension reloaded.')
        except Exception as e:
            await ctx.send(f'💢 Failed!\n```\n{type(e).__name__}: {e}\n```')


async def setup(bot):
    await bot.add_cog(Load(bot))
