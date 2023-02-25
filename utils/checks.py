import discord

from discord import app_commands
from discord.ext import commands
from utils.configuration import StaffRank
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kurisu import Kurisu


class InsufficientStaffRank(commands.CheckFailure):
    message: str


def is_staff(role: str):
    async def predicate(ctx: commands.Context):
        if check_staff(ctx.bot, role, ctx.author.id) or (ctx.guild and ctx.author == ctx.guild.owner):
            return True
        raise InsufficientStaffRank(f"You must be at least {role} to use this command.")
    return commands.check(predicate)


def is_staff_app(role: str):
    async def predicate(interaction: discord.Interaction) -> bool:
        if (interaction.guild and interaction.user == interaction.guild.owner) or check_staff(interaction.client, role, interaction.user.id):  # type: ignore
            return True
        raise InsufficientStaffRank(f"You must be at least {role} to use this command.")
    return app_commands.check(predicate)


def check_staff(bot: 'Kurisu', role: str, user_id: int) -> bool:
    position = bot.configuration.staff.get(user_id)
    if not position and bot.configuration.helpers.get(user_id):
        position = StaffRank.Helper
    if position is None:
        return False
    return position <= StaffRank[role]


async def check_bot_or_staff(ctx: commands.Context | discord.Interaction, target: discord.Member | discord.User, action: str):
    bot: 'Kurisu' = ctx.bot if isinstance(ctx, commands.Context) else ctx.client  # type: ignore
    if target.bot:
        who = "a bot"
    elif check_staff(bot, "Helper", target.id):
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
        if not check_staff(ctx.bot, 'Helper', author.id) and (ctx.bot.roles['Verified'] not in author.roles) and (
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
