import datetime
import discord
import io
import random
import re
import traceback

from discord import app_commands
from discord.ext import commands
from typing import Optional, Union


class ConsoleColor(discord.Color):

    @classmethod
    def n3ds(cls):
        return cls(0xCE181E)

    @classmethod
    def wiiu(cls):
        return cls(0x009AC7)

    @classmethod
    def switch(cls):
        return cls(0xE60012)

    @classmethod
    def wii(cls):
        return cls(0x009AC7)

    @classmethod
    def legacy(cls):
        return cls(0x707070)


async def send_dm_message(member: discord.Member, message: str, ctx: Optional[commands.Context] = None, **kwargs) -> bool:
    """A helper method for sending a message to a member's DMs.

    Returns a boolean indicating success of the DM
    and notifies of the failure if ctx is supplied."""
    try:
        await member.send(message, **kwargs)
        return True
    except (discord.HTTPException, discord.Forbidden, discord.NotFound, AttributeError):
        if ctx:
            await ctx.send(f"Failed to send DM message to {member.mention}")
        return False


async def get_user(ctx: Union[commands.Context, discord.Interaction], user_id: int) -> Optional[Union[discord.Member, discord.User]]:
    if ctx.guild and (user := ctx.guild.get_member(user_id)):
        return user
    else:
        bot = ctx.bot if isinstance(ctx, commands.Context) else ctx.client
        return await bot.fetch_user(user_id)


def command_signature(command, *, prefix=".") -> str:
    """Helper method for a command signature

    Parameters
    -----------
    command: :class:`discord.ext.commands.Command`
        The command to generate a signature for
    prefix: str
        The prefix to include in the signature"""
    return f"{discord.utils.escape_markdown(prefix)}{command.qualified_name} {command.signature}"


def gen_color(seed) -> discord.Color:
    random.seed(seed)
    c_r = random.randint(0, 255)
    c_g = random.randint(0, 255)
    c_b = random.randint(0, 255)
    return discord.Color((c_r << 16) + (c_g << 8) + c_b)


def parse_time(time_string) -> int:
    """Parses a time string in dhms format to seconds"""
    # thanks Luc#5653
    units = {
        "d": 86400,
        "h": 3600,
        "m": 60,
        "s": 1
    }
    match = re.findall("([0-9]+[smhd])", time_string)  # Thanks to 3dshax server's former bot
    if not match:
        return -1
    return sum(int(item[:-1]) * units[item[-1]] for item in match)


def parse_date(date_string: str) -> Optional[datetime.datetime]:
    date_lst = date_string.split(' ')

    if len(date_lst) == 1:
        date_lst.append('00:00')
    elif len(date_lst) != 2:
        return None
    try:
        datetime_obj = datetime.datetime.strptime(' '.join(date_lst), "%Y-%m-%d %H:%M")
    except ValueError:
        return None
    return datetime_obj


def create_error_embed(ctx: Union[commands.Context, discord.Interaction], exc: Union[discord.DiscordException, app_commands.AppCommandError]) -> discord.Embed:
    app_command: bool = isinstance(ctx, discord.Interaction)
    author = ctx.user if app_command else ctx.author
    command: str = ctx.command.name if ctx.command else "unknown command"
    embed = discord.Embed(title=f"Unexpected exception in command {command}", color=0xe50730)
    trace = "".join(traceback.format_exception(etype=None, value=exc, tb=exc.__traceback__))
    if len(trace) > 4080:
        trace = trace[-4080:]
    embed.description = f'```py\n{trace}```'
    embed.add_field(name="Exception Type", value=exc.__class__.__name__)
    embed.add_field(name="Information", value=f"channel: {ctx.channel.mention if isinstance(ctx.channel, discord.TextChannel) else 'Direct Message'}\ncommand: {command}\nauthor: {author.mention}\n{f'message: {ctx.message.content}' if not app_command else ''}", inline=False)
    return embed


def paginate_message(msg: str, prefix: str = '```', suffix: str = '```', max_size: int = 2000):
    paginator = commands.Paginator(prefix=prefix, suffix=suffix, max_size=max_size)
    sep = max_size - len(prefix) - len(suffix) - 2
    for chunk in [msg[i:i + sep] for i in range(0, len(msg), sep)]:
        paginator.add_line(chunk)
    return paginator


def text_to_discord_file(text: str, *, name: str = 'output.txt'):
    encoded = text.encode("utf-8")
    return discord.File(filename=name, fp=io.BytesIO(encoded))


# https://stackoverflow.com/questions/9647202/ordinal-numbers-replacement
# but modified to be an f-string
def ordinal(n: int) -> str:
    # noinspection SpellCheckingInspection
    return f'{n}{"tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10::4]}'
