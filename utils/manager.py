import re

from Levenshtein import distance
from typing import Optional
from utils.models import FilteredWord, LevenshteinWord, ApprovedInvite, WhitelistWord


async def check_collisions() -> Optional[dict[str, list]]:
    filtered_words = await FilteredWord.query.gino.all()
    levenshtein_words = await LevenshteinWord.query.gino.all()
    collisions = {}
    for lword in levenshtein_words:
        for fword in filtered_words:
            if distance(lword.word, fword.word) < lword.threshold:
                if lword.word not in collisions:
                    collisions[lword.word] = []
                collisions[lword.word].append(fword.word)

    return collisions


class WordFilterManager:
    def __init__(self):
        self.kinds = ('piracy tool', 'piracy tool alert', 'unbanning tool', 'piracy site', 'scamming site', 'piracy video')
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
        return await FilteredWord.query.where(FilteredWord.kind == kind).order_by(FilteredWord.word).gino.all()

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

    def search_word(self, message: str) -> tuple[str, dict]:
        msg_no_sep = re.sub(r'[ *_\-~]', '', message)
        matches = {}
        for kind in self.kinds[:-1]:
            matches[kind] = []
            for word in self.filter[kind]:
                if word in msg_no_sep and (match := self.word_exp[word].search(message)):
                    matches[kind].append(match)
                    a, b = match.span(0)
                    message = f"{message[:a]}**{match.group(0)}**{message[b:]}"
                    matches[kind].append(word)
        return message, matches

    def search_video(self, message: str) -> tuple[bool, bool]:
        res = re.findall(r'((?:https?://)?(?:www.)?)(?:(youtube\.com/watch\?v=)|(youtu\.be/))([aA-zZ_\-\d]{11})', message)
        contains_video = any(res)
        contains_piracy_video = False if not contains_video else any(x for x in res if x in self.filter['piracy video'])
        return contains_video, contains_piracy_video


class LevenshteinFilterManager:
    def __init__(self):
        self.kinds = ('scamming site',)
        self.filter: dict[str, list[tuple[str, int]]] = {}
        self.whitelist: list[str] = []

    async def load(self):
        self.whitelist = [entry.word for entry in await self.fetch_whitelist()]
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

    def search_site(self, message: str, filter_name: str) -> list[str]:
        lfilter = self.filter[filter_name]
        matches = []
        message = message[::-1]
        to_check = re.findall(r"([\w0-9-]+\.[\w0-9-]+)", message)

        for word in to_check:
            if word in self.whitelist:
                continue
            word = word[::-1]
            for trigger, threshold in lfilter:
                lf_distance = distance(word, trigger)
                if lf_distance < threshold:
                    matches.append(word)
        return matches


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

    def search_invite(self, message: str):
        approved_invites = []
        non_approved_invites = []
        res = re.findall(r'(?:discordapp\.com/invite|discord\.gg|discord\.com/invite)/([\w]+)', message)
        for invite_code in res:
            if any([x for x in self.invites if x.code in res]):
                approved_invites.append(invite_code)
            else:
                non_approved_invites.append(invite_code)
        return approved_invites, non_approved_invites
