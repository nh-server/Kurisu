from __future__ import annotations

import logging
from os.path import dirname, join

from discord.ext import commands

from utils.mdcmd import add_md_files_as_commands

logger = logging.getLogger(__name__)


class AssistanceSwitch(commands.Cog):
    """
    Switch help commands that will mostly be used in the help channels.
    """

    format_map = {
        'nx_firmware': '21.2.0',
        'ams_ver': '1.10.2',
        'hekate_ver': '6.5.1',
        'last_revision': 'February 24th, 2026',
    }

    # compatibility until the use of these variables is removed
    nx_firmware = format_map['nx_firmware']
    ams_ver = format_map['ams_ver']
    hekate_ver = format_map['hekate_ver']
    last_revision = format_map['last_revision']

    data_dir = join(dirname(__file__), 'assistance-cmds')


add_md_files_as_commands(AssistanceSwitch, console_cmd="switch")


async def setup(bot):
    await bot.add_cog(AssistanceSwitch(bot))
