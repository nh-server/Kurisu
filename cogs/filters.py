import discord

from discord.ext import commands
from utils.checks import is_staff


class Filter(commands.Cog):
    """
    Commands to manage the filter.
    """
    def __init__(self, bot):
        self.bot = bot

    # Command group for the word filter
    @is_staff("Helper")
    @commands.group()
    async def wordfilter(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @is_staff("SuperOP")
    @wordfilter.command(name='add')
    async def add_word(self, ctx, word: str, *, kind: str):
        if kind not in self.bot.wordfilter.kinds:
            return await ctx.send(f"Possible word kinds for word filter: {', '.join(self.bot.wordfilter.kinds)}")
        word, _ = await self.bot.wordfilter.add(word=word, kind=kind)
        if word is None:
            return await ctx.send(f"Failed to add word to {kind} filter")
        await self.bot.channels['mod-logs'].send(f"🆕 **Added**: {ctx.author.mention} added `{word}` to the word filter!")
        await ctx.send("Successfully added word to word filter")

    @wordfilter.command(name='list')
    async def list_words(self, ctx):
        embed = discord.Embed()
        for kind in self.bot.wordfilter.kinds:
            if self.bot.wordfilter.filter[kind]:
                embed.add_field(name=kind, value='\n'.join(self.bot.wordfilter.filter[kind]))
        if embed:
            await ctx.send(embed=embed)
        else:
            await ctx.send("The word filter is empty!")

    @is_staff("SuperOP")
    @wordfilter.command(name='delete', aliases=['remove'])
    async def delete_word(self, ctx, word: str):
        name = await self.bot.wordfilter.delete(word=word)
        if name is None:
            return await ctx.send("Word not found!")
        await ctx.send(f"Delete filtered word succesfully!")
        await self.bot.channels['mod-logs'].send(f"⭕ **Deleted**: {ctx.author.mention} deleted word `{word}` from the filter!")


def setup(bot):
    bot.add_cog(Filter(bot))
