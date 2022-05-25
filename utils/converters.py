import discord

from discord import app_commands
from discord.ext import commands
from utils.utils import parse_date, parse_time


class DateOrTimeConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, arg: str):
        if (seconds := parse_date(arg)) != -1:
            return seconds
        elif (seconds := parse_time(arg)) != -1:
            return seconds
        raise commands.BadArgument("Invalid date/time format")


class TimeTransformer(app_commands.Transformer):
    @classmethod
    async def transform(cls, interaction: discord.Interaction, value: str) -> int:
        seconds = parse_time(value)
        if seconds > 0:
            return seconds
        raise app_commands.TransformerError("Invalid time format", discord.AppCommandOptionType.integer, cls)
