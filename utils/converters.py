import discord

from datetime import datetime
from discord import app_commands
from discord.ext import commands
from utils.utils import parse_date, parse_time


class DateOrTimeToSecondsConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, arg: str):
        if (datetime_obj := parse_date(arg)) is not None:
            return int((datetime_obj - datetime.utcnow()).total_seconds())
        elif (seconds := parse_time(arg)) != -1:
            return seconds
        raise commands.BadArgument("Invalid date/time format")


class TimeTransformer(app_commands.Transformer):
    @classmethod
    async def transform(cls, interaction: discord.Interaction, value: str) -> int:
        seconds = parse_time(value)
        if seconds > 0:
            return seconds
        raise app_commands.TransformerError("Invalid time format", discord.AppCommandOptionType.string, cls)


class DateTransformer(app_commands.Transformer):
    @classmethod
    async def transform(cls, interaction: discord.Interaction, value: str) -> datetime:
        if(datetime_obj := parse_date(value)) is not None:
            return datetime_obj
        raise app_commands.TransformerError("Invalid time format", discord.AppCommandOptionType.string, cls)


# Javascript is a cursed language
class HackIDTransformer(app_commands.Transformer):
    @classmethod
    async def transform(cls, interaction: discord.Interaction, value: str) -> int:
        ctx = await commands.Context.from_interaction(interaction)
        try:
            discord_object = await commands.ObjectConverter().convert(ctx, value)
            return discord_object.id
        except commands.ObjectNotFound:
            raise app_commands.TransformerError("Invalid ID", discord.AppCommandOptionType.string, cls)
