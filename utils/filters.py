import asyncio
import re
from typing import TYPE_CHECKING
from Levenshtein import distance

from .managerbase import BaseManager
from .database import FiltersDatabaseManager

if TYPE_CHECKING:
    from kurisu import Kurisu
    from .database import LevenshteinWord, FilteredWord, FilterKind

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

    @property
    def whitelist(self):
        return self._whitelist

    @property
    def lsh_words(self):
        return self._lsh_words

    @property
    def filtered_words(self):
        return self._filtered_words

    async def add_filtered_word(self, word: str, kind: 'FilterKind'):
        await self.db.add_filtered_word(word, kind.value)

    async def delete_filtered_word(self, word: str) -> int:
        return await self.db.delete_filtered_word(word)

    async def add_levenshtein_word(self, word: str, threshold: int, kind: 'FilterKind') -> int:
        return await self.db.add_levenshtein_word(word, threshold, kind.value)

    async def delete_levenshtein_word(self, word: str) -> int:
        return await self.db.delete_levenshtein_word(word)

    async def add_whitelisted_word(self, word: str) -> int:
        return await self.db.add_whitelisted_word(word)

    async def delete_whitelisted_word(self, word: str) -> int:
        return await self.db.delete_whitelisted_word(word)

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
