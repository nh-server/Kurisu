import discord

from discord import app_commands
from discord.ext import commands
from utils.crud import get_helper, get_staff
from typing import Union

staff_ranks = {"Owner": 0, "SuperOP": 1, "OP": 2, "HalfOP": 3, "Helper": 4}


def is_staff(role):
    async def predicate(ctx: commands.Context) -> bool:
        return True if ctx.guild and ctx.author == ctx.guild.owner else check_staff(ctx.author, role)
    return commands.check(predicate)


def is_staff_app(role):
    async def predicate(interaction: discord.Interaction) -> bool:
        return True if interaction.guild and interaction.user == interaction.guild.owner else check_staff(interaction.user, role)
    return app_commands.check(predicate)


async def check_staff(author, role: str):
    return await check_staff_id(role, author.id)


async def check_staff_id(role: str, user_id: int):
    if role == "Helper":
        if await get_helper(user_id):
            return True
    if staff := await get_staff(user_id):
        return staff_ranks[staff.position] <= staff_ranks[role]
    return False


async def check_bot_or_staff(ctx: Union[commands.Context, discord.Interaction], target: discord.user, action: str):
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
