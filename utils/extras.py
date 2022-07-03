import asyncio
from datetime import datetime

from typing import TYPE_CHECKING
from collections import defaultdict
import discord
from discord.utils import time_snowflake

from .managerbase import BaseManager
from .database import ExtrasDatabaseManager, Tag, TimedRole, Reminder


if TYPE_CHECKING:
    from typing import Union, Optional
    from discord import Member, User, Role
    from kurisu import Kurisu
    from . import OptionalMember


class ExtrasManager(BaseManager, db_manager=ExtrasDatabaseManager):
    """Manages the bot extras."""

    db: ExtrasDatabaseManager

    _auto_probation: bool = False

    def __init__(self, bot: 'Kurisu'):
        super().__init__(bot)
        asyncio.create_task(self.setup())

    async def setup(self):

        self._tags: 'dict[str, Tag]' = {t.title: t async for t in self.db.get_tags()}

        self._timed_roles: 'list[TimedRole]' = [tr async for tr in self.db.get_timed_roles()]

        self._reminders = defaultdict(list)

        async for r in self.db.get_reminders():
            self._reminders[r.author_id].append(r)

    @property
    def tags(self) -> 'dict[str, Tag]':
        return self._tags

    @property
    def reminders(self) -> 'dict[int, list[Reminder]]':
        return self._reminders

    @property
    def timed_roles(self) -> 'list[TimedRole]':
        return self._timed_roles

    async def add_timed_role(self, user: 'Union[Member, User, OptionalMember]', role: 'Role', expiring_date: datetime):
        res = await self.db.add_timed_role(role.id, user.id, expiring_date)
        if res:
            self._timed_roles.append(TimedRole(role_id=role.id, user_id=user.id, expiring_date=expiring_date))
        return res

    async def delete_timed_role(self, user_id: int, role_id: int):

        res = await self.db.delete_timed_role(user_id, role_id)
        if res:
            #  TODO There must be some better way to do this
            s = discord.utils.get(self._timed_roles, user_id=user_id, role_id=role_id)
            if s:
                self._timed_roles.remove(s)
        return res

    async def add_3ds_friend_code(self, user: 'Union[Member, User, OptionalMember]', fc: int):
        return await self.db.add_3ds_friend_code(user.id, fc)

    async def add_switch_friend_code(self, user: 'Union[Member, User, OptionalMember]', fc: int):
        return await self.db.add_switch_friend_code(user.id, fc)

    async def get_friend_code(self, user_id: int):
        return await self.db.get_friend_code(user_id)

    async def delete_switch_friend_code(self, user_id: int):
        return await self.db.delete_switch_friend_code(user_id)

    async def delete_3ds_friend_code(self, user_id: int):
        return await self.db.delete_3ds_friend_code(user_id)

    async def add_reminder(self, date: datetime, author: 'Union[Member, User, OptionalMember]', content: str) -> int:
        now = time_snowflake(datetime.now())
        res = await self.db.add_reminder(now, date, author.id, content)
        if res:
            self._reminders[author.id].append(Reminder(id=now, date=date, author_id=author.id, content=content))
        return res

    async def delete_reminder(self, reminder_id, author_id: int):
        res = await self.db.delete_reminder(reminder_id)
        if res:
            del self._reminders[author_id]
        return res

    async def add_tag(self, title: str, content: str, author: int):
        now = time_snowflake(datetime.now())
        res = await self.db.add_tag(now, title, content, author)
        if res:
            self._tags[title] = Tag(id=now, title=title, content=content, author_id=author)
        return res

    async def update_tag(self, title: str, content: str):
        res = await self.db.update_tag(title, content)
        if res:
            old_tag = self._tags[title]
            self._tags[title] = Tag(id=old_tag.id, title=title, content=content, author_id=old_tag.author_id)
        return res

    async def delete_tag(self, title: str):
        res = await self.db.delete_tag(title)
        if res:
            del self._tags[title]
        return res

    def search_tags(self, tag_name: str, *, limit=10) -> list[str]:
        res = []
        for tag in self._tags:
            if tag_name in tag:
                res.append(tag)
            if len(res) == limit:
                break
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
        assert citizen is not None
        amount = citizen.social_credit + amount
        await self.db.set_social_credit(citizen_id, amount)
