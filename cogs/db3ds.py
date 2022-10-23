from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.ext import commands, tasks
from Levenshtein import distance

if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.context import KurisuContext


class DB3DS(commands.Cog):
    """3DS Title ID database lookup commands"""

    def __init__(self, bot):
        self.bot: Kurisu = bot
        self.tidpull.start()

    titledb = []

    def cog_unload(self):
        self.tidpull.cancel()

    @tasks.loop(hours=1)
    async def tidpull(self):
        regions = [
            "GB",
            "JP",
            "KR",
            "TW",
            "US"
        ]
        titledb = []
        for region in regions:
            async with self.bot.session.get(f"https://raw.githubusercontent.com/hax0kartik/3dsdb/master/jsons/list_{region}.json") as r:
                if r.status == 200:
                    j = await r.json(content_type=None)
                    titledb = titledb + j
                else:
                    # if any of the JSONs can't be pulled, don't update
                    # otherwise, it could replace the db with nothing,
                    # and old data is better than no data
                    return
        self.titledb = titledb

    async def tidsearchbyname(self, query: str) -> dict:
        """
        Search the list of games by game title using Levenshtein distance meter.
        Return the game entry if matches, return None otherwise.
        """
        query = query.lower()
        max_rat = 0
        res = {}
        for game in self.titledb:
            title = game['Name'].lower()
            if "-U-" in game["Product Code"]:  # skip update titles
                continue
            len_tot = len(query) + len(title)
            ratio = int(((len_tot - distance(query, title)) / len_tot) * 100)
            if ratio > 50 and ratio > max_rat:
                res = game
                max_rat = ratio
        return res

    async def tidsearchbygamecode(self, query: str) -> dict:
        """
        Search the list of games by 4-letter gamecode.
        Return the game entry if matches, return None otherwise.
        """
        query = query.upper()
        res = {}
        for game in self.titledb:
            # this can be safely assumed to be all uppercase, since that's what ninty does
            code = game['Product Code']
            if "-U-" in game["Product Code"]:  # skip update titles
                continue
            if code[-4:] == query:
                res = game
                # there can only be one copy of gamecode, excluding updates (which is excluded above)
                # so let's not waste time looking at the rest of the list
                break
        return res

    @commands.command()
    async def tidlookup(self, ctx: KurisuContext, *, query=""):
        """Links to 3DSDB and/or one of the apps.\n
        To link to 3DSDB: `tidlookup`
        To search for an app: `tidlookup [query]`"""
        if query == "":
            embed = discord.Embed(title="3DSDB")
            embed.set_author(name="hax0kartik")
            embed.description = "A database of DS and 3DS homebrew"
            embed.url = "https://hax0kartik.github.io/3dsdb/"
            return await ctx.send(embed=embed)
        res = {}
        # because switch cases in python suck, let's just check if res is None every time!
        if len(query) == 4:
            res = await self.tidsearchbygamecode(query)
        if not res:
            res = await self.tidsearchbyname(query)
        if not res:
            return await ctx.send("No app found!")
        embed = discord.Embed()
        embed.title = res["Name"]
        embed.add_field(name="Product Code", value=res["Product Code"], inline=False)
        embed.add_field(name="TitleID", value=res["TitleID"], inline=False)
        embed.add_field(name="Size", value=res["Size"], inline=False)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(DB3DS(bot))
