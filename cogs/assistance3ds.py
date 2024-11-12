from __future__ import annotations

import logging
from os.path import dirname, join
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from utils.mdcmd import add_md_files_as_commands
from utils.utils import KurisuCooldown, simple_embed

if TYPE_CHECKING:
    from utils.context import KurisuContext

logger = logging.getLogger(__name__)


class Assistance3DS(commands.Cog):
    """
    3DS help commands that will mostly be used in the help channels.
    """

    data_dir = join(dirname(__file__), 'assistance-cmds')

    @commands.dynamic_cooldown(KurisuCooldown(1, 30.0), commands.BucketType.channel)
    @commands.command()
    async def luma(self, ctx: KurisuContext, lumaversion=""):
        """Download links for Luma versions"""
        if len(lumaversion) >= 3 and lumaversion[0].isdigit() and lumaversion[1] == "." and lumaversion[2].isdigit():
            await simple_embed(ctx, f"Luma v{lumaversion}\nhttps://github.com/LumaTeam/Luma3DS/releases/tag/v{lumaversion}", color=discord.Color.blue())
        elif lumaversion == "latest":
            await simple_embed(ctx, "Latest Luma Version:\nhttps://github.com/LumaTeam/Luma3DS/releases/latest", color=discord.Color.blue())
        else:
            await simple_embed(ctx, "Download links for the most common Luma3DS releases:\n"
                                    "[Latest Luma](https://github.com/LumaTeam/Luma3DS/releases/latest)\n"
                                    "[Luma v7.0.5](https://github.com/LumaTeam/Luma3DS/releases/tag/v7.0.5)\n"
                                    "[Luma v7.1](https://github.com/LumaTeam/Luma3DS/releases/tag/v7.1)",
                                    color=discord.Color.blue())


add_md_files_as_commands(Assistance3DS, console_cmd="3ds")


async def setup(bot):
    await bot.add_cog(Assistance3DS(bot))
