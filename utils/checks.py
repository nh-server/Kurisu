import discord

from discord import app_commands
from discord.ext import commands
from utils.crud import get_helper, get_staff_member
from typing import Union

staff_ranks = {"Owner": 0, "SuperOP": 1, "OP": 2, "HalfOP": 3, "Helper": 4}


class InsufficientStaffRank(commands.CheckFailure):
    message: str


def is_staff(role: str):
    async def predicate(ctx):
        if await check_staff(ctx.author, role) or (ctx.guild and ctx.guild.owner.id == ctx.author.id):
            return True
        raise InsufficientStaffRank(f"You must be at least {role} to use this command.")
    return commands.check(predicate)


def is_staff_app(role: str):
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.guild and interaction.user == interaction.guild.owner or check_staff(interaction.user, role):
            return True
        raise InsufficientStaffRank(f"You must be at least {role} to use this command.")
    return app_commands.check(predicate)


async def check_staff(author, role: str) -> bool:
    return await check_staff_id(role, author.id)


async def check_staff_id(role: str, user_id: int) -> bool:
    if role == "Helper":
        if await get_helper(user_id):
            return True
    if staff := await get_staff_member(user_id):
        return staff_ranks[staff.position] <= staff_ranks[role]
    return False


async def check_bot_or_staff(ctx: Union[commands.Context, discord.Interaction], target: Union[discord.Member, discord.User], action: str):
    if target.bot:
        who = "a bot"
    elif await check_staff_id("Helper", target.id):
        who = "another staffer"
    else:
        return False
    if isinstance(ctx, commands.Context):
        await ctx.send(f"You can't {action} {who} with this command!")
    else:
        await ctx.response.send_message(f"You can't {action} {who} with this command!", ephemeral=True)
    return True


def check_if_user_can_sr():
    async def predicate(ctx):
        author = ctx.author
        if not await check_staff_id('Helper', author.id) and (ctx.bot.roles['Verified'] not in author.roles) and (
                ctx.bot.roles['Trusted'] not in author.roles) and (ctx.bot.roles['Retired Staff'] not in author.roles):
            return False
        return True

    return commands.check(predicate)


def check_if_user_can_ready():
    async def predicate(ctx):
        channel = ctx.channel
        if channel != ctx.bot.channels['newcomers']:
            return False
        return True

    return commands.check(predicate)
