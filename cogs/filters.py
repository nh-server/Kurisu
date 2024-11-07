from __future__ import annotations

import discord
import re

from discord.ext import commands
from textwrap import wrap
from typing import TYPE_CHECKING, Literal
from Levenshtein import distance
from utils.checks import is_staff
from utils.database import FilterKind
from utils.utils import text_to_discord_file
from utils.views import ConfirmationButtons, PaginatedEmbedView, EmbedListPaginator

if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.context import KurisuContext


class Filter(commands.Cog):
    """
    Commands to manage the filter.
    """
    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.emoji = discord.PartialEmoji.from_str('🖥️')
        self.filters = bot.filters

    # Command group for the word filter
    @is_staff("Helper")
    @commands.group(aliases=['wf'])
    async def wordfilter(self, ctx: KurisuContext):
        """Command group for managing the word filter"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @is_staff("OP")
    @wordfilter.command(name='add')
    async def add_word(self, ctx: KurisuContext, word: str, *, kind: str):
        """Adds a word to the word filter. A filter list must be specified"""
        word = word.lower()
        try:
            filter_kind = FilterKind(kind)
        except ValueError:
            return await ctx.send(f"Possible word kinds for word filter: {', '.join(k.value for k in FilterKind)}")
        if ' ' in word or '-' in word:
            return await ctx.send("Filtered words cant contain dashes or spaces!")
        if discord.utils.get(self.filters.filtered_words, word=word):
            return await ctx.send("This word is already in the filter!")
        await self.filters.add_filtered_word(word, filter_kind)
        await self.bot.channels['mod-logs'].send(f"🆕 **Added**: {ctx.author.mention} added `{word}` to the word filter!")
        await ctx.send("Successfully added word to word filter")

    @wordfilter.command(name='list')
    async def list_words(self, ctx: KurisuContext):
        """List the word filter lists and their content."""
        embed = discord.Embed()
        words = {}

        for kind in FilterKind:
            words[kind] = []
            for fw in self.filters.filtered_words:
                if fw.kind is kind:
                    words[kind].append(fw.word)

        for kind, fws in words.items():
            parts = wrap('\n'.join(fws), 1024, break_long_words=False, replace_whitespace=False)
            if (pages := len(parts)) > 1:
                for n, part in enumerate(parts, start=1):
                    embed.add_field(name=f"{kind} {n}/{pages}", value=part)
            elif parts:
                embed.add_field(name=kind.value, value=parts[0])
        if embed:
            await ctx.author.send(embed=embed)
        else:
            await ctx.send("The word filter is empty!")

    @is_staff("OP")
    @wordfilter.command(name='delete', aliases=['remove'])
    async def delete_word(self, ctx: KurisuContext, *, words: str):
        """Deletes a word from the word filter"""
        word_list = words.split()
        deleted = []
        for word in word_list:
            res = await self.filters.delete_filtered_word(word=word)
            if res:
                deleted.append(word)
        if deleted:
            await ctx.send(f"Deleted words `{'`,`'.join(deleted)}` succesfully!")
            await self.bot.channels['mod-logs'].send(f"⭕ **Deleted**: {ctx.author.mention} deleted words `{'`,`'.join(deleted)}` from the filter!")
        else:
            await ctx.send("No word was deleted from the filter!")

    @wordfilter.command(name='export')
    async def wordfilter_export(self, ctx, export_format: Literal['automod', 'text'], *, filters: str):
        """Export the filtered words in the specified filters to a text file.
        `automod` outputs the words in a format ready to be copied to AutoMod without filter distinction.
        `text` outputs the words of each filter separated by new lines with the filter name before them."""

        if filters == 'all':
            filter_classes = [f for f in FilterKind]
        else:
            try:
                filter_classes = [FilterKind(filter_name) for filter_name in filters.split()]
            except ValueError:
                return await ctx.send(f"Invalid filter name. Possible word kinds for word filter: {', '.join(k.value for k in FilterKind)}")

        if export_format == 'automod':
            text = '*' + '*, *'.join(word.word for word in self.filters.filtered_words if word.kind in filter_classes) + '*'
        else:
            text = ""
            for filter_class in filter_classes:
                words = [word.word for word in self.filters.filtered_words if word.kind is filter_class]
                if words:
                    text += f"{filter_class.value}\n" + '\n'.join(words) + '\n\n\n'
        file = text_to_discord_file(text, name=f"wordfilter_{export_format}_export.txt")
        await ctx.send(file=file)

    @is_staff("OP")
    @wordfilter.command(name='import')
    async def wordfilter_import(self, ctx, input_file: discord.Attachment, type: Literal['join', 'replace'], *, filter_name: str):
        """Imports words to the word filter. These can added to the existing ones (`join`) or replace them (`replace`).
        The file format must be words codified in utf-8 separated by new lines."""

        try:
            filter_kind = FilterKind(filter_name)
        except ValueError:
            return await ctx.send(f"Possible word kinds for word filter: {', '.join(k.value for k in FilterKind)}")

        text = (await input_file.read()).decode('utf-8')
        word_list = [word.lower() for word in text.split('\n')]

        repeat = []
        invalid = []

        for word in word_list.copy():
            if type == 'join' and discord.utils.get(self.filters.filtered_words, word=word):
                word_list.remove(word)
                repeat.append(word)
            elif ' ' in word or '-' in word:
                word_list.remove(word)
                invalid.append(word)

        if not word_list:
            return await ctx.send("There is no valid words to import!")

        res = await self.filters.import_filtered_words(word_list, filter_kind, type)

        if not res:
            return await ctx.send("Failed to import words.")

        added = '\n'.join(word_list)
        result_text = f"Added:\n{added}\n\n"
        if repeat:
            repeat_str = '\n'.join(repeat)
            result_text += f"Repeats:\n{repeat_str}\n\n"
        if invalid:
            invalid_str = '\n'.join(invalid)
            result_text += f"Invalid:\n{invalid_str}"

        file = text_to_discord_file(result_text, name='import.txt')

        await ctx.send(f"Successfully imported words.\nAdded: {len(word_list)}\nRepeats: {len(repeat)}\nInvalid: {len(invalid)}", file=file)

    @is_staff("Owner")
    @wordfilter.command(name='clear')
    async def wordfilter_clear(self, ctx: KurisuContext):
        """Deletes all filtered words in the filter"""
        view = ConfirmationButtons(ctx.author)
        msg = await ctx.send("WARNING: This will delete all filtered words in the wordfilter, continue?", view=view)
        await view.wait()
        if view.value:
            await self.filters.clear_filtered_words()
            await msg.edit(content="Cleared all filtered words.", view=None)
        else:
            await msg.edit(content="Deletion aborted.", view=None)

    # Command group for the levenshtein word filter
    @is_staff("Helper")
    @commands.group(aliases=['xnoefilter', 'lfilter', 'lf'])
    async def levenshteinfilter(self, ctx: KurisuContext):
        """Command group for managing the levenshtein filter"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @is_staff("OP")
    @levenshteinfilter.command(name='add')
    async def add_levenshtein(self, ctx: KurisuContext, word: str, threshold: int, *, kind: str):
        """Adds a word to the levenshtein filter. A permutation threshold and a filter list must be specified.
        Words added are whitelisted by default."""
        word = word.lower()
        try:
            filter_kind = FilterKind(kind)
        except ValueError:
            return await ctx.send(f"Possible word kinds for word filter: {', '.join(f.value for f in FilterKind)}")
        if ' ' in word:
            return await ctx.send("Filtered words can't contain spaces!")
        if threshold == 0:
            return await ctx.send("The permutation threshold must be above 0!")
        if discord.utils.get(self.filters.lsh_words, word=word):
            return await ctx.send("This word is already in the filter!")
        res = await self.filters.add_levenshtein_word(word, threshold, filter_kind)
        if not res:
            return await ctx.send("Failed to add word to levenshtein filter.")
        await self.bot.channels['mod-logs'].send(f"🆕 **Added**: {ctx.author.mention} added `{word}` to the Levenshtein filter!")
        await ctx.send("Successfully added word to Levenshtein filter")

    @levenshteinfilter.command(name='list')
    async def list_levenshtein(self, ctx: KurisuContext):
        """List the levenshtein filter lists and their content."""
        embed = discord.Embed()
        words = {}

        for kind in FilterKind:
            words[kind] = []
            for lw in self.filters.lsh_words:
                if lw.kind is kind:
                    words[kind].append(f"{lw.word} treshhold {lw.threshold}")

        for kind, lws in words.items():
            parts = wrap('\n'.join(lws), 1024, break_long_words=False, replace_whitespace=False)
            if (pages := len(parts)) > 1:
                for n, part in enumerate(parts, start=1):
                    embed.add_field(name=f"{kind} {n}/{pages}", value=part)
            elif parts:
                embed.add_field(name=kind.value, value=parts[0])
        if embed:
            await ctx.author.send(embed=embed)
        else:
            await ctx.send("The levenshtein filter is empty!")

    @levenshteinfilter.command(name='test')
    async def test_levenshtein(self, ctx: KurisuContext, message):
        """Test a message against the levenshtein filter"""

        matches = {}
        message = message[::-1]
        to_check = re.findall(r"([\w0-9-]+\.[\w0-9-]+)", message)

        for word in to_check:
            word = word[::-1]
            if word in self.filters.whitelist:
                continue
            matches[word] = []
            for lsh_word in self.filters.lsh_words:
                word_distance = distance(word, lsh_word.word)
                if word_distance < lsh_word.threshold:
                    matches[word].append(lsh_word.word)
        if matches:
            embed = discord.Embed(title="Matches")
            for match in matches.keys():
                embed.add_field(name=match, value='\n'.join(matches[match]))
            await ctx.send(embed=embed)
        else:
            await ctx.send("Message didn't trigger the levenshtein filter.")

    @is_staff("OP")
    @levenshteinfilter.command(name='delete', aliases=['remove'])
    async def delete_levenshtein(self, ctx: KurisuContext, *, words: str):
        """Deletes a word from the levenshtein filter"""
        word_list = words.split()
        deleted = []
        for word in word_list:
            res = await self.filters.delete_levenshtein_word(word)
            if res:
                deleted.append(word)
        if deleted:
            await ctx.send(f"Deleted words `{'`,`'.join(deleted)}` succesfully!")
            await self.bot.channels['mod-logs'].send(f"⭕ **Deleted**: {ctx.author.mention} deleted words `{'`,`'.join(deleted)}` from the Levenshtein filter!")
        else:
            await ctx.send("No word was deleted from the Levenshtein filter!")

    @levenshteinfilter.group(name='whitelist')
    async def levenshtein_whitelist(self, ctx: KurisuContext):
        """Group of commands to manage the whitelist of the levenshtein filter"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @is_staff("OP")
    @levenshtein_whitelist.command(name='add')
    async def whitelist_add(self, ctx: KurisuContext, word: str):
        """Adds a word to the levenshtein filter whitelist"""
        word = word.lower()
        if word in self.filters.whitelist:
            return await ctx.send("This word is already whitelisted!")
        await self.filters.add_whitelisted_word(word)
        await ctx.send("Word added to whitelist successfully!")

    @is_staff("OP")
    @levenshtein_whitelist.command(name='remove')
    async def whitelist_remove(self, ctx: KurisuContext, word: str):
        """Removes a word from the levenshtein filter whitelist"""
        word = word.lower()
        if word in self.filters.whitelist:
            return await ctx.send("This word is not whitelisted!")
        await self.filters.delete_whitelisted_word(word)
        await ctx.send("Word removed from whitelist successfully!")

    @levenshtein_whitelist.command(name='list')
    async def whitelist_list(self, ctx: KurisuContext):
        """List the whitelisted words in the levenshtein filter"""
        if self.filters.whitelist:
            await ctx.author.send('\n'.join(word for word in self.filters.whitelist))
        else:
            await ctx.send("The whitelist is empty.")

    @is_staff("Helper")
    @commands.group(aliases=['if'])
    async def invitefilter(self, ctx: KurisuContext):
        """Command group for managing the invite filter"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @is_staff("OP")
    @invitefilter.command(name='add')
    async def add_invite(self, ctx: KurisuContext, invite: discord.Invite, alias: str):
        """Adds a discord invite to the filter whitelist"""

        if self.filters.get_invite_named(alias):
            return await ctx.send("This alias is already in use!")

        if self.filters.approved_invites.get(invite.code):
            return await ctx.send("This invite code is already in use!")

        if invite.guild is None or isinstance(invite.guild, discord.Object):
            return await ctx.send("No information from the guild could be fetched.")

        res = await self.filters.add_approved_invite(invite, uses=-1, alias=alias)
        if not res:
            return await ctx.send("Failed to add invite to the invite whitelist!")
        await self.bot.channels['mod-logs'].send(f"🆕 **Added**: {ctx.author.mention} added {invite.code}(`{invite.guild.name}`) to the invite whitelist!")
        await ctx.send("Successfully added invite to whitelist")

    @is_staff("OP")
    @invitefilter.command(name='delete')
    async def delete_invite(self, ctx: KurisuContext, code: str):
        """Removes a discord invite from the filter whitelist"""
        entry = self.filters.approved_invites.get(code)
        if not entry:
            return await ctx.send("Invite code not found!")
        res = await self.filters.delete_approved_invite(code)
        if not res:
            return await ctx.send("Failed to delete invite.")
        await ctx.send(f"Deleted server `{entry.alias}` from filter succesfully!")
        await self.bot.channels['mod-logs'].send(f"⭕ **Deleted**: {ctx.author.mention} deleted server `{entry.alias}` from the invite filter!")

    @invitefilter.command(name='list')
    async def list_invites(self, ctx: KurisuContext):
        """List invites in the filter whitelist"""
        if self.filters.approved_invites:
            embeds: list[discord.Embed] = []
            idx = 0
            text = ""
            next_line = ""
            n_invites = len(self.filters.approved_invites.values())
            embeds.append(discord.Embed(title=f"List of invites [{idx+1}]"))
            for n, invite in enumerate(self.filters.approved_invites.values(), start=1):
                next_line = f"name: {invite.alias} code:{invite.code} uses:{invite.uses}\n"
                if len(text) + len(next_line) > 1024:
                    embeds[idx].add_field(name='Invites', value=text)
                    text = next_line
                    if n < n_invites:
                        idx += 1
                        embeds.append(discord.Embed(title=f"List of invites [{idx+1}]"))
                else:
                    text += next_line
                    next_line = ""
            if not next_line:
                embeds[idx].add_field(name='Invites', value=text)
            view = PaginatedEmbedView(EmbedListPaginator(embeds))
            await ctx.send(embed=view.paginator.current(), view=view)
        else:
            await ctx.send("The invite filter is empty!")

    # @commands.command(name='checkcollision', aliases=['filtercollision'])
    # async def check_filter_collision(self, ctx: KurisuContext):
    #     """Detects collisions between the levenshtein filter and the word filter,
    #     shows what words matched an entry in the levenshtein filter"""
    #     if collisions := await check_collisions():
    #         embed = discord.Embed(title="Filter Collisions")
    #         for key in collisions.keys():
    #             embed.add_field(name=key, value='\n'.join(collisions[key]))
    #         await ctx.send(embed=embed)
    #     else:
    #         await ctx.send("No collisions were detected!")


async def setup(bot):
    await bot.add_cog(Filter(bot))
