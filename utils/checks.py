import discord

from discord.ext import commands
from utils.crud import get_helper, get_staff

staff_ranks = {"Owner": 0, "SuperOP": 1, "OP": 2, "HalfOP": 3, "Helper": 4}


def is_staff(role):
    async def predicate(ctx):
        if isinstance(ctx.channel, discord.abc.GuildChannel):
            return await check_staff(ctx, role) if not ctx.author == ctx.guild.owner else True
        else:
            return await check_staff(ctx, role)

    return commands.check(predicate)


async def check_staff(ctx, role: str):
    return await check_staff_id(role, ctx.author.id)


async def check_staff_id(role: str, user_id: int):
    if role == "Helper":
        if await get_helper(user_id):
            return True
    if staff := await get_staff(user_id):
        return staff_ranks[staff.position] <= staff_ranks[role]
    return False


async def check_bot_or_staff(ctx, target: discord.user, action: str):
    if target.bot:
        who = "a bot"
    elif await check_staff_id("Helper", target.id):
        who = "another staffer"
    else:
        return False
    await ctx.send(f"You can't {action} {who} with this command!")
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
