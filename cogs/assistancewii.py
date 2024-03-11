from __future__ import annotations

import logging
from os.path import dirname, join

from discord.ext import commands

from utils.mdcmd import add_md_files_as_commands

logger = logging.getLogger(__name__)


class AssistanceWii(commands.GroupCog):
    """
    Wii help commands that will mostly be used in the help channels.
    """
    data_dir = join(dirname(__file__), 'assistance-cmds')


add_md_files_as_commands(AssistanceWii, console_cmd="wii")


async def setup(bot):
    await bot.add_cog(AssistanceWii(bot))
