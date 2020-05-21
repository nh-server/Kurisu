import discord


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
