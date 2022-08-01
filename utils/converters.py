import discord

from datetime import datetime
from discord import app_commands, Member
from discord.ext.commands import BadArgument, MemberConverter, ObjectConverter, Context, Converter, ObjectNotFound
from utils.utils import parse_date, parse_time
from typing import NamedTuple, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional


class OptionalMember(NamedTuple):
    id: int
    member: 'Optional[Member]' = None

    @property
    def display_if_exist(self) -> str:
        if self.member is None:
            return 'ID ' + str(self.id)
        return str(self.member)


class MemberOrID(Converter):
    async def convert(self, ctx: 'Context', argument: str) -> 'OptionalMember':
        member: Optional[Member] = None
        try:
            member = await MemberConverter().convert(ctx, argument)
            member_id: int = member.id
        except BadArgument:
            try:
                member_id = int(argument)
            except ValueError:
                raise BadArgument(f"Couldn't convert {argument!r} into a Member or int")

        return OptionalMember(member_id, member)


class DateOrTimeToSecondsConverter(Converter):
    async def convert(self, ctx: Context, arg: str):
        if (datetime_obj := parse_date(arg)) is not None:
            return int((datetime_obj - datetime.utcnow()).total_seconds())
        elif (seconds := parse_time(arg)) != -1:
            return seconds
        raise BadArgument("Invalid date/time format")


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
        if (datetime_obj := parse_date(value)) is not None:
            return datetime_obj
        raise app_commands.TransformerError("Invalid time format", discord.AppCommandOptionType.string, cls)


# Javascript is a cursed language
class HackIDTransformer(app_commands.Transformer):
    @classmethod
    async def transform(cls, interaction: discord.Interaction, value: str) -> int:
        ctx = await Context.from_interaction(interaction)
        try:
            discord_object = await ObjectConverter().convert(ctx, value)
            return discord_object.id
        except ObjectNotFound:
            raise app_commands.TransformerError("Invalid ID", discord.AppCommandOptionType.string, cls)
