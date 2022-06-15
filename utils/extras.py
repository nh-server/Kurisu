import asyncio
from datetime import datetime

from typing import TYPE_CHECKING, NamedTuple
from collections import defaultdict

import discord
from discord.utils import time_snowflake

from .managerbase import BaseManager
from .database import ExtrasDatabaseManager

if TYPE_CHECKING:
    from typing import Union, Optional
    from discord import Member, User, Role
    from kurisu import Kurisu
    from . import OptionalMember


class Tag(NamedTuple):
    id: int
    title: str
    content: str
    author_id: int


class Reminder(NamedTuple):
    id: int
    date: datetime
    author_id: int
    content: str


class TimedRole(NamedTuple):
    role_id: int
    user_id: int
    expiring_date: datetime


class ExtrasManager(BaseManager, db_manager=ExtrasDatabaseManager):
    """Manages the bot extras."""

    db: ExtrasDatabaseManager

    _auto_probation: bool = False

    def __init__(self, bot: 'Kurisu'):
        super().__init__(bot)
        asyncio.create_task(self.setup())

    async def setup(self):

        self._tags: 'dict[str, Tag]' = {t[1]: Tag(id=t[0], title=t[1], content=t[2], author_id=t[3])
                                        async for t in self.db.get_tags()}

        self._timed_roles = [TimedRole(role_id=tr[1], user_id=tr[2], expiring_date=tr[3])
                             async for tr in self.db.get_timed_roles()]

        self._reminders = defaultdict(list)
        async for r in self.db.get_reminders():
            reminder = Reminder(id=r[0], date=r[1], author_id=r[2], content=r[3])
            self._reminders[reminder.id].append(reminder)

    @property
    def tags(self) -> dict[str, Tag]:
        return self._tags

    @property
    def reminders(self) -> dict[int, list[Reminder]]:
        return self._reminders

    async def add_timed_role(self, user: 'Union[Member, User, OptionalMember]', role: 'Role', expiring_date: datetime):
        res = await self.db.add_timed_role(user.id, role.id, expiring_date)
        if res:
            self._timed_roles.append(TimedRole(role_id=role.id, user_id=user.id, expiring_date=expiring_date))

    async def delete_timed_role(self, user: 'Union[Member, User, OptionalMember]', role: 'Role'):

        res = await self.db.delete_timed_role(user.id, role.id)
        if res:
            #  TODO There must be some better way to do this
            s = discord.utils.get(self._timed_roles, user_id=user.id, role_id=role.id)
            if s:
                self._timed_roles.remove(s)

    async def add_3ds_friend_code(self, user: 'Union[Member, User, OptionalMember]', fc: int):
        await self.db.add_3ds_friend_code(user.id, fc)

    async def add_switch_friend_code(self, user: 'Union[Member, User, OptionalMember]', fc: int):
        await self.db.add_switch_friend_code(user.id, fc)

    # async def delete_friend_code(self, user_id: int):
    #     await self._delete('friendcodes', id=user_id)
    #
    # async def update_3ds_friend_code(self, user_id: int, fc: 'Optional[int]'):
    #     await self._update('friendcodes', {'fc_3ds': fc}, user_id=user_id)
    #
    # async def update_switch_friend_code(self, user_id: int, fc: 'Optional[int]'):
    #     await self._update('friendcodes', {'fc_3ds': fc}, user_id=user_id)

    async def add_reminder(self, date: datetime, author: 'Union[Member, User, OptionalMember]', content: str) -> int:
        now = time_snowflake(datetime.now())
        res = await self.db.add_reminder(now, date, author.id, content)
        if res:
            self._reminders[author.id].append(Reminder(id=now, date=date, author_id=author.id, content=content))
        return res

    async def delete_reminder(self, reminder_id, author_id: int):
        await self.db.delete_reminder(reminder_id)
        del self._reminders[author_id]

    async def add_tag(self, title: str, content: str, author: int):
        now = time_snowflake(datetime.now())
        await self.db.add_tag(now, title, content, author)
        self._tags[title] = Tag(id=now, title=title, content=content, author_id=author)

    async def update_tag(self, title: str, content: str):
        await self.db.update_tag(title, content)
        old_tag = self._tags[title]
        self._tags[title] = Tag(id=old_tag.id, title=title, content=content, author_id=old_tag.author_id)

    async def delete_tag(self, title: str):
        await self.db.delete_tag(title)
        del self._tags[title]

    def search_tags(self, tag_name: str, *, limit=10) -> list[str]:
        res = []
        for tag in self._tags:
            if tag_name in tag:
                res.append(tag)
        return res

    async def add_voteview(self, view_id: int, message_id, identifier: str, author_id: int,
                           options: str, start: 'Optional[datetime]', staff_only: bool):
        await self.db.add_voteview(view_id=view_id, message_id=message_id, identifier=identifier, author_id=author_id,
                                   options=options, start=start, staff_only=staff_only)

    async def delete_voteview(self, view_id: int):
        await self.db.delete_voteview(view_id)

    async def add_vote(self, view_id: int, voter_id: int, option: str):
        await self.db.add_vote(view_id, voter_id, option)

    async def get_votes(self, view_id: int):
        async for v in self.db.get_votes(view_id):
            yield v

    async def add_citizen(self, citizen_id: int):
        return await self.db.add_citizen(citizen_id)

    async def get_citizen(self, citizen_id: int):
        return await self.db.get_citizen(citizen_id)

    async def delete_citizen(self, citizen_id: int):
        await self.db.delete_citizen(citizen_id)

    async def add_social_credit(self, citizen_id: int, amount: int):
        citizen = await self.get_citizen(citizen_id)
        if not citizen:
            await self.add_citizen(citizen_id)
            citizen = await self.get_citizen(citizen_id)
        amount = citizen.social_credit + amount
        await self.db.set_social_credit(citizen_id, amount)
