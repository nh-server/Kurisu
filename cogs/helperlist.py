from __future__ import annotations

import discord

from discord.ext import commands
from utils.checks import is_staff
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.context import KurisuContext, GuildContext


class HelperList(commands.Cog):
    """
    Management of active helpers.
    """

    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.configuration = self.bot.configuration
        self.emoji = discord.PartialEmoji.from_str('📜')

    async def cog_check(self, ctx: KurisuContext):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        return True

    @is_staff(role='Owner')
    @commands.command()
    async def addhelper(self, ctx: GuildContext, member: discord.Member, console: str):
        """Add user as a helper. Owners only."""
        if console not in self.bot.helper_roles:
            await ctx.send(f"💢 That's not a valid position. You can use __{'__, __'.join(self.bot.helper_roles.keys())}__")
            return
        res = await self.configuration.add_helper(member, console)
        if not res:
            return await ctx.send("Failed to add helper")
        await ctx.send(f"{member.mention} is now a helper. Welcome to the party room!")

    @is_staff(role='Owner')
    @commands.command()
    async def delhelper(self, ctx: GuildContext, member: discord.Member):
        """Remove user from helpers. Owners only."""
        if member.id not in self.configuration.helpers:
            return await ctx.send("This user is not a helper!")
        await ctx.send(member.name)
        res = await self.configuration.delete_helper(member)
        if not res:
            return await ctx.send("Failed to remove helper")
        await ctx.send(f"{member.mention} is no longer a helper. Stop by some time!")

    @commands.command()
    async def helpon(self, ctx: GuildContext):
        """Gain highlighted helping role. Only needed by Helpers."""
        author = ctx.author
        if author.id not in self.configuration.helpers:
            await ctx.send("You are not listed as a helper, and can't use this.")
            return
        await author.add_roles(self.bot.helper_roles[self.configuration.helpers[author.id]])
        await ctx.send(f"{author.mention} is now actively helping.")
        msg = f"🚑 **Elevated: +Help**: {author.mention} | {author}"
        await self.bot.channels['mod-logs'].send(msg)

    @commands.command()
    async def helpoff(self, ctx: GuildContext):
        """Remove highlighted helping role. Only needed by Helpers."""
        author = ctx.author
        if author.id not in self.configuration.helpers:
            await ctx.send("You are not listed as a helper, and can't use this.")
            return
        await author.remove_roles(self.bot.helper_roles[self.configuration.helpers[author.id]])
        await ctx.send(f"{author.mention} is no longer actively helping!")
        msg = f"👎🏻 **De-Elevated: -Help**: {author.mention} | {author}"
        await self.bot.channels['mod-logs'].send(msg)

    @commands.command()
    async def listhelpers(self, ctx: GuildContext):
        """List helpers per console."""
        consoles: dict[str, list] = {}
        embed = discord.Embed()
        for console in self.bot.helper_roles.keys():
            consoles[console] = []
            for user_id, helper_console in self.configuration.helpers.items():
                if console == helper_console:
                    consoles[console].append(user_id)
            if consoles[console]:
                embed.add_field(
                    name=console,
                    value="".join(f"<@{x}>\n" for x in consoles[console]),
                    inline=False,
                )

        await ctx.send("Here is a list of our helpers:", embed=embed)


async def setup(bot):
    await bot.add_cog(HelperList(bot))
