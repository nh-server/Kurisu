from __future__ import annotations

import discord

from discord.ext import commands, tasks
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.context import GuildContext


class BFM(commands.Cog):
    """Bruteforce Movable status polling"""

    def __init__(self, bot):
        self.bot: Kurisu = bot
        self.bfm_check.start()

    def cog_unload(self):
        self.bfm_check.cancel()

    @tasks.loop(minutes=10)
    async def bfm_check(self, ctx: GuildContext):
        async with self.bot.session.get("https://bfm.nintendohomebrew.com/status") as r:
            if r.status != 200:
                embed = discord.Embed(title="BFM Seedminer is down!")
                embed.description = f"Site returned error code: {r.status}"
                await self.bot.channels["community-resources-🙂"].send(embed=embed)
                return
            status = await r.json()
        if status['userCount'] > 15:
            embed = discord.Embed(title="BFM queue is elevated!")
            if status['miningCount'] == 0 and status['minersStandby'] == 0:
                embed.title = "BFM queue is elevated, but why?"
            embed.add_field(name="In queue", value=status['userCount'], inline=False)
            embed.add_field(name="Mining", value=status['miningCount'], inline=False)
            embed.add_field(name="Idle", value=status['minersStandby'], inline=False)

            await self.bot.channels["community-resources-🙂"].send(embed=embed)


async def setup(bot):
    await bot.add_cog(BFM(bot))
