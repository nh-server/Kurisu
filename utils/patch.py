# Patched discord.py methods for monkey patching

import discord
import re

from discord.ext import commands
from discord.ext.commands import MemberNotFound, UserNotFound
from discord.ext.commands._types import BotT
from discord.ext.commands.converter import _get_from_guilds, _utils_get


async def patched_member_convert(self, ctx: commands.Context[BotT], argument: str) -> discord.Member:
    bot = ctx.bot
    match = self._get_id_match(argument) or re.match(r'<@!?([0-9]{15,20})>$', argument)
    guild = ctx.guild
    if match is None:
        raise MemberNotFound(argument)
    else:
        user_id = int(match.group(1))
        if guild:
            result = guild.get_member(user_id) or _utils_get(ctx.message.mentions, id=user_id)
        else:
            result = _get_from_guilds(bot, 'get_member', user_id)

    if not isinstance(result, discord.Member):
        if guild is None:
            raise MemberNotFound(argument)

        if user_id is not None:
            result = await self.query_member_by_id(bot, guild, user_id)

        if not result:
            raise MemberNotFound(argument)

    return result


async def patched_user_convert(self, ctx: commands.Context[BotT], argument: str) -> discord.User:
    match = self._get_id_match(argument) or re.match(r'<@!?([0-9]{15,20})>$', argument)

    if match is not None:
        user_id = int(match.group(1))
        result = ctx.bot.get_user(user_id) or _utils_get(ctx.message.mentions, id=user_id)
        if result is None:
            try:
                result = await ctx.bot.fetch_user(user_id)
            except discord.HTTPException:
                raise UserNotFound(argument) from None

        return result  # type: ignore
    raise UserNotFound(argument)
