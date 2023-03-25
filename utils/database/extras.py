from datetime import datetime
from discord.utils import time_snowflake
from typing import TYPE_CHECKING, NamedTuple

from .common import BaseDatabaseManager

if TYPE_CHECKING:
    from typing import AsyncGenerator, Optional
    import asyncpg


# I can't really think of a use for this... maybe I'll remove it if nothing happens.


class ChangedRole(NamedTuple):
    role_id: int
    channel_id: int
    original_value: 'Optional[bool]'


class Vote(NamedTuple):
    view_id: int
    voter_id: int
    option: str


class Citizen(NamedTuple):
    id: int
    social_credit: int


class DatabaseChannel(NamedTuple):
    channel_id: int
    name: str
    private: bool
    filtered: bool
    lock_level: int
    mod_channel: bool


class FriendCode(NamedTuple):
    user_id: int
    fc_3ds: int
    fc_switch: int


class Tag(NamedTuple):
    id: int
    title: str
    content: str
    author_id: int
    aliases: 'Optional[list[str]]'


class Reminder(NamedTuple):
    id: int
    date: datetime
    author_id: int
    content: str


class TimedRole(NamedTuple):
    role_id: int
    user_id: int
    expiring_date: datetime


tables = {'timedroles': ['id', 'role_id', 'user_id', 'expiring_date'],
          'friendcodes': ['user_id', 'fc_3ds', 'fc_switch'],
          'reminders': ['id', 'reminder_date', 'author_id', 'content'],
          'tags': ['id', 'title', 'content', 'author_id'],
          'tag_aliases': ['tag_id', 'alias'],
          'voteviews': ['id', 'message_id', 'identifier', 'author_id', 'options', 'start', 'staff_only'],
          'votes': ['view_id', 'voter_id', 'option'],
          'citizens': ['id', 'social_credit']}


