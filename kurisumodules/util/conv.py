from typing import TYPE_CHECKING
from discord.ext.commands.converter import Converter, MemberConverter
from discord.ext.commands.errors import BadArgument

if TYPE_CHECKING:
    from typing import Optional, Tuple, Union
    from discord import Member
    from discord.ext.commands import Context


class MemberOrID(Converter):
    async def convert(self, ctx: 'Context', argument: str) -> 'Tuple[int, Optional[Member]]':
        member: Member = None
        try:
            member = await MemberConverter().convert(ctx, argument)
            member_id: int = member.id
        except BadArgument:
            try:
                member_id = int(argument)
            except ValueError:
                raise BadArgument(f"Couldn't convert {argument!r} into a Member or int")

        return member_id, member

    # for the purpose of type hints, don't mind me :eyes:
    @staticmethod
    def __getitem__(item: int) -> 'Union[int, Optional[Member]]':
        pass
