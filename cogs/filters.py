import discord

from discord.ext import commands
from textwrap import wrap
from utils.checks import is_staff


class Filter(commands.Cog):
    """
    Commands to manage the filter.
    """
    def __init__(self, bot):
        self.bot = bot

    # Command group for the word filter
    @is_staff("Helper")
    @commands.group(aliases=['wf'])
    async def wordfilter(self, ctx):
        """Command group for managing the word filter"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @is_staff("SuperOP")
    @wordfilter.command(name='add')
    async def add_word(self, ctx, word: str, *, kind: str):
        """Adds a word to the word filter. A filter list must be specified"""
        word = word.lower()
        if kind not in self.bot.wordfilter.kinds:
            return await ctx.send(f"Possible word kinds for word filter: {', '.join(self.bot.wordfilter.kinds)}")
        if ' ' in word or '-' in word:
            return await ctx.send("Filtered words cant contain dashes or spaces!")
        if await self.bot.wordfilter.fetch_word(word):
            return await ctx.send("This word is already in the filter!")
        entry = await self.bot.wordfilter.add(word=word, kind=kind)
        await self.bot.channels['mod-logs'].send(f"🆕 **Added**: {ctx.author.mention} added `{entry.word}` to the word filter!")
        await ctx.send("Successfully added word to word filter")

    @wordfilter.command(name='list')
    async def list_words(self, ctx):
        """List the word filter filter lists and their content."""
        embed = discord.Embed()
        for kind in self.bot.wordfilter.kinds:
            if self.bot.wordfilter.filter[kind]:
                parts = wrap('\n'.join(self.bot.wordfilter.filter[kind]), 1024, break_long_words=False, replace_whitespace=False)
                if (pages := len(parts)) > 1:
                    for n, part in enumerate(parts, start=1):
                        embed.add_field(name=f"{kind} {n}/{pages}", value=part)
                else:
                    embed.add_field(name=kind, value=parts[0])
        if embed:
            await ctx.author.send(embed=embed)
        else:
            await ctx.send("The word filter is empty!")

    @is_staff("SuperOP")
    @wordfilter.command(name='delete', aliases=['remove'])
    async def delete_word(self, ctx, *, words: str):
        """Deletes a word from the word filter"""
        words = words.split()
        deleted = []
        for word in words:
            entry = await self.bot.wordfilter.delete(word=word)
            if entry:
                deleted.append(entry.word)
        if deleted:
            await ctx.send(f"Deleted words `{'`,`'.join(deleted)}` succesfully!")
            await self.bot.channels['mod-logs'].send(f"⭕ **Deleted**: {ctx.author.mention} deleted words `{'`,`'.join(deleted)}` from the filter!")
        else:
            await ctx.send("No word was deleted from the filter!")

    # Command group for the levenshtein word filter
    @is_staff("Helper")
    @commands.group(aliases=['xnoefilter', 'lfilter', 'lf'])
    async def levenshteinfilter(self, ctx):
        """Command group for managing the levenshtein filter"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @is_staff("SuperOP")
    @levenshteinfilter.command(name='add')
    async def add_levenshtein(self, ctx, word: str, threshold: int, *, kind: str):
        """Adds a word to the levenshtein filter. A permutation threshold and a filter list must be specified.
        Words added are whitelisted by default."""
        word = word.lower()
        if kind not in self.bot.levenshteinfilter.kinds:
            return await ctx.send(f"Possible word kinds for word filter: {', '.join(self.bot.levenshteinfilter.kinds)}")
        if ' ' in word:
            return await ctx.send("Filtered words can't contain spaces!")
        if threshold == 0:
            return await ctx.send("The permutation threshold must be above 0!")
        if await self.bot.levenshteinfilter.fetch_word(word):
            return await ctx.send("This word is already in the filter!")
        entry = await self.bot.levenshteinfilter.add(word=word, threshold=threshold, kind=kind, whitelist=True)
        await self.bot.channels['mod-logs'].send(f"🆕 **Added**: {ctx.author.mention} added `{entry.word}` to the Levenshtein filter!")
        await ctx.send("Successfully added word to Levenshtein filter")

    @levenshteinfilter.command(name='list')
    async def list_levenshtein(self, ctx):
        """List the levenshtein filter filter lists and their content."""
        embed = discord.Embed()
        for kind in self.bot.levenshteinfilter.kinds:
            if self.bot.levenshteinfilter.filter[kind]:
                value = "".join(
                    f"{word} with threshold {threshold}{' - whitelisted' if word in self.bot.levenshteinfilter.whitelist else ''} \n"
                    for word, threshold in self.bot.levenshteinfilter.filter[kind]
                )
                embed.add_field(name=kind, value=value)
        if embed:
            await ctx.author.send(embed=embed)
        else:
            await ctx.send("The Levenshtein filter is empty!")

    @is_staff("SuperOP")
    @levenshteinfilter.command(name='delete', aliases=['remove'])
    async def delete_levenshtein(self, ctx, *, words: str):
        """Deletes a word from the levenshtein filter"""
        words = words.split()
        deleted = []
        for word in words:
            entry = await self.bot.levenshteinfilter.delete(word=word)
            if entry:
                deleted.append(entry.word)
        if deleted:
            await ctx.send(f"Deleted words `{'`,`'.join(deleted)}` succesfully!")
            await self.bot.channels['mod-logs'].send(f"⭕ **Deleted**: {ctx.author.mention} deleted words `{'`,`'.join(deleted)}` from the Levenshtein filter!")
        else:
            await ctx.send("No word was deleted from the Levenshtein filter!")

    @levenshteinfilter.group(name='whitelist')
    async def levenshtein_whitelist(self, ctx):
        """Group of commands to manage the whitelist of the levenshtein filter"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @is_staff("SuperOP")
    @levenshtein_whitelist.command(name='add')
    async def whitelist_add(self, ctx, word: str):
        """Adds a word to the levenshtein filter whitelist"""
        word = word.lower()
        if db_word := await self.bot.levenshteinfilter.fetch_word(word=word):
            if db_word.whitelist:
                return await ctx.send("This word is already whitelisted!")
            else:
                await self.bot.levenshteinfilter.edit(word=db_word.word, threshold=db_word.threshold, whitelist=True)
        elif await self.bot.levenshteinfilter.fetch_whitelist_word(word=word):
            return await ctx.send("This word is already whitelisted!")
        await self.bot.levenshteinfilter.add_whitelist_word(word=word)
        await ctx.send("Word added to whitelist successfully!")

    @is_staff("SuperOP")
    @levenshtein_whitelist.command(name='remove')
    async def whitelist_remove(self, ctx, word: str):
        """Removes a word from the levenshtein filter whitelist"""
        word = word.lower()
        if db_word := await self.bot.levenshteinfilter.fetch_word(word=word):
            if not db_word.whitelist:
                return await ctx.send("This word is not whitelisted!")
            else:
                await self.bot.levenshteinfilter.edit(word=db_word.word, threshold=db_word.threshold, whitelist=False)
        elif not await self.bot.levenshteinfilter.fetch_whitelist_word(word=word):
            return await ctx.send("This word is not whitelisted!")
        await self.bot.levenshteinfilter.delete_whitelist_word(word=word)
        await ctx.send("Word removed from whitelist successfully!")

    @levenshtein_whitelist.command(name='list')
    async def whitelist_list(self, ctx):
        """List the whitelisted words in the levenshtein filter"""
        whitelist = await self.bot.levenshteinfilter.fetch_whitelist()
        if whitelist:
            await ctx.author.send('\n'.join(x.word for x in whitelist))
        else:
            await ctx.send("The whitelist is empty.")

    @is_staff("Helper")
    @commands.group(aliases=['if'])
    async def invitefilter(self, ctx):
        """Command group for managing the invite filter"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @is_staff("SuperOP")
    @invitefilter.command(name='add')
    async def add_invite(self, ctx, invite: discord.Invite, alias: str):
        """Adds a invite to the filter whitelist"""
        if await self.bot.invitefilter.fetch_invite_by_alias(alias) or await self.bot.invitefilter.fetch_invite_by_code(invite.code):
            return await ctx.send("This invite code or alias is already in use!")
        entry = await self.bot.invitefilter.add(code=invite.code, alias=alias, uses=-1)
        if entry is None:
            return await ctx.send("Failed to add invite to the invite whitelist!")
        await self.bot.channels['mod-logs'].send(f"🆕 **Added**: {ctx.author.mention} added {invite.code}(`{invite.guild.name}`) to the invite whitelist!")
        await ctx.send("Successfully added invite to whitelist")

    @is_staff("SuperOP")
    @invitefilter.command(name='delete')
    async def delete_invite(self, ctx, code: str):
        """Removes a invite from the filter whitelist"""
        entry = await self.bot.invitefilter.fetch_invite_by_code(code=code)
        if not entry:
            return await ctx.send("Invite code not found!")
        await self.bot.invitefilter.delete(code=code)
        await ctx.send(f"Deleted server `{entry.alias}` from filter succesfully!")
        await self.bot.channels['mod-logs'].send(f"⭕ **Deleted**: {ctx.author.mention} deleted server `{entry.alias}` from the invite filter!")

    @invitefilter.command(name='list')
    async def list_invites(self, ctx):
        """List invites in the filter whitelist"""
        embed = discord.Embed()
        if self.bot.invitefilter.invites:
            embed.add_field(name='Invites', value='\n'.join(f"name: {invite.alias} code:{invite.code} uses:{invite.uses}" for invite in self.bot.invitefilter.invites))
            await ctx.send(embed=embed)
        else:
            await ctx.send("The invite filter is empty!")


def setup(bot):
    bot.add_cog(Filter(bot))
