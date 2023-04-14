from __future__ import annotations

import discord
import re

from discord.ext import commands, tasks
from Levenshtein import distance
from typing import TYPE_CHECKING

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

    async def search_game_by_name(self, query: str) -> dict:
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

    async def search_game_by_gamecode(self, query: str) -> dict:
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

    async def search_game_by_tid(self, query: str) -> dict:
        """
        Search the list of games by title id.
        Return the game entry if matches, return None otherwise.
        """
        query = query.upper()

        if not query.startswith("000"):
            query = "000" + query

        res = {}
        for game in self.titledb:
            titleid = game['TitleID']
            if query == titleid:
                res = game
                # TitleID is unique so need to search more
                break
        return res

    @staticmethod
    def is_titleid(query: str):
        # 00040000 for games, 0004000E for updates, 00048004 for dsiware
        return re.fullmatch("0{3}?4[08]00[0E4][a-f0-9]{8}", query, re.IGNORECASE)

    @staticmethod
    def is_gamecode(query: str):
        return re.fullmatch('[aA-zZ0-9]{4}', query, re.IGNORECASE)

    @commands.command(aliases=['lookup'])
    async def tidlookup(self, ctx: KurisuContext, *, query: str = ""):
        """Links to 3DSDB and/or one of the apps.\n
        To link to 3DSDB: `tidlookup`
        To search for an app: `tidlookup [query]`"""
        if query == "":
            embed = discord.Embed(title="3DSDB")
            embed.set_author(name="hax0kartik")
            embed.description = "A database of 3DS games that were on the eShop"
            embed.url = "https://hax0kartik.github.io/3dsdb/"
            return await ctx.send(embed=embed)
        if self.is_gamecode(query):
            res = await self.search_game_by_gamecode(query)
        elif self.is_titleid(query):
            res = await self.search_game_by_tid(query)
        else:
            res = await self.search_game_by_name(query)
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
