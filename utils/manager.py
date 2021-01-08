import re

from typing import Optional, List
from utils.models import FilteredWord, ApprovedInvite


class WordFilterManager:
    def __init__(self):
        self.kinds = ('piracy tool', 'piracy video', 'piracy tool alert', 'drama', 'unbanning tool', 'piracy site')
        self.filter = {}
        self.word_exp = {}

    async def load(self):
        for kind in self.kinds:
            self.filter[kind] = []
            for entry in await self.fetch_by_kind(kind=kind):
                self.filter[kind].append(entry.word)
                self.word_exp[entry.word] = re.compile(r"[ *_\-~]*".join(list(entry.word)))
        print("Loaded word filter")

    async def add(self, word: str, kind: str) -> FilteredWord:
        entry = await FilteredWord.create(word=word, kind=kind)
        await self.load()
        return entry

    @staticmethod
    async def fetch_by_kind(kind: str) -> List[FilteredWord]:
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


class InviteFilterManager:
    def __init__(self):
        self.invites = []

    async def load(self):
        self.invites.clear()
        self.invites = await self.fetch_all()

    async def add(self, code: str, alias: str, uses: int) -> ApprovedInvite:
        entry = await ApprovedInvite.create(code=code, uses=uses, alias=alias)
        self.invites.append(entry)
        return entry

    @staticmethod
    async def fetch_all() -> List[ApprovedInvite]:
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