class ExtrasDatabaseManager(BaseDatabaseManager, tables=tables):
    """Manages the extras database."""

    async def add_timed_role(self, role_id: int, user_id: int, expiring_date: datetime):
        await self.bot.configuration.add_member(user_id)
        now = time_snowflake(datetime.now())
        return await self._insert('timedroles', id=now, role_id=role_id, user_id=user_id, expiring_date=expiring_date)

    async def delete_timed_role(self, user_id: int, role_id: int):
        return await self._delete('timedroles', user_id=user_id, role_id=role_id)

    async def get_timed_roles(self) -> 'AsyncGenerator[TimedRole, None]':
        async for p in self._select('timedroles'):
            yield TimedRole(role_id=p[1], user_id=p[2], expiring_date=p[3])

    async def add_3ds_friend_code(self, user_id: int, fc: int):
        await self.bot.configuration.add_member(user_id)
        return await self._insert('friendcodes', user_id=user_id, fc_3ds=fc)

    async def add_switch_friend_code(self, user_id: int, fc: int):
        await self.bot.configuration.add_member(user_id)
        return await self._insert('friendcodes', user_id=user_id, fc_switch=fc)

    async def delete_friend_code(self, user_id: int):
        return await self._delete('friendcodes', user_id=user_id)

    async def delete_switch_friend_code(self, user_id: int):
        fcs = await self.get_friend_code(user_id)
        if fcs:
            res = await self._update('friendcodes', {'fc_switch': None}, user_id=user_id)
            if res and fcs.fc_3ds is None:
                await self.delete_friend_code(user_id)
            return res

    async def delete_3ds_friend_code(self, user_id: int):
        fcs = await self.get_friend_code(user_id)
        if fcs:
            res = await self._update('friendcodes', {'fc_3ds': None}, user_id=user_id)
            if res and fcs.fc_switch is None:
                await self.delete_friend_code(user_id)
            return res

    async def get_friend_code(self, user_id: int) -> 'Optional[FriendCode]':
        res = await self._select_one('friendcodes', user_id=user_id)
        if not res:
            return
        return FriendCode(user_id=res[0], fc_3ds=res[1], fc_switch=res[2])

    async def add_tag(self, tag_id: int, title: str, content: str, author_id: int):
        await self.bot.configuration.add_member(author_id)
        return await self._insert('tags', id=tag_id, title=title, content=content, author_id=author_id)

    async def update_tag(self, title: str, content: str):
        return await self._update('tags', {'content': content}, title=title)

    async def delete_tag(self, title: str):
        return await self._delete('tags', title=title)

    async def get_tags(self):
        async for t in self._select('tags'):
            yield Tag(id=t[0], title=t[1], content=t[2], author_id=t[3], aliases=None)

    async def get_tags_with_aliases(self):
        conn: asyncpg.Connection

        query = "select *, ARRAY(SELECT alias from tags left join tag_aliases ta on tags.id = ta.tag_id) as aliases from tags"

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                async for t in conn.cursor(query):
                    yield Tag(id=t[0], title=t[1], content=t[2], author_id=t[3], aliases=t[4])

    async def add_reminder(self, reminder_id: int, date: datetime, author_id: int, content: str) -> int:
        await self.bot.configuration.add_member(author_id)
        return await self._insert('reminders', id=reminder_id, reminder_date=date, author_id=author_id, content=content)

    async def delete_reminder(self, reminder_id: int) -> int:
        return await self._delete('reminders', id=reminder_id)

    async def get_reminders(self) -> 'AsyncGenerator[Reminder, None]':
        async for r in self._select('reminders'):
            yield Reminder(id=r[0], date=r[1], author_id=r[2], content=r[3])

    async def add_voteview(self, view_id: int, message_id, identifier: str, author_id: int,
                           options: str, start: 'Optional[datetime]', staff_only: bool):
        return await self._insert('voteviews', id=view_id, message_id=message_id, identifier=identifier,
                                  author_id=author_id,
                                  options=options, start=start, staff_only=staff_only)

    async def get_voteviews(self, identifier) -> 'AsyncGenerator[tuple[int, int, str, int, str, datetime, bool], None]':
        async for vv in self._select('voteviews', identifier=identifier):
            yield vv

    async def delete_voteview(self, view_id: int) -> int:
        return await self._delete('voteviews', id=view_id)

    async def add_vote(self, view_id: int, voter_id: int, option: str) -> int:
        await self.bot.configuration.add_member(voter_id)

        query = "INSERT INTO votes VALUES($1,$2,$3) ON CONFLICT (view_id, voter_id) DO UPDATE SET option=excluded.option"
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                res = await conn.execute(query, view_id, voter_id, option)
        return self._parse_status(res)

    async def update_vote(self, view_id: int, voter_id: int, option: str):
        await self._update('voteviews', {'option': option}, view_id=view_id, voter_id=voter_id)

    async def get_votes(self, view_id: int) -> 'AsyncGenerator[Vote, None]':
        async for v in self._select('votes', view_id=view_id):
            yield Vote(view_id=v[0], voter_id=v[1], option=v[2])

    async def add_citizen(self, citizen_id: int) -> int:
        await self.bot.configuration.add_member(citizen_id)
        return await self._insert('citizens', id=citizen_id)

    async def get_citizen(self, citizen_id: int) -> 'Optional[Citizen]':
        res = await self._select_one('citizens', id=citizen_id)
        if res:
            return Citizen(id=res[0], social_credit=res[1])

    async def delete_citizen(self, citizen_id: int) -> int:
        return await self._delete('citizens', id=citizen_id)

    async def set_social_credit(self, citizen_id: int, amount: int) -> int:
        return await self._update('citizens', {'social_credit': amount}, id=citizen_id)

    async def add_tag_alias(self, tag_id: int, alias: str):
        return await self._insert('tag_aliases', tag_id=tag_id, alias=alias)

    async def delete_tag_alias(self, tag_id: int, alias: str):
        return await self._delete('tag_aliases', tag_id=tag_id, alias=alias)
