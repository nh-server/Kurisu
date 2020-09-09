import discord
import os.path

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
        if ' ' in word or '-' in word:
            return await ctx.send("Filtered words cant contain dashes or spaces!")
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
            await ctx.author.send(embed=embed)
        else:
            await ctx.send("The word filter is empty!")

    @is_staff("SuperOP")
    @wordfilter.command(name='delete', aliases=['remove'])
    async def delete_word(self, ctx, word: str):
        name = await self.bot.wordfilter.delete(word=word)
        if name is None:
            return await ctx.send("Word not found!")
        await ctx.send(f"Delete word `{word}` succesfully!")
        await self.bot.channels['mod-logs'].send(f"⭕ **Deleted**: {ctx.author.mention} deleted word `{word}` from the filter!")

    @is_staff("Owner")
    @wordfilter.command()
    async def bulk_load_config(self, ctx):
        if os.path.exists("wordfilter.json"):
            try:
                await self.bot.wordfilter.bulk_load()
                await ctx.send("Bulk loaded config successfully!")
            except BaseException as e:
                return await ctx.send(f"Failed to bulk load configuration: {e}")
        else:
            await ctx.send("There is no valid file for loading!")

    @is_staff("Helper")
    @commands.group()
    async def invitefilter(self, ctx):
        """Command group for managing the invite filter"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @is_staff("SuperOP")
    @invitefilter.command(name='add')
    async def add_invite(self, ctx, invite: discord.Invite, alias: str):
        """Adds a invite to the filter whitelist"""
        if await self.bot.invitefilter.fetch(code=invite.code, alias=alias, separator='OR'):
            return await ctx.send("This invite code or alias is already in use!")
        name, _ = await self.bot.invitefilter.add(name=invite.guild.name, code=invite.code, alias=alias)
        if name is None:
            return await ctx.send("Failed to add invite to the invite whitelist!")
        await self.bot.channels['mod-logs'].send(f"🆕 **Added**: {ctx.author.mention} added {invite.code}(`{invite.guild.name}`) to the invite whitelist!")
        await ctx.send("Successfully added invite to whitelist")

    @is_staff("SuperOP")
    @invitefilter.command(name='delete')
    async def delete_invite(self, ctx, code: str):
        """Removes a invite from the filter whitelist"""
        name, _ = await self.bot.invitefilter.delete(code=code)
        if not name:
            return await ctx.send("Invite code not found!")
        await ctx.send(f"Deleted server `{name}` from filter succesfully!")
        await self.bot.channels['mod-logs'].send(f"⭕ **Deleted**: {ctx.author.mention} deleted server `{name}` from the invite filter!")

    @invitefilter.command(name='list')
    async def list_invites(self, ctx):
        """List invites in the filter whitelist"""
        embed = discord.Embed()
        if self.bot.invitefilter.invites:
            embed.add_field(name='Invites', value='\n'.join(f"name: {alias} code:{self.bot.invitefilter.invites[alias].code} uses:{self.bot.invitefilter.invites[alias].uses}" for alias in self.bot.invitefilter.invites.keys()))
            await ctx.send(embed=embed)
        else:
            await ctx.send("The invite filter is empty!")


def setup(bot):
    bot.add_cog(Filter(bot))
