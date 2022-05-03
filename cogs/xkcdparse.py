from __future__ import annotations

import discord
import xkcd

from discord.ext import commands
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from kurisu import Kurisu


class xkcdparse(commands.Cog):
    """
    xkcd parser.
    """
    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.emoji = discord.PartialEmoji.from_str('📡')

    word_responses = {
        "pointers": 138,
        "sudo": 149,
        "sandwich": 149,
        "compiling": 303,
        "code compiling": 303,
        "bobby tables": 327,
        "little bobby tables": 327,
        "duty calls": 386,
        "security": 538,
        "standards": 927,
        "password": 936,
        "denvercoder9": 979,
        "workflow": 1172,
        "free speech": 1357,
        "screenshot": 1373,
        "tasks": 1425,
        "real programmers": 378
    }

    @commands.command()
    async def xkcd(self, ctx: commands.Context, *, comic):
        """Show xkcd comic by number. Use "latest" to show the latest comic, or "random" to show a random comic."""
        comic = comic.lower()
        if comic == "latest":
            await ctx.send("https://xkcd.com/{}/".format(xkcd.getLatestComic().number))
        elif comic == "random":
            await ctx.send("https://xkcd.com/{}/".format(xkcd.getRandomComic().number))
        elif comic.isdecimal():
            await ctx.send("https://xkcd.com/{}/".format(xkcd.getComic(comic).number))
        elif comic in self.word_responses:
            await ctx.send("https://xkcd.com/{}/".format(xkcd.getComic(self.word_responses[comic]).number))
        else:
            await ctx.send("I can't find that one!")


async def setup(bot):
    await bot.add_cog(xkcdparse(bot))
