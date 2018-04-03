from typing import TYPE_CHECKING, NamedTuple
from discord.ext.commands.converter import Converter, MemberConverter
from discord.ext.commands.errors import BadArgument

if TYPE_CHECKING:
    from typing import Optional, Tuple, Union
    from discord import Member
    from discord.ext.commands import Context


class OptionalMember(NamedTuple):
    id: int
    member: 'Optional[Member]'

    @property
    def display_if_exist(self) -> str:
        if self.member is None:
            return str(self.id)
        return str(self.member)


class MemberOrID(Converter):
    async def convert(self, ctx: 'Context', argument: str) -> 'OptionalMember':
        member: Member = None
        try:
            member = await MemberConverter().convert(ctx, argument)
            member_id: int = member.id
        except BadArgument:
            try:
                member_id = int(argument)
            except ValueError:
                raise BadArgument(f"Couldn't convert {argument!r} into a Member or int")

        return OptionalMember(member_id, member)

    # for the purpose of type hints, don't mind me :eyes:
    id: int
    member: 'Optional[Member]'

    @property
    def display_if_exist(self) -> str:
        raise RuntimeError('called wrong display method')
