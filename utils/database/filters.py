from collections import OrderedDict
from typing import TYPE_CHECKING, NamedTuple

from .common import BaseDatabaseManager

if TYPE_CHECKING:
    from typing import AsyncGenerator
    import asyncpg

from enum import Enum


class FilterKind(Enum):
    PiracyTool = 'piracy tool'
    PiracyToolAlert = 'piracy tool alert'
    UnbanningTool = 'unbanning tool'
    PiracySite = 'piracy site'
    ScammingSite = 'scamming site'
    PiracyVideo = 'piracy video'


class LevenshteinWord(NamedTuple):
    word: str
    threshold: int
    kind: FilterKind


class FilteredWord(NamedTuple):
    word: str
    kind: FilterKind


class ApprovedInvite(NamedTuple):
    code: str
    uses: int
    alias: str


tables = {'filteredwords': OrderedDict((('word', 'TEXT'), ('kind', 'TEXT'))),
          'levenshteinwords': OrderedDict((('word', 'TEXT'), ('threshold', 'INTEGER'), ('kind', 'TEXT'))),
          'whitelistedwords': OrderedDict((('word', 'TEXT'),)),
          'approvedinvites': OrderedDict((('code', 'TEXT'), ('uses', 'INTEGER'), ('alias', 'TEXT'))),
          }


class FiltersDatabaseManager(BaseDatabaseManager, tables=tables):
    """Manages the filters database."""

    async def add_filtered_word(self, word: str, kind: str) -> int:
        return await self._insert('filteredwords', word=word, kind=kind)

    async def delete_filtered_word(self, word: str) -> int:
        return await self._delete('filteredwords', word=word)

    async def get_filtered_words(self) -> 'AsyncGenerator[FilteredWord, None]':
        async for fw in self._select('filteredwords'):
            yield FilteredWord(word=fw[0], kind=FilterKind(fw[1]))

    async def add_levenshtein_word(self, word: str, threshold: int, kind: str) -> int:
        return await self._insert('levenshteinwords', word=word, threshold=threshold, kind=kind)

    async def delete_levenshtein_word(self, word: str):
        return await self._delete('levenshteinwords', word=word)

    async def get_levenshtein_words(self) -> 'AsyncGenerator[LevenshteinWord, None]':
        async for lw in self._select('levenshteinwords'):
            yield LevenshteinWord(word=lw[0], threshold=lw[1], kind=FilterKind(lw[2]))

    async def add_whitelisted_word(self, word: str) -> int:
        return await self._insert('whitelistedwords', word=word)

    async def delete_whitelisted_word(self, word: str) -> int:
        return await self._delete('whitelistedwords', word=word)

    async def get_whitelisted_words(self) -> 'AsyncGenerator[str, None]':
        async for wl in self._select('whitelistedwords'):
            yield wl[0]

    async def add_approved_invite(self, code: str, uses: int, alias: str):
        return await self._insert('approvedinvites', code=code, uses=uses, alias=alias)

    async def delete_approved_invite(self, code: str):
        return await self._delete('approvedinvites', code=code)

    async def get_approved_invites(self):
        async for ai in self._select('approvedinvites'):
            yield ApprovedInvite(code=ai[0], uses=ai[1], alias=ai[2])

    async def update_invite_use(self, code: str):
        query = "UPDATE approvedinvites SET uses=uses-1 WHERE code=$1"
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                return await conn.execute(query, code)
