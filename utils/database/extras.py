
from collections import OrderedDict
from datetime import datetime
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


tables = {'timedroles': OrderedDict((('id', 'BIGINT'), ('role_id', 'BIGINT'), ('user_id', 'BIGINT'), ('expiring_date', 'BIGINT'))),
          'friendcodes': OrderedDict((('id', 'BIGINT'), ('fc_3ds', 'BIGINT'), ('fc_switch', 'BIGINT'))),
          'reminders': OrderedDict((('id', 'BIGINT'), ('date', 'TIME'),
                                   ('author', 'BIGINTN'), ('reminder', 'INTEGER'))),
          'tags': OrderedDict((('id', 'BIGINT'), ('title', 'TEXT'), ('content', 'TEXT'), ('author', 'BIGINT'))),
          'voteviews': OrderedDict((('id', 'BIGINT'), ('message_id', 'BIGINT'), ('identifier', 'BIGINT'),
                                    ('message_id', 'BIGINT'), ('message_id', 'BIGINT'), ('message_id', 'BIGINT'))),
          'votes': OrderedDict((('view_id', 'BIGINT'), ('voter_id', 'BIGINT'), ('option', 'TEXT')))}


class ExtrasDatabaseManager(BaseDatabaseManager, tables=tables):
    """Manages the extras database."""

    async def add_timed_role(self, role_id: int, user_id: int, expiring_date: datetime):
        await self.bot.configuration.add_member(user_id)
        return await self._insert('timedroles', role_id=role_id, user_id=user_id, expiring_date=expiring_date)

    async def delete_timed_role(self, user_id: int, role_id: int):
        return await self._delete('timedroles', user_id=user_id, role_id=role_id)

    async def get_timed_roles(self) -> 'AsyncGenerator[tuple[int, int, int, datetime], None]':
        async for p in self._select('timedroles'):
            yield p

    async def add_3ds_friend_code(self, user_id: int, fc: int):
        await self.bot.configuration.add_member(user_id)
        return await self._insert('friendcodes', id=user_id, fc_3ds=fc)

    async def add_switch_friend_code(self, user_id: int, fc: int):
        await self.bot.configuration.add_member(user_id)
        return await self._insert('friendcodes', id=user_id, fc_switch=fc)

    async def delete_friend_code(self, user_id: int):
        return await self._delete('friendcodes', id=user_id)

    async def update_3ds_friend_code(self, user_id: int, fc: 'Optional[int]'):
        await self._update('friendcodes', {'fc_3ds': fc}, user_id=user_id)

    async def update_switch_friend_code(self, user_id: int, fc: 'Optional[int]'):
        await self._update('friendcodes', {'fc_3ds': fc}, user_id=user_id)

    async def add_tag(self, tag_id: int, title: str, content: str, author_id: int):
        await self.bot.configuration.add_member(author_id)
        return await self._insert('tags', id=tag_id, title=title, content=content, author_id=author_id)

    async def update_tag(self, title: str, content: str):
        return await self._update('tags', {'content': content}, title=title)

    async def delete_tag(self, title: str):
        return await self._delete('tags', title=title)

    async def get_tags(self):
        async for t in self._select('tags'):
            yield t

    async def add_reminder(self, reminder_id: int, date: datetime, author_id: int, content: str) -> int:
        await self.bot.configuration.add_member(author_id)
        return await self._insert('reminders', id=reminder_id, date=date, author_id=author_id, reminder=content)

    async def delete_reminder(self, reminder_id: int) -> int:
        return await self._delete('reminders', id=reminder_id)

    async def get_reminders(self) -> 'AsyncGenerator[tuple[int, datetime, int, str], None]':
        async for r in self._select('reminders'):
            yield r

    async def add_voteview(self, view_id: int, message_id, identifier: str, author_id: int,
                           options: str, start: 'Optional[datetime]', staff_only: bool):
        await self._insert('voteviews', id=view_id, message_id=message_id, identifier=identifier, author_id=author_id,
                           options=options, start=start, staff_only=staff_only)

    async def delete_voteview(self, view_id: int):
        await self._delete('voteviews', id=view_id)

    async def add_vote(self, view_id: int, voter_id: int, option: str):
        await self.bot.configuration.add_member(voter_id)

        query = "INSERT INTO votes VALUES($1,$2,$3) ON CONFLICT (view_id, voter_id) DO UPDATE SET option=excluded.option"
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(query, view_id, voter_id, option)

    async def update_vote(self, view_id: int, voter_id: int, option: str):
        await self._update('voteviews', {'option': option}, view_id=view_id, voter_id=voter_id)

    async def get_votes(self, view_id: int):
        async for v in self._select('votes', view_id=view_id):
            yield Vote(view_id=v[0], voter_id=v[1], option=v[2])

    async def add_citizen(self, citizen_id: int):
        await self.bot.configuration.add_member(citizen_id)
        await self._insert('citizens', id=citizen_id)

    async def get_citizen(self, citizen_id: int) -> 'Optional[Citizen]':
        res = await self._select_one('citizens', id=citizen_id)
        if res:
            return Citizen(id=res[0], social_credit=res[1])

    async def delete_citizen(self, citizen_id: int):
        await self._delete('citizens', id=citizen_id)

    async def set_social_credit(self, citizen_id: int, amount: int):
        await self._update('citizens', {'social_credit': amount}, id=citizen_id)
