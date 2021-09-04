import re

from typing import Optional
from utils.models import FilteredWord, LevenshteinWord, ApprovedInvite, WhitelistWord


class WordFilterManager:
    def __init__(self):
        self.kinds = ('piracy tool', 'piracy video', 'piracy tool alert', 'drama', 'unbanning tool', 'piracy site', 'scamming site')
        self.filter: dict[str, list[str]] = {}
        self.word_exp = {}

    async def load(self):
        for kind in self.kinds:
            self.filter[kind] = []
            for entry in await self.fetch_by_kind(kind=kind):
                self.filter[kind].append(entry.word)
                self.word_exp[entry.word] = re.compile(r"[ *_\-~]*".join(list(entry.word)))

    async def add(self, word: str, kind: str) -> FilteredWord:
        entry = await FilteredWord.create(word=word, kind=kind)
        await self.load()
        return entry

    @staticmethod
    async def fetch_by_kind(kind: str) -> list[FilteredWord]:
        return await FilteredWord.query.where(FilteredWord.kind == kind).gino.all()

    @staticmethod
    async def fetch_word(word: str) -> Optional[FilteredWord]:
        return await FilteredWord.get(word)

    async def delete(self, word: str) -> Optional[FilteredWord]:
        entry = await self.fetch_word(word)
        if entry:
            await entry.delete()
            self.filter[entry.kind].remove(entry.word)
            del self.word_exp[entry.word]
        return entry


class LevenshteinFilterManager:
    def __init__(self):
        self.kinds = ('scamming site',)
        self.filter: dict[str, list[tuple[str, int]]] = {}
        self.whitelist: list[str] = []

    async def load(self):
        self.whitelist = await self.fetch_whitelist()
        for kind in self.kinds:
            self.filter[kind] = []
            for entry in await self.fetch_by_kind(kind=kind):
                self.filter[kind].append((entry.word, entry.threshold))
                if entry.whitelist:
                    self.whitelist.append(entry.word)

    async def add(self, word: str, kind: str, threshold: int, whitelist: bool) -> LevenshteinWord:
        entry = await LevenshteinWord.create(word=word, kind=kind, threshold=threshold, whitelist=whitelist)
        await self.load()
        return entry

    async def edit(self, word: str, threshold: int, whitelist: bool) -> LevenshteinWord:
        entry = await self.fetch_word(word)
        await entry.update(threshold=threshold, whitelist=whitelist).apply()
        return entry

    async def add_whitelist_word(self, word: str) -> WhitelistWord:
        entry = await WhitelistWord.create(word=word)
        self.whitelist.append(word)
        return entry

    @staticmethod
    async def fetch_by_kind(kind: str) -> list[LevenshteinWord]:
        return await LevenshteinWord.query.where(LevenshteinWord.kind == kind).gino.all()

    @staticmethod
    async def fetch_word(word: str) -> Optional[LevenshteinWord]:
        return await LevenshteinWord.get(word)

    @staticmethod
    async def fetch_whitelist_word(word: str) -> Optional[WhitelistWord]:
        return await WhitelistWord.get(word)

    async def fetch_whitelist(self) -> list[WhitelistWord]:
        return await WhitelistWord.query.gino.all()

    async def delete(self, word: str) -> Optional[LevenshteinWord]:
        entry = await self.fetch_word(word)
        if entry:
            await entry.delete()
            self.filter[entry.kind].remove((entry.word, entry.threshold))
        return entry

    async def delete_whitelist_word(self, word: str) -> Optional[WhitelistWord]:
        entry = await self.fetch_whitelist_word(word)
        if entry:
            await entry.delete()
            self.whitelist.remove(word)
        return entry


class InviteFilterManager:
    def __init__(self):
        self.invites: list[ApprovedInvite] = []

    async def load(self):
        self.invites.clear()
        self.invites = await self.fetch_all()

    async def add(self, code: str, alias: str, uses: int) -> ApprovedInvite:
        entry = await ApprovedInvite.create(code=code, uses=uses, alias=alias)
        self.invites.append(entry)
        return entry

    @staticmethod
    async def fetch_all() -> list[ApprovedInvite]:
        return await ApprovedInvite.query.gino.all()

    @staticmethod
    async def fetch_invite_by_alias(alias) -> Optional[ApprovedInvite]:
        return await ApprovedInvite.query.where(ApprovedInvite.alias == alias).gino.first()

    @staticmethod
    async def fetch_invite_by_code(code) -> Optional[ApprovedInvite]:
        return await ApprovedInvite.get(code)

    async def set_uses(self, code: str, uses: int):
        invite = await ApprovedInvite.get(code)
        await invite.update(uses=uses).apply()
        await self.load()

    async def delete(self, code: str):
        entry = await self.fetch_invite_by_code(code)
        if entry:
            await entry.delete()
            await self.load()
        return entry
