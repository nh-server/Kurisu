from __future__ import annotations

import discord

from discord.ext import commands
from typing import Union, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from kurisu import Kurisu


class KurisuContext(commands.Context):
    channel: Union[discord.TextChannel, discord.VoiceChannel, discord.Thread, discord.DMChannel]
    prefix: str
    command: commands.Command
    bot: Kurisu

    async def get_user(self, user_id: int) -> Optional[Union[discord.Member, discord.User]]:
        if self.guild and (user := self.guild.get_member(user_id)):
            return user
        else:
            try:
                return await self.bot.fetch_user(user_id)
            except discord.NotFound:
                return None


class GuildContext(KurisuContext):
    channel: Union[discord.TextChannel, discord.VoiceChannel, discord.Thread]
    author: discord.Member
    guild: discord.Guild
