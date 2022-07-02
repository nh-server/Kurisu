import asyncio
import re
from typing import TYPE_CHECKING, Optional

import discord
from Levenshtein import distance

from .managerbase import BaseManager
from .database import FiltersDatabaseManager, ApprovedInvite, FilteredWord, LevenshteinWord

if TYPE_CHECKING:
    from kurisu import Kurisu
    from .database import FilterKind

rgx_special_chars = '()[]{}?*+-|^$\\.&~# \t\n\r\v\f'


def separate_and_escape_str(string: str) -> list[str]:
    separated = []
    for char in string:
        if char in rgx_special_chars:
            separated.append('\\' + char)
        else:
            separated.append(char)
    return separated


class FiltersManager(BaseManager, db_manager=FiltersDatabaseManager):
    """Manages the bot filters."""

    db: FiltersDatabaseManager

    def __init__(self, bot: 'Kurisu'):
        super().__init__(bot)
        asyncio.create_task(self.setup())

    async def setup(self):
        self._whitelist: list[str] = [wl async for wl in self.db.get_whitelisted_words()]

        self._lsh_words: 'list[LevenshteinWord]' = [wl async for wl in self.db.get_levenshtein_words()]

        self._filtered_words: 'list[FilteredWord]' = [fw async for fw in self.db.get_filtered_words()]

        self._approved_invites: 'dict[str, ApprovedInvite]' = {ai.code: ai async for ai in self.db.get_approved_invites()}

    @property
    def whitelist(self):
        return self._whitelist

    @property
    def lsh_words(self):
        return self._lsh_words

    @property
    def filtered_words(self):
        return self._filtered_words

    @property
    def approved_invites(self):
        return self._approved_invites

    # fetch, insert and update operations

    async def add_filtered_word(self, word: str, kind: 'FilterKind'):
        res = await self.db.add_filtered_word(word, kind.value)
        if res:
            self._filtered_words.append(FilteredWord(word=word, kind=kind))
        return res

    async def delete_filtered_word(self, word: str) -> int:
        res = await self.db.delete_filtered_word(word)
        if res:
            f_word = discord.utils.get(self._filtered_words, word=word)
            if f_word:
                self._filtered_words.remove(f_word)
        return res

    async def add_levenshtein_word(self, word: str, threshold: int, kind: 'FilterKind') -> int:
        res = await self.db.add_levenshtein_word(word, threshold, kind.value)
        if res:
            self._lsh_words.append(LevenshteinWord(word=word, threshold=threshold, kind=kind))
        return res

    async def delete_levenshtein_word(self, word: str) -> int:
        res = await self.db.delete_levenshtein_word(word)
        if res:
            lsh_word = discord.utils.get(self._lsh_words, word=word)
            if lsh_word:
                self._lsh_words.remove(lsh_word)
        return res

    async def add_whitelisted_word(self, word: str) -> int:
        res = await self.db.add_whitelisted_word(word)
        if res:
            self._whitelist.append(word)
        return res

    async def delete_whitelisted_word(self, word: str) -> int:
        res = await self.db.delete_whitelisted_word(word)
        if res:
            self._whitelist.remove(word)
        return res

    async def add_approved_invite(self, invite: discord.Invite, uses: int, alias: str):
        res = await self.db.add_approved_invite(code=invite.code, uses=uses, alias=alias)
        if res:
            self._approved_invites[invite.code] = ApprovedInvite(code=invite.code, uses=uses, alias=alias)
        return res

    async def delete_approved_invite(self, code: str):
        res = await self.db.delete_approved_invite(code)
        if res:
            del self._approved_invites[code]
        return res

    async def update_invite_use(self, code: str):
        res = await self.db.update_invite_use(code)
        if res:
            old = self._approved_invites[code]
            self._approved_invites[code] = ApprovedInvite(code=old.code, uses=old.uses - 1, alias=old.alias)
        return res

    def get_invite_named(self, alias: str) -> Optional[ApprovedInvite]:
        return discord.utils.get(self._approved_invites.values(), alias=alias)

    # Filter operations
    def match_filtered_words(self, message: str) -> set:
        matches = set()
        for word in self._filtered_words:
            pos = message.find(word.word)
            if pos != -1:
                matches.add(word.kind)
        return matches

    def match_levenshtein_words(self, message: str):
        matches = set()
        message = message[::-1]
        to_check = re.findall(r"([\w0-9-]+\.[\w0-9-]+)", message)

        for word in to_check:
            word = word[::-1]
            if word in self._whitelist:
                continue
            for lword in self._lsh_words:
                lf_distance = distance(word, lword.word)
                if lf_distance < lword.threshold:
                    matches.add(lword.kind)
        return matches

    def search_invite(self, message: str) -> tuple[list[ApprovedInvite], list[str]]:
        approved_invites = []
        non_approved_invites = []
        res = re.findall(r'(?:discordapp\.com/invite|discord\.gg|discord\.com/invite)/([\w]+)', message)

        for invite_code in set(res):
            if invite := self._approved_invites.get(invite_code):
                approved_invites.append(invite)
            else:
                non_approved_invites.append(invite_code)
        return approved_invites, non_approved_invites
