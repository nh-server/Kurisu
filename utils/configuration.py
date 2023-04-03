import asyncio

from discord import Member, User, Role, Object, PermissionOverwrite
from enum import IntEnum
from typing import TYPE_CHECKING, NamedTuple

import discord

from .managerbase import BaseManager
from .database import ConfigurationDatabaseManager

if TYPE_CHECKING:
    from typing import Optional, AsyncGenerator
    from kurisu import Kurisu
    from . import OptionalMember
    from .database import ChangedRole


class StaffRank(IntEnum):
    Owner = 0
    SuperOP = 1
    OP = 2
    HalfOP = 3
    Staff = 3
    Helper = 4


class DBChannel(NamedTuple):
    id: int
    name: str
    filtered: bool
    lock_level: int
    mod_channel: int


class ConfigurationManager(BaseManager, db_manager=ConfigurationDatabaseManager):
    """Manages bot configuration."""

    db: ConfigurationDatabaseManager

    _auto_probation: bool = False

    def __init__(self, bot: 'Kurisu'):
        super().__init__(bot)
        asyncio.create_task(self.setup())

    async def setup(self):
        flag = await self.db.get_flag('auto_probation')

        self._auto_probation = flag[1] if flag else False

        self._staff: dict[int, StaffRank] = {user_id: StaffRank[position] async for user_id, position in self.db.get_all_staff()}

        self._helpers: dict[int, str] = {user_id: console async for user_id, console in self.db.get_all_helpers()}

        self._nofilter_list: list[int] = [c async for c in self.db.get_all_nofilter_channels()]

        self._rules: dict[int, str] = {rule_id: description async for rule_id, description in self.db.get_rules()}

        self._watch_list: list[int] = [user_id async for user_id, watched in self.db.get_members() if watched is True]

    @property
    def staff(self) -> dict[int, StaffRank]:
        return self._staff

    @property
    def helpers(self) -> dict[int, str]:
        return self._helpers

    @property
    def auto_probation(self) -> bool:
        return self._auto_probation

    @property
    def nofilter_list(self) -> list[int]:
        return self._nofilter_list

    @property
    def rules(self) -> dict[int, str]:
        return self._rules

    @property
    def watch_list(self) -> list[int]:
        return self._watch_list

    # auto-probation
    async def set_auto_probation(self, status: bool):
        self._auto_probation = status
        await self.db.set_flag('auto_probation', status)

    def auto_probation_status(self):
        return self._auto_probation

    async def add_member(self, user_id: int):
        await self.db.add_member(user_id)

    async def set_watch(self, user_id: int, watched: bool):

        res = await self.db.set_watch(user_id, watched)
        if res:
            if watched:
                self._watch_list.append(user_id)
            else:
                self._watch_list.remove(user_id)

    # staff
    async def add_staff(self, user: 'Member | User | OptionalMember', level: str):
        if level not in self.bot.staff_roles:
            raise ValueError('not a staff level')
        if self._staff.get(user.id) is not None or self._helpers.get(user.id) is not None:
            res = await self.db.set_staff_level(user.id, level)
        else:
            res = await self.db.add_staff_member(user.id, level)
        if res:
            self._staff[user.id] = StaffRank[level]
        return res

    async def delete_staff(self, user: 'Member | User | OptionalMember'):

        if user.id in self._helpers:
            res = await self.db.remove_staff_position(user.id)
        else:
            res = await self.db.delete_staff(user.id)
        if res:
            del self._staff[user.id]
        return res

    async def add_helper(self, user: 'Member | User | OptionalMember', console: str):
        if console not in self.bot.helper_roles:
            raise ValueError('not a staff level')
        if self._staff.get(user.id) is not None or self._helpers.get(user.id) is not None:
            res = await self.db.set_helper_console(user.id, console)
        else:
            res = await self.db.add_helper(user.id, console)
        if res:
            if isinstance(user, Member):
                await user.add_roles(self.bot.roles['Helpers'])
            self._helpers[user.id] = console
        return res

    async def delete_helper(self, user: 'Member | User | OptionalMember'):

        if user.id in self._staff:
            res = await self.db.remove_helper_console(user.id)
        else:
            res = await self.db.delete_staff(user.id)
        if res:
            if isinstance(user, Member):
                await user.remove_roles(self.bot.roles['Helpers'])
            del self._helpers[user.id]
        return res

    async def update_staff_roles(self, member: Member):
        staff_role = self.bot.roles['Staff']
        all_roles = self.bot.staff_roles
        try:
            if member.id in self._staff:
                await member.remove_roles(*self.bot.staff_roles.values())
                await member.add_roles(staff_role, self.bot.staff_roles[self._staff[member.id].name])
            else:
                await member.remove_roles(staff_role, *all_roles.values())
        except discord.Forbidden:
            pass

    async def add_role(self, name: str, role: discord.Role):
        if await self.get_role(name):
            await self.db.update_role(name=name, role_id=role.id)
        else:
            await self.db.add_role(name=name, role_id=role.id)

    async def get_role(self, name: str) -> 'Optional[tuple[int, str]]':
        return await self.db.get_role(name)

    async def add_channel(self, name: str, channel: discord.TextChannel | discord.VoiceChannel | discord.Thread | discord.CategoryChannel):
        if await self.get_channel_by_name(name):
            return await self.db.update_channel(channel.id, name)
        else:
            return await self.db.add_channel(channel.id, name)

    async def get_channel_by_name(self, name: str):
        return await self.db.get_channel_by_name(name)

    async def get_channel(self, channel_id: int) -> 'Optional[DBChannel]':
        c = await self.db.get_channel(channel_id)
        if c:
            return DBChannel(id=c[0], name=c[1], filtered=c[2], lock_level=c[3], mod_channel=c[4])

    async def set_channel_lock_level(self, channel: discord.TextChannel | discord.Thread | discord.VoiceChannel, lock_level: int):
        await self.db.set_channel_lock_level(channel.id, lock_level)

    async def set_nofilter_channel(self, channel: discord.TextChannel | discord.Thread | discord.VoiceChannel, filtered: bool):
        db_channel = await self.get_channel(channel.id)
        res = None
        if not db_channel:
            res = await self.add_channel(channel.name, channel)
        if db_channel or res:
            res = await self.db.set_nofilter_channel(channel.id, filtered)
            if res:
                if filtered:
                    try:
                        self.nofilter_list.remove(channel.id)
                    except ValueError:
                        pass
                else:
                    self.nofilter_list.append(channel.id)
        return res

    async def add_changed_roles(self, roles: 'list[tuple[int, Optional[bool]]]', channel: discord.TextChannel | discord.Thread | discord.VoiceChannel):
        await self.db.add_changed_roles(roles, channel.id)

    async def delete_changed_role(self, role: discord.Role, channel: discord.TextChannel | discord.Thread | discord.VoiceChannel):
        await self.db.delete_changed_role(role.id, channel.id)

    async def get_changed_roles(self, channel: discord.TextChannel | discord.VoiceChannel) -> 'AsyncGenerator[ChangedRole, None]':
        async for cr in self.db.get_changed_roles(channel.id):
            yield cr

    async def clear_changed_roles(self, channel: discord.TextChannel | discord.VoiceChannel):
        await self.db.clear_changed_roles(channel.id)

    async def add_flag(self, name: str, value: bool):
        if await self.get_flag(name):
            await self.db.set_flag(name, value)
        else:
            await self.db.add_flag(name, value)

    async def get_flag(self, name: str):
        return await self.db.get_flag(name)

    async def delete_flag(self, name: str):
        return await self.db.delete_flag(name)

    async def add_rule(self, rule_id, content: str):
        await self.db.add_rule(rule_id, content)
        self._rules[rule_id] = content

    async def edit_rule(self, rule_id: int, content: str):
        await self.db.edit_rule(rule_id, content)
        self._rules[rule_id] = content

    async def delete_rule(self, rule_id: int):
        await self.db.delete_rule(rule_id)
        del self._rules[rule_id]

    async def store_channel_overwrites(self, name: str, overwrites: dict[Role | Member | Object, PermissionOverwrite]):
        permission_dict = {}
        for discord_object, overwrite in overwrites.items():
            if isinstance(discord_object, (Member, User)):
                continue
            permission_dict[discord_object.id] = {}
            for permission, value in overwrite:
                permission_dict[discord_object.id][permission] = value
        return await self.db.store_channel_overwrites(name, permission_dict)

    async def get_channel_overwrites(self, name: str) -> 'Optional[dict[discord.Object, PermissionOverwrite]]':
        overwrites = await self.db.get_channel_overwrites(name)
        if overwrites is None:
            return overwrites
        f_overwrites = {}
        for id, overwrites in overwrites.items():
            f_overwrites[discord.Object(id=id, type=discord.Role)] = discord.PermissionOverwrite(**overwrites)
        return f_overwrites

    async def delete_channel_overwrites(self, name: str) -> int:
        return await self.db.delete_channel_overwrites(name)
