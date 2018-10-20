from typing import TYPE_CHECKING

from discord.ext import commands

# some of this is from Luc#5653's help, who got it from RoboDanny


def is_staff():
    """Check if the user is staff."""
    async def predicate(ctx: commands.Context):
        return (await ctx.bot.get_role_by_name('staff-role')) in ctx.author.roles

    return commands.check(predicate)


def is_helper():
    """Check if the user is a part of helpers."""
    async def predicate(ctx: commands.Context):
        return (await ctx.bot.get_role_by_name('helpers-role')) in ctx.author.roles

    return commands.check(predicate)


# could is_staff and is_helper be combined?
def is_helper_or_staff():
    """Check if the user is a part of helpers or staff."""
    async def predicate(ctx: commands.Context):
        return ((await ctx.bot.get_role_by_name('helpers-role')) in ctx.author.roles
                or await ctx.bot.get_role_by_name('staff-role') in ctx.author.roles)

    return commands.check(predicate)
