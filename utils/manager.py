from typing import Optional, List
from utils.models import FilteredWord, ApprovedInvite


class WordFilterManager:
    def __init__(self):
        self.kinds = ('piracy tool', 'piracy video', 'piracy tool alert', 'drama', 'unbanning tool', 'piracy site')
        self.filter = {}

    async def load(self):
        for kind in self.kinds:
            self.filter[kind] = [entry.word for entry in await self.fetch(kind=kind)]
        print("Loaded word filter")

    async def add(self, word: str, kind: str) -> FilteredWord:
        entry = await FilteredWord.create(word=word, kind=kind)
        await self.load()
        return entry

    async def fetch(self, kind: str) -> List[FilteredWord]:
        return await FilteredWord.query.where(FilteredWord.kind == kind).gino.all()

    async def delete(self, word: str):
        entry = await FilteredWord.get(word)
        if entry:
            await entry.delete()
            return entry


class InviteFilterManager:
    def __init__(self):
        self.invites = []

    async def load(self):
        self.invites.clear()
        self.invites = await self.fetch_all()

    async def add(self, code: str, alias: str, uses: int) -> Optional[ApprovedInvite]:
        entry = await ApprovedInvite.create(code=code, uses=uses, alias=alias)
        await self.load()
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
            return entry
