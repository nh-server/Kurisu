import discord
import re


async def send_dm_message(member, message) -> bool:
    """A helper method for sending a message to a member's DMs.

    Returns a boolean indicating success of the DM."""
    try:
        await member.send(message)
        return True
    except (discord.HTTPException, discord.Forbidden, discord.NotFound, AttributeError):
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
    if match is None:
        return -1
    for item in match:
        seconds += int(item[:-1]) * units[item[-1]]
    return seconds