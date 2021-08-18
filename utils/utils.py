import discord
import random
import re

from discord.ext import commands


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


async def send_dm_message(member: discord.Member, message: str, ctx: commands.Context = None, **kwargs) -> bool:
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


def command_signature(command, *, prefix=".") -> str:
    """Helper method for a command signature

    Parameters
    -----------
    command: :class:`discord.ext.commands.Command`
        The command to generate a signature for
    prefix: str
        The prefix to include in the signature"""
    signature = f"{discord.utils.escape_markdown(prefix)}{command.qualified_name} {command.signature}"
    return signature


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
    seconds = 0
    match = re.findall("([0-9]+[smhd])", time_string)  # Thanks to 3dshax server's former bot
    if not match:
        return -1
    for item in match:
        seconds += int(item[:-1]) * units[item[-1]]
    return seconds


def create_error_embed(ctx, exc) -> discord.Embed:
    embed = discord.Embed(title=f"Unexpected exception in command {ctx.command}", color=0x2F3136)
    embed.add_field(name=f"{exc.__class__.__name__} Exception ", value=exc, inline=False)
    embed.add_field(name="Information", value=f"channel: {ctx.channel.mention if isinstance(ctx.channel, discord.TextChannel) else 'Direct Message'}\ncommand: {ctx.command}\nmessage: {ctx.message.content}\nuser: {ctx.author.mention}", inline=False)
    return embed


def paginate_message(msg: str, prefix: str = '```', suffix: str = '```', max_size: int = 2000):
    paginator = commands.Paginator(prefix=prefix, suffix=suffix, max_size=max_size)
    sep = max_size - len(prefix) - len(suffix) - 2
    for chunk in [msg[i:i + sep] for i in range(0, len(msg), sep)]:
        paginator.add_line(chunk)
    return paginator
