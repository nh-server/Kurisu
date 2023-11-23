from __future__ import annotations

import logging
from os.path import dirname, join
from typing import TYPE_CHECKING

from discord.ext import commands

from utils.mdcmd import add_md_files_as_commands
from utils.utils import KurisuCooldown, simple_embed

if TYPE_CHECKING:
    from utils.context import KurisuContext

logger = logging.getLogger(__name__)


class AssistanceSwitch(commands.GroupCog):
    """
    Switch help commands that will mostly be used in the help channels.
    """

    format_map = {
        'nx_firmware': '16.0.1',
        'ams_ver': '1.5.1',
        'hekate_ver': '6.0.2',
        'last_revision': 'March 28th, 2023',
    }

    # compatibility until the use of these variables is removed
    nx_firmware = format_map['nx_firmware']
    ams_ver = format_map['ams_ver']
    hekate_ver = format_map['hekate_ver']
    last_revision = format_map['last_revision']

    data_dir = join(dirname(__file__), 'assistance-cmds')

    @commands.dynamic_cooldown(KurisuCooldown(1, 30.0), commands.BucketType.channel)
    @commands.command()
    async def nxcfw(self, ctx: KurisuContext, cfw=""):
        """Information on why we don't support or recommend various other Switch CFWs"""

        if cfw == "sx":  # Alias for sxos
            cfw = "sxos"

        cfwinfo = {
            'kosmos': {
                'info':
                    ('* Kosmos bundles several extras, including system modules which can cause issues'
                     ' with booting if they are not compatible with the currently running firmware. '
                     'As a result, troubleshooting is often required to figure out which one is causing the issue.'),
                'title': "Kosmos"
            },
            'reinx': {
                'info':
                    ('* Older versions have caused bans due to the incorrectly implemented user agent string.'
                     '* The author has expressed no interest in adding emuMMC/emuNAND.'
                     '* The author has expressed that they feel it doesn\'t matter if consoles get banned.'
                     '* It often takes weeks to several months for it to get support for the latest firmware.'),
                'title': "ReiNX"
            },
            'sxos': {
                'info':
                    (
                        '* SX OS is illegal to purchase and own. It bundles various keys and copyrighted data that cannot be legally shared.'
                        '* It has known compatibility issues with homebrew, due to its non-standard and proprietary nature.'
                        '* It does not support loading custom system modules.'
                        '* Several versions of the CFW have caused users to be banned without their knowledge.'),
                'title': "SX OS"
            }
        }

        if not (info := cfwinfo.get(cfw)):
            await ctx.send(f"Please specify a cfw. Valid options are: {', '.join(x for x in cfwinfo)}.")

            ctx.command.reset_cooldown(ctx)
            return
        await simple_embed(ctx, info['info'], title=f"Why {info['title']} isn't recommended")


add_md_files_as_commands(AssistanceSwitch, console_cmd="switch")


async def setup(bot):
    await bot.add_cog(AssistanceSwitch(bot))
