from datetime import datetime
from re import compile, finditer, search
from typing import List, Union

import discord
from discord.ext import commands


class Season:
    def __init__(self, start: str, end: str, emote: str, emote_str: str):
        self.start_str = start
        self.end_str = end
        self.start = Season.get_int_from_dotstr(start)
        self.end = Season.get_int_from_dotstr(end)
        self.emote = emote
        self.emote_str = emote_str
        self.emote_regex = compile(emote)

    def __contains__(self, time: Union[str, int]) -> bool:
        if isinstance(time, str):
            time = Season.get_int_from_dotstr(time)

        # handle wrapping around year boundaries
        if self.start > self.end:
            return time <= self.end or time >= self.start
        else:
            return self.start <= time <= self.end

    def __eq__(self, other: str) -> bool:
        return other in (self.emote_str, self.emote)

    @staticmethod
    def get_int_from_dotstr(dotstr: str) -> int:
        month, day = dotstr.split(".")
        return (int(month) * 31) + int(day)


class Seasonal(commands.Cog):
    seasons: List[Season] = [
        Season("12.1", "12.31", "🎄", "xmasthing"),
        Season("6.1", "6.31", "🌈", "rainbow"),
        Season("10.1", "10.31", "🎃", "pumpkin"),
        Season("11.1", "11.30", "🦃", "turkey"),
        Season("12.31", "1.1", "🎆", "fireworks"),
        Season("3.16", "3.17", "🍀", "shamrock"),
    ]

    def __init__(self, bot):
        self.bot = bot

    async def _seasonal_impl(self, ctx, mode: str, target: str = None):
        season = None
        t = datetime.today()
        curr_time = f"{t.month}.{t.day}"
        for season_ in self.seasons:
            if (mode == "remove" and season_.emote_str == target) or (target == None and curr_time in season_):
                season = season_
                break
        else:
            if target is None or mode == "add":
                return await ctx.send(
                    "There is no special season happening right now "
                    "or it hasn't been implemented yet."
                )    
            return await ctx.send(
                "There is no season with the name you specified."
            )

        if mode == "add":
            if target is not None:
                return await ctx.send(
                    "💢 You can't choose which season to add! "
                    "(Try again with just .seasonal)"
                )

            new_nick = f"{ctx.author.display_name} {season.emote}"
            if ctx.author.display_name[-1] == season.emote:
                return await ctx.send(
                    f"Your shown name already ends in a {season.emote}!"
                )
            if len(new_nick) > 32:
                return await ctx.send(
                    "💢 Your name is too long! "
                    f"(max is 32 characters, yours would be {len(new_nick)})")
        elif mode == "remove":
            if ctx.author.nick:
                matches = list(finditer(season.emote_regex, ctx.author.nick))

                if matches:
                    res = matches[-1]
                    new_nick = (
                        f"{ctx.author.display_name[:res.start()]}"
                        f"{ctx.author.display_name[res.end():]}"
                    )
                else:
                    return await ctx.send(
                        "Your nickname doesn't contain the current/requested"
                        f" seasonal emote [{season.emote} | '{season.emote_str}']"
                    )
            
                if len(new_nick) == 0:
                    return await ctx.send("💢 I can't completely remove your nick!")
            elif bool(search(season.emote_regex, ctx.author.name)):
                return await ctx.send(f"Your username is the one with a {season.emote_str}")
            else:
                return await ctx.send(f"You don't have a {season.emote_str}")

        try:
            await ctx.author.edit(nick=new_nick)
            await ctx.send(f"Your nickname is now `{ctx.author.display_name}`")
        except discord.errors.Forbidden:
            await ctx.send("💢  I can't change your nickname! (Permission Error)")
    
    @commands.guild_only()
    @commands.command()
    async def seasonal(self, ctx):
        """Adds the emote of the current season to your name.
        
        You can see which seasons exist and when they are by typing .seasonals
        """
        return await self._seasonal_impl(ctx, "add")

    @commands.guild_only()
    @commands.command()
    async def noseasonal(self, ctx, *, target: str = None):
        """Removes the emote of the current season (or any you want) 
        from your name.  
        
        You can see which seasons exist and when they are by typing .seasonals
        """
        return await self._seasonal_impl(ctx, "remove", target)
    
    @commands.command(aliases=["seasons"])
    async def seasonals(self, ctx):
        """Lists all available seasons."""

        line_template = "{0:6} | {1:6} | {2:1} | {3}\n"
        await ctx.send(
            "The following seasons exist on this server:\n```"
            + line_template.format("start", "end", "emote", "emote_name")
            + f"{'=' * 36}\n"
            + "".join(
                line_template.format(
                    season.start_str, season.end_str, season.emote, season.emote_str
                ) for season in self.seasons
            )
            + "```"
        )

def setup(bot):
    bot.add_cog(Seasonal(bot))
