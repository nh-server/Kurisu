from typing import Optional, List
import aiosqlite3
import json
from utils.models import FilteredWord, ApprovedInvite


class Manager:

    @staticmethod
    def format_args(args: dict) -> str:
        if len(args) < 1:
            return ''
        separator = args.pop('separator', 'AND')
        statement = 'WHERE '
        conditions = []
        for kword, value in args.items():
            conditions.append(f"{kword} = '{value}'")
        return statement + f' {separator} '.join(conditions)


class WordFilterManager(Manager):
    def __init__(self, bot):
        self.kinds = ('piracy tool', 'piracy video', 'piracy tool alert', 'drama', 'unbanning tool', 'piracy site')
        self.filter = {}

    async def load(self):
        for kind in self.kinds:
            self.filter[kind] = [i[0] for i in await self.fetch(kind=kind)]
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


class InviteFilterManager(Manager):
    def __init__(self, bot):
        self.invites = []

    async def load(self):
        self.invites.clear()
        self.invites = await self.fetch()

    async def add(self, code: str, alias: str, uses: int) -> Optional[ApprovedInvite]:
        entry = await FilteredWord.create(code=code, use=uses, alias=alias)
        await self.load()
        return entry

    async def fetch(self) -> List[ApprovedInvite]:
        return await ApprovedInvite.query.gino.all()

    async def fetchinvite(self, alias) -> Optional[ApprovedInvite]:
        return await ApprovedInvite.query.where(FilteredWord.alias == alias).gino.first()

    async def set_uses(self, code: str, uses: int):
        invite = await ApprovedInvite.get(code)
        await invite.update(uses=uses).apply()
        await self.load()

    async def delete(self, code: str = "", alias: str = ""):
        if code:
            entry = await ApprovedInvite.get(code)
        elif alias:
            entry = await ApprovedInvite.query.where(FilteredWord.alias == alias).gino.first()
        if entry:
            await entry.delete()
            return entry
