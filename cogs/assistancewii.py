from __future__ import annotations

import logging
from os.path import dirname, join
from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from markdownify import markdownify

from utils.mdcmd import add_md_files_as_commands
from utils.utils import ConsoleColor, KurisuCooldown

if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.context import KurisuContext

logger = logging.getLogger(__name__)


class AssistanceWii(commands.GroupCog):
    """
    Wii help commands that will mostly be used in the help channels.
    """
    data_dir = join(dirname(__file__), 'assistance-cmds')

    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot

    @commands.dynamic_cooldown(KurisuCooldown(1, 30.0), commands.BucketType.channel)
    @commands.command(aliases=["wfcerror"])
    async def wiierror(self, ctx: KurisuContext, error: int):
        """
        Get information about an error code displayed on the Wii and/or the Nintendo WFC.
        Usage: `wiierror <error code>`
        """
        # It seems error codes must be within 6 digits
        if error > 999999:
            return await ctx.send(f"{ctx.author.mention} This is an invalid error code. Please try again.")
        apicall = f"https://wiimmfi.de/error?m=json&e={error}"
        async with ctx.typing():
            async with self.bot.session.get(apicall) as r:
                if r.status == 200:
                    response = await r.json()
                    if response[0]["found"] == 0:
                        return await ctx.send(f"{ctx.author.mention} This error code does not exist.")
                    else:
                        embed = discord.Embed(title=f"Error {error}", colour=ConsoleColor.wii())
                        for i in response[0]["infolist"]:
                            embed.add_field(name=i["type"], value=f'**{i["name"]}**: {markdownify(i["info"])}', inline=False)
                        return await ctx.send(embed=embed)
                else:
                    return await ctx.send(f'{ctx.author.mention} API returned error {r.status}. Please check your values and try again.')


add_md_files_as_commands(AssistanceWii, console_cmd="wii")


async def setup(bot):
    await bot.add_cog(AssistanceWii(bot))
