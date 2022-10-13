from __future__ import annotations

import discord

from discord.ext import commands
from typing import TYPE_CHECKING, Optional
from utils.checks import is_staff
from textwrap import wrap

if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.context import KurisuContext, GuildContext


class Modwatch(commands.Cog):
    """
    User watch management commands.
    """

    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.emoji = discord.PartialEmoji.from_str('👀')
        self.configuration = bot.configuration
        self.logs = bot.logs

    async def cog_check(self, ctx: KurisuContext):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        return True

    @is_staff("Helper")
    @commands.command()
    async def watch(self, ctx: GuildContext, member: discord.Member, *, reason: Optional[str]):
        """Adds a member to the watchlist."""
        if member.id in self.configuration.watch_list:
            await ctx.send("User is already being watched!")
            return
        await self.configuration.set_watch(member.id, True)
        await ctx.send(f"{member.mention} is now being watched.")
        await self.logs.post_action_log(ctx.author, member, 'watch', reason=reason)

    @is_staff("Helper")
    @commands.command()
    async def unwatch(self, ctx: GuildContext, member: discord.Member):
        """Removes a member from the watchlist."""
        if member.id not in self.configuration.watch_list:
            await ctx.send("This user was not being watched.")
            return
        await self.configuration.set_watch(member.id, False)
        await ctx.send(f"{member.mention} is no longer being watched.")
        await self.logs.post_action_log(ctx.author, member, 'unwatch')

    @is_staff("Helper")
    @commands.command()
    async def listwatch(self, ctx: GuildContext):
        """List the members in the watchlist."""
        lines = []
        for user_id in self.configuration.watch_list:
            member = ctx.guild.get_member(user_id)
            lines.append(f"{f'{member.name}' if member else f'<@{user_id}>'} ({user_id})")
        messages = wrap('\n'.join(lines), 1810, break_long_words=False, replace_whitespace=False)
        if not messages:
            await ctx.send("The watchlist is empty!")
            return
        if (n_messages := len(messages)) > 1:
            for n, message in enumerate(messages, start=1):
                await ctx.author.send(f"**Watchlist contents {n}/{n_messages}**\n{message}")
        else:
            await ctx.author.send(f"**Watchlist contents**\n{messages[0]}")

    @is_staff("OP")
    @commands.command()
    async def watch_cleanup(self, ctx: GuildContext):
        """Removes members that aren't in the server from the watchlist."""
        removed = 0
        for user_id in self.configuration.watch_list:
            if not ctx.guild.get_member(user_id):
                await self.configuration.set_watch(user_id, False)
                removed += 1
        await ctx.send(f"Watch list cleanup complete. Removed {removed} entries.")


async def setup(bot):
    await bot.add_cog(Modwatch(bot))
