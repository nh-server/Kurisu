import disnake
import random
import re
import traceback

from disnake.ext import commands
from typing import Optional, Union


class ConsoleColor(disnake.Color):

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


async def send_dm_message(member: disnake.Member, message: str, inter = None, **kwargs) -> bool:
    """A helper method for sending a message to a member's DMs.

    Returns a boolean indicating success of the DM
    and notifies of the failure if ctx is supplied."""
    try:
        await member.send(message, **kwargs)
        return True
    except (disnake.HTTPException, disnake.Forbidden, disnake.NotFound, AttributeError):
        if inter:
            await inter.response.send_message(f"Failed to send DM message to {member.mention}")
        return False


async def get_user(ctx: commands.Context, user_id: int) -> Optional[Union[disnake.Member, disnake.User]]:
    if ctx.guild and (user := ctx.guild.get_member(user_id)):
        return user
    else:
        return await ctx.bot.fetch_user(user_id)


def command_signature(command, *, prefix=".") -> str:
    """Helper method for a command signature

    Parameters
    -----------
    command: :class:`disnake.ext.commands.Command`
        The command to generate a signature for
    prefix: str
        The prefix to include in the signature"""
    return f"{disnake.utils.escape_markdown(prefix)}{command.qualified_name} {command.signature}"


def gen_color(seed) -> disnake.Color:
    random.seed(seed)
    c_r = random.randint(0, 255)
    c_g = random.randint(0, 255)
    c_b = random.randint(0, 255)
    return disnake.Color((c_r << 16) + (c_g << 8) + c_b)


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


def create_error_embed(inter, exc) -> disnake.Embed:
    embed = disnake.Embed(title=f"Unexpected exception in command {inter.data.name}", color=0xe50730)
    trace = "".join(traceback.format_exception(etype=None, value=exc, tb=exc.__traceback__))
    embed.description = f'```py\n{trace}```'
    embed.add_field(name="Exception Type", value=exc.__class__.__name__)
    embed.add_field(name="Information", value=f"channel: {inter.channel.mention if isinstance(inter.channel, disnake.TextChannel) else 'Direct Message'}\ncommand: {inter.application_command.name}\nauthor: {inter.author.mention}", inline=False)
    return embed


def paginate_message(msg: str, prefix: str = '```', suffix: str = '```', max_size: int = 2000):
    paginator = commands.Paginator(prefix=prefix, suffix=suffix, max_size=max_size)
    sep = max_size - len(prefix) - len(suffix) - 2
    for chunk in [msg[i:i + sep] for i in range(0, len(msg), sep)]:
        paginator.add_line(chunk)
    return paginator
