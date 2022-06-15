from collections import OrderedDict
from typing import TYPE_CHECKING, NamedTuple

from .common import BaseDatabaseManager

if TYPE_CHECKING:
    from typing import AsyncGenerator, Tuple, Optional
    import asyncpg


# I can't really think of a use for this... maybe I'll remove it if nothing happens.


class ChangedRole(NamedTuple):
    role_id: int
    channel_id: int
    original_value: 'Optional[bool]'


class DatabaseChannel(NamedTuple):
    channel_id: int
    name: str
    private: bool
    filtered: bool
    lock_level: int
    mod_channel: bool


tables = {'flags': OrderedDict((('name', 'TEXT'), ('value', 'BOOLEAN'))),
          'staff': OrderedDict((('user_id', 'BIGINT'), ('position', 'TEXT'), ('console', 'TEXT'))),
          'members': OrderedDict((('id', 'BIGINT'), ('watched', 'bool'))),
          'membernotes': OrderedDict((('staff_id', 'BIGINT'), ('user_id', 'BIGINT'), ('note', 'bool'))),
          'memberlinks': OrderedDict((('id', 'BIGINT'), ('watched', 'bool'))),
          'channels': OrderedDict((('id', 'BIGINT'), ('name', 'TEXT'),
                                   ('filtered', 'BOOLEAN'), ('lock_level', 'INTEGER'), ('mod_channel', 'BOOLEAN'))),
          'changedroles': OrderedDict((('role_id', 'BIGINT'), ('channel_id', 'BIGINT'), ('original_value', 'BOOLEAN'))),
          'roles': OrderedDict((('id', 'BIGINT'), ('name', 'TEXT'))),
          'rules': OrderedDict((('id', 'BIGINT'), ('description', 'TEXT')))}


class ConfigurationDatabaseManager(BaseDatabaseManager, tables=tables):
    """Manages the configuration database."""

    async def add_member(self, member_id: int):
        query = "INSERT INTO members VALUES ($1) ON CONFLICT (id) DO NOTHING"
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(query, member_id)

    async def get_members(self) -> 'AsyncGenerator[tuple[int, bool], None]':
        async for m in self._select('members'):
            yield m

    async def set_watch(self, user_id: int, watched: bool):
        await self.add_member(user_id)
        await self._update('members', {'watched': watched}, id=user_id)

    async def add_flag(self, name: str, value: 'Optional[bool]'):
        await self._insert('flags', name=name, value=value)

    async def set_flag(self, name: str, value: 'Optional[bool]'):
        await self._update('flags', {'value': value}, name=name)

    async def get_all_flags(self) -> 'AsyncGenerator[Tuple[str, bool], None]':
        async for k, v in self._select('flags'):
            yield k, v

    async def get_flag(self, name: str) -> 'Optional[tuple[str, bool]]':
        # TODO is this fine?
        async for name, value in self._select('flags', name=name):
            return name, value

    async def delete_flag(self, name: str):
        await self._delete('flags', name=name)

    async def add_staff_member(self, user_id: int, position: str):
        await self.add_member(user_id)
        await self._insert('staff', user_id=user_id, position=position)

    async def add_helper(self, user_id: int, console: str):
        await self.add_member(user_id)
        await self._insert('staff', user_id=user_id, console=console)

    async def set_staff_level(self, user_id: int, position: str):
        await self._update('staff', {'position': position}, user_id=user_id)

    async def set_helper_console(self, user_id: int, console: str):
        await self._update('staff', {'console': console}, user_id=user_id)

    async def remove_staff_position(self, user_id: int):
        await self._update('staff', {'position': None}, user_id=user_id)

    async def remove_helper_console(self, user_id: int):
        await self._update('staff', {'console': None}, user_id=user_id)

    async def delete_staff(self, user_id):
        await self._delete('staff', user_id=user_id)

    async def get_all_staff(self) -> 'AsyncGenerator[Tuple[int, str], None]':
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                async for snowflake, position, _ in conn.cursor("SELECT * FROM staff WHERE position IS NOT NULL"):
                    yield snowflake, position

    async def get_all_helpers(self) -> 'AsyncGenerator[Tuple[int, str], None]':
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                async for snowflake, _, console in conn.cursor("SELECT * FROM staff WHERE console IS NOT NULL"):
                    yield snowflake, console

    async def add_channel(self, channel_id: int, name: str):
        await self._insert('channels', id=channel_id, name=name)

    async def get_channel(self, channel_id: int):
        async for c in self._select('channels', id=channel_id):
            return c

    async def get_channel_by_name(self, name: str) -> 'Optional[tuple[int, str, bool, int, bool]]':
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                return await conn.fetchrow("SELECT * from channels WHERE name=$1", name)

    async def update_channel(self, channel_id: int, name: str):
        await self._update('channels', {'id': channel_id}, name=name)

    async def set_channel_lock_level(self, channel_id: int, lock_level: int):
        await self._update('channels', {'lock_level': lock_level}, id=channel_id)

    async def set_nofilter_channel(self, channel_id: int, filtered: bool):
        await self._update('channels', {'filtered': filtered}, id=channel_id)

    async def get_all_nofilter_channels(self) -> 'AsyncGenerator[int, None]':
        async for channel_id, *_ in self._select('channels', filtered=False):
            yield channel_id

    async def add_role(self, name: str, role_id: int):
        await self._insert('roles', id=role_id, name=name)

    async def get_role(self, name: str) -> 'Optional[tuple[int, str]]':
        async for role_id, name in self._select('roles', name=name):
            return role_id, name
        return None

    async def update_role(self, name: str, role_id: int):
        await self._update('roles', {role_id: role_id}, name=name)

    async def add_changed_roles(self, role_id_list: list[int], channel_id: int):
        query = "INSERT INTO changedroles VALUES ($1,$2)"
        values = []
        for role_id in role_id_list:
            values.append((role_id, channel_id))

        conn: asyncpg.Connection

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.executemany(query, values)

    async def delete_changed_role(self, role_id: int, channel_id: int):
        await self._delete('changedroles', role_id=role_id, channel_id=channel_id)

    async def get_changed_roles(self, channel_id: int) -> 'AsyncGenerator[ChangedRole, None]':
        async for cr in self._select('changed_roles', channel_id=channel_id):
            yield ChangedRole(role_id=cr[0], channel_id=cr[1], original_value=cr[2])

    async def clear_changed_role(self, channel_id):
        await self._delete('changedroles', channel_id=channel_id)

    async def add_rule(self, rule_id, content: str):
        await self._insert('rules', id=rule_id, description=content)

    async def edit_rule(self, rule_id: int, content: str):
        await self._update('rules', {'content': content}, id=rule_id)

    async def delete_rule(self, rule_id: int):
        await self._delete('rules', id=rule_id)

    async def get_rules(self) -> 'AsyncGenerator[tuple[int, str], None]':
        async for r in self._select('rules'):
            yield r
