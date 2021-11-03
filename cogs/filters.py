import disnake
import re

from disnake.ext import commands
from textwrap import wrap

from disnake.ext.commands import Param

from utils.checks import is_staff
from utils.manager import check_collisions, WordFilterManager as WFM, LevenshteinFilterManager as LFM
from Levenshtein import distance


class Filter(commands.Cog):
    """
    Commands to manage the filter.
    """
    def __init__(self, bot):
        self.bot = bot

    @is_staff("Helper")
    @commands.slash_command()
    async def wordfilter(self, inter):
        """Command group for managing the word filter"""
        pass

    @is_staff("OP")
    @wordfilter.sub_command(name='add')
    async def add_word(self, inter,word: str = Param(desc="Word to add to the filter", conv=lambda inter, arg: arg.lower()),
                       kind: str = Param(desc="Filter to add the word to", choices=WFM.kinds)):
        """Adds a word to the word filter. A filter list must be specified"""
        if kind not in self.bot.wordfilter.kinds:
            return await inter.response.send_message(f"Possible word kinds for word filter: {', '.join(self.bot.wordfilter.kinds)}")
        if ' ' in word or '-' in word:
            return await inter.response.send_message("Filtered words cant contain dashes or spaces!")
        if await self.bot.wordfilter.fetch_word(word):
            return await inter.response.send_message("This word is already in the filter!")
        entry = await self.bot.wordfilter.add(word=word, kind=kind)
        await self.bot.channels['mod-logs'].send(f"🆕 **Added**: {inter.author.mention} added `{entry.word}` to the word filter!")
        await inter.response.send_message("Successfully added word to word filter")

    @wordfilter.sub_command(name='list')
    async def list_words(self, inter):
        """List the word filter filter lists and their content."""
        embed = disnake.Embed()
        for kind in self.bot.wordfilter.kinds:
            if self.bot.wordfilter.filter[kind]:
                parts = wrap('\n'.join(self.bot.wordfilter.filter[kind]), 1024, break_long_words=False, replace_whitespace=False)
                if (pages := len(parts)) > 1:
                    for n, part in enumerate(parts, start=1):
                        embed.add_field(name=f"{kind} {n}/{pages}", value=part)
                else:
                    embed.add_field(name=kind, value=parts[0])
        if embed:
            await inter.response.send_message(embed=embed, ephemeral=True)
        else:
            await inter.response.send_message("The word filter is empty!")

    @is_staff("OP")
    @wordfilter.sub_command(name='delete')
    async def delete_word(self, inter, words: list[str] = Param(desc="Words to delete")):
        """Deletes a word from the word filter"""
        print(words)
        return
        words = words.split()
        deleted = []
        for word in words:
            entry = await self.bot.wordfilter.delete(word=word)
            if entry:
                deleted.append(entry.word)
        if deleted:
            await inter.response.send_message(f"Deleted words `{'`,`'.join(deleted)}` succesfully!")
            await self.bot.channels['mod-logs'].send(f"⭕ **Deleted**: {inter.author.mention} deleted words `{'`,`'.join(deleted)}` from the filter!")
        else:
            await inter.response.send_message("No word was deleted from the filter!")

    # Command group for the levenshtein word filter
    @is_staff("Helper")
    @commands.slash_command()
    async def levenshteinfilter(self, inter):
        """Command group for managing the levenshtein filter"""
        pass

    @is_staff("OP")
    @levenshteinfilter.sub_command(name='add')
    async def add_levenshtein(self, inter, word: str = Param(desc="Word to add to the filter"), threshold: int = Param(desc="Threshold of similarity"), kind: str = Param(desc="Filter to add the word to", choices=LFM.kinds)):
        """Adds a word to the levenshtein filter. Words added are whitelisted by default."""
        word = word.lower()
        if kind not in self.bot.levenshteinfilter.kinds:
            return await inter.response.send_message(f"Possible word kinds for word filter: {', '.join(self.bot.levenshteinfilter.kinds)}")
        if ' ' in word:
            return await inter.response.send_message("Filtered words can't contain spaces!")
        if threshold == 0:
            return await inter.response.send_message("The permutation threshold must be above 0!")
        if await self.bot.levenshteinfilter.fetch_word(word):
            return await inter.response.send_message("This word is already in the filter!")
        entry = await self.bot.levenshteinfilter.add(word=word, threshold=threshold, kind=kind, whitelist=True)
        await self.bot.channels['mod-logs'].send(f"🆕 **Added**: {inter.author.mention} added `{entry.word}` to the Levenshtein filter!")
        await inter.response.send_message("Successfully added word to Levenshtein filter")

    @levenshteinfilter.sub_command(name='list')
    async def list_levenshtein(self, inter):
        """List the levenshtein filter filter lists and their content."""
        embed = disnake.Embed()
        for kind in self.bot.levenshteinfilter.kinds:
            if self.bot.levenshteinfilter.filter[kind]:
                value = "".join(
                    f"{word} with threshold {threshold}{' - whitelisted' if word in self.bot.levenshteinfilter.whitelist else ''} \n"
                    for word, threshold in self.bot.levenshteinfilter.filter[kind]
                )
                embed.add_field(name=kind, value=value)
        if embed:
            await inter.response.send_message(embed=embed, ephemeral=True)
        else:
            await inter.response.send_message("The Levenshtein filter is empty!")

    @levenshteinfilter.sub_command(name='test')
    async def test_levenshtein(self, inter,message):
        """Test a message against the levenshtein filter"""

        matches = {}
        message = message[::-1]
        to_check = re.findall(r"([\w0-9-]+\.[\w0-9-]+)", message)

        for kind in self.bot.levenshteinfilter.kinds:
            for word in to_check:
                word = word[::-1]
                matches[word] = []
                for trigger, threshold in self.bot.levenshteinfilter.filter[kind]:
                    word_distance = distance(word, trigger)
                    if word in self.bot.levenshteinfilter.whitelist or word_distance > threshold:
                        continue
                    else:
                        matches[word].append(trigger)
                if not matches[word]:
                    del matches[word]
        if matches:
            embed = disnake.Embed(title="Matches")
            for match in matches.keys():
                embed.add_field(name=match, value='\n'.join(matches[match]))
            await inter.response.send_message(embed=embed)
        else:
            await inter.response.send_message("Message didn't trigger the levenshtein filter.")

    @is_staff("OP")
    @levenshteinfilter.sub_command(name='delete')
    async def delete_levenshtein(self, inter,*, words: str):
        """Deletes a word from the levenshtein filter"""
        words = words.split()
        deleted = []
        for word in words:
            entry = await self.bot.levenshteinfilter.delete(word=word)
            if entry:
                deleted.append(entry.word)
        if deleted:
            await inter.response.send_message(f"Deleted words `{'`,`'.join(deleted)}` succesfully!")
            await self.bot.channels['mod-logs'].send(f"⭕ **Deleted**: {inter.author.mention} deleted words `{'`,`'.join(deleted)}` from the Levenshtein filter!")
        else:
            await inter.response.send_message("No word was deleted from the Levenshtein filter!")

    @levenshteinfilter.sub_command(name='checkcollision')
    async def check_filter_collision(self, inter):
        """Detects collisions between the levenshtein filter and the word filter"""
        if collisions := await check_collisions():
            embed = disnake.Embed(title="Filter Collisions")
            for key in collisions.keys():
                embed.add_field(name=key, value='\n'.join(collisions[key]))
            await inter.response.send_message(embed=embed)
        else:
            await inter.response.send_message("No collisions were detected!")

    @levenshteinfilter.sub_command_group(name='whitelist')
    async def levenshtein_whitelist(self, inter):
        """Group of commands to manage the whitelist of the levenshtein filter"""
        pass

    @is_staff("OP")
    @levenshtein_whitelist.sub_command(name='add')
    async def whitelist_add(self, inter,word: str):
        """Adds a word to the levenshtein filter whitelist"""
        word = word.lower()
        if db_word := await self.bot.levenshteinfilter.fetch_word(word=word):
            if db_word.whitelist:
                return await inter.response.send_message("This word is already whitelisted!")
            else:
                await self.bot.levenshteinfilter.edit(word=db_word.word, threshold=db_word.threshold, whitelist=True)
        elif await self.bot.levenshteinfilter.fetch_whitelist_word(word=word):
            return await inter.response.send_message("This word is already whitelisted!")
        await self.bot.levenshteinfilter.add_whitelist_word(word=word)
        await inter.response.send_message("Word added to whitelist successfully!")

    @is_staff("OP")
    @levenshtein_whitelist.sub_command(name='remove')
    async def whitelist_remove(self, inter,word: str):
        """Removes a word from the levenshtein filter whitelist"""
        word = word.lower()
        if db_word := await self.bot.levenshteinfilter.fetch_word(word=word):
            if not db_word.whitelist:
                return await inter.response.send_message("This word is not whitelisted!")
            else:
                await self.bot.levenshteinfilter.edit(word=db_word.word, threshold=db_word.threshold, whitelist=False)
        elif not await self.bot.levenshteinfilter.fetch_whitelist_word(word=word):
            return await inter.response.send_message("This word is not whitelisted!")
        await self.bot.levenshteinfilter.delete_whitelist_word(word=word)
        await inter.response.send_message("Word removed from whitelist successfully!")

    @levenshtein_whitelist.sub_command(name='list')
    async def whitelist_list(self, inter):
        """List the whitelisted words in the levenshtein filter"""
        whitelist = await self.bot.levenshteinfilter.fetch_whitelist()
        if whitelist:
            await inter.response.send_message('\n'.join(x.word for x in whitelist), ephemeral=True)
        else:
            await inter.response.send_message("The whitelist is empty.")

    @is_staff("Helper")
    @commands.slash_command()
    async def invitefilter(self, inter):
        """Command group for managing the invite filter"""
        pass

    @is_staff("OP")
    @invitefilter.sub_command(name='add')
    async def add_invite(self, inter,invite: disnake.Invite, alias: str):
        """Adds a invite to the filter whitelist"""
        if await self.bot.invitefilter.fetch_invite_by_alias(alias) or await self.bot.invitefilter.fetch_invite_by_code(invite.code):
            return await inter.response.send_message("This invite code or alias is already in use!")
        entry = await self.bot.invitefilter.add(code=invite.code, alias=alias, uses=-1)
        if entry is None:
            return await inter.response.send_message("Failed to add invite to the invite whitelist!")
        await self.bot.channels['mod-logs'].send(f"🆕 **Added**: {inter.author.mention} added {invite.code}(`{invite.guild.name}`) to the invite whitelist!")
        await inter.response.send_message("Successfully added invite to whitelist")

    @is_staff("OP")
    @invitefilter.sub_command(name='delete')
    async def delete_invite(self, inter,code: str):
        """Removes a invite from the filter whitelist"""
        entry = await self.bot.invitefilter.fetch_invite_by_code(code=code)
        if not entry:
            return await inter.response.send_message("Invite code not found!")
        await self.bot.invitefilter.delete(code=code)
        await inter.response.send_message(f"Deleted server `{entry.alias}` from filter succesfully!")
        await self.bot.channels['mod-logs'].send(f"⭕ **Deleted**: {inter.author.mention} deleted server `{entry.alias}` from the invite filter!")

    @invitefilter.sub_command(name='list')
    async def list_invites(self, inter):
        """List invites in the filter whitelist"""
        embed = disnake.Embed()
        if self.bot.invitefilter.invites:
            embed.add_field(name='Invites', value='\n'.join(f"name: {invite.alias} code:{invite.code} uses:{invite.uses}" for invite in self.bot.invitefilter.invites))
            await inter.response.send_message(embed=embed)
        else:
            await inter.response.send_message("The invite filter is empty!")


def setup(bot):
    bot.add_cog(Filter(bot))
