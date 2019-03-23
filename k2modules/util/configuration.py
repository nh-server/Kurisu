from typing import TYPE_CHECKING

from k2modules.data.names import staff_roles
from .managerbase import BaseManager
from .database import ConfigurationDatabaseManager

if TYPE_CHECKING:
    from typing import Dict, Set, Union
    from discord import Member, User
    from kurisu2 import Kurisu2
    from . import OptionalMember


class ConfigurationManager(BaseManager, db_manager=ConfigurationDatabaseManager):
    """Manages bot configuration."""

    db: ConfigurationDatabaseManager

    _auto_probation = False
    _staff: 'Dict[int, str]'
    _nofilter_list: 'Set[int]'

    def __init__(self, bot: 'Kurisu2'):
        super().__init__(bot)

    async def load(self):
        a = self.db.get_all_flags()
        async for k, v in a:
            if k == 'auto_probation':
                self._auto_probation = v

        self._staff = (await self.db.get_all_staff_levels())

        self._nofilter_list = set(await self.db.get_all_nofilter_channels())

    # auto-probation
    def set_auto_probation(self, status: bool):
        self._auto_probation = status
        self.db.set_flag('auto_probation', status)

    def get_auto_probation(self):
        return self._auto_probation

    # staff
    def add_staff(self, user: 'Union[Member, User, OptionalMember]', level: str):
        level = level.lower()
        if level not in staff_roles:
            raise ValueError('not a staff level')
        self._staff[user.id] = level
        self.db.set_staff_level(user.id, level)

    def delete_staff(self, user: 'Union[Member, User, OptionalMember]'):
        del self._staff[user.id]
        self.db.delete_staff(user.id)

    async def update_staff_roles(self, member: 'Member'):
        staff_role = await self.bot.get_role_by_name('staff-role')
        all_roles = {x: await self.bot.get_role_by_name(y) for x, y in staff_roles.items()}
        if member.id in self._staff:
            await member.remove_roles(*all_roles.values())
            await member.add_roles(staff_role, all_roles[self._staff[member.id]])
        else:
            await member.remove_roles(staff_role, *all_roles.values())
