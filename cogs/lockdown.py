from __future__ import annotations

import discord

from discord.ext import commands
from typing import TYPE_CHECKING, Optional, Union
from utils import crud
from utils.checks import is_staff, check_staff_id

if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.context import KurisuContext, GuildContext


class Lockdown(commands.Cog):
    """
    Channel lockdown commands.
    """
    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.emoji = discord.PartialEmoji.from_str('🔒')

    async def cog_check(self, ctx: KurisuContext):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        return True

    async def lockdown_channels(self, ctx: GuildContext, *, channels: list[Union[discord.TextChannel, discord.VoiceChannel]], top_role: discord.Role,
                                level: int, message: Optional[str] = None) -> list[discord.TextChannel]:

        locked_down = []
        to_add = []

        for c in channels:

            db_channel = await crud.get_dbchannel(c.id)

            if not db_channel:
                db_channel = await crud.add_dbchannel(c.id, c.name)

            if db_channel.lock_level > 0:
                await ctx.send(f"🔒 {c.mention} is already locked down. Use `.unlock` to unlock.")
                continue

            overwrites_changed = False
            reason = f"Level {level} lockdown"
            for role in c.changed_roles:

                # Bots are spared
                if role.is_bot_managed():
                    continue

                if role.position < top_role.position:
                    overwrites = c.overwrites_for(role)
                    if overwrites.send_messages is not False:
                        value = overwrites.send_messages
                        overwrites.update(send_messages=False)
                        try:
                            await c.set_permissions(role, overwrite=overwrites, reason=reason)
                        except discord.Forbidden:
                            continue
                        to_add.append((role.id, value))
                        overwrites_changed = True

            if not overwrites_changed:
                await ctx.send(f"No changes done to {c.mention}")
                continue

            await crud.add_changed_roles(c.id, to_add)
            await db_channel.update(lock_level=level).apply()
            locked_down.append(c)

            if message:
                await c.send(message)

        return locked_down

    @is_staff("HalfOP")
    @commands.command(aliases=['lock'])
    async def lockdown(self, ctx: GuildContext, channels: commands.Greedy[Union[discord.TextChannel, discord.VoiceChannel]]):
        """Lock message sending in the channel. Staff only."""

        author = ctx.author

        if not channels:
            if isinstance(ctx.channel, discord.Thread):
                return await ctx.send("You can't lock a thread.")
            else:
                channels.append(ctx.channel)

        locked_down = await self.lockdown_channels(ctx, channels=channels, level=2, top_role=self.bot.roles['Staff'],
                                                   message="🔒 Channel locked down. Only staff members may speak."
                                                           " Do not bring the topic to other channels or risk disciplinary actions.")

        if locked_down:
            msg = f"🔒 **Lockdown**: {ctx.author.mention} locked down channels | {author}\n📝 __Channels__: {', '.join(c.mention for c in locked_down)}"
            await self.bot.channels['mod-logs'].send(msg)

    @is_staff("Owner")
    @commands.command(aliases=['slock'])
    async def slockdown(self, ctx: GuildContext, channels: commands.Greedy[Union[discord.TextChannel, discord.VoiceChannel]]):
        """Lock message sending in the channel for everyone. Owners only."""

        author = ctx.author

        if not channels:
            if isinstance(ctx.channel, discord.Thread):
                return await ctx.send("You can't lock a thread.")
            else:
                channels.append(ctx.channel)

        locked_down = await self.lockdown_channels(ctx, channels=channels, level=3, top_role=self.bot.roles['Owner'],
                                                   message="🔒 Channel locked down. Only the server Owners may speak."
                                                           " Do not bring the topic to other channels or risk disciplinary actions.")

        if locked_down:
            msg = f"🔒 **Lockdown**: {ctx.author.mention} locked down channels | {author}\n📝 __Channels__: {', '.join(c.mention for c in locked_down)}"
            await self.bot.channels['mod-logs'].send(msg)

    @is_staff('Helper')
    @commands.command()
    async def softlock(self, ctx: GuildContext, channels: commands.Greedy[Union[discord.TextChannel, discord.VoiceChannel]]):
        """Lock message sending in the channel, without the "disciplinary action" note. Staff and Helpers only."""

        author = ctx.author

        if not channels:
            if isinstance(ctx.channel, discord.Thread):
                return await ctx.send("You can't lock a thread.")
            else:
                channels.append(ctx.channel)

        is_helper = not await check_staff_id('HalfOP', author.id)

        if is_helper and any(c not in self.bot.assistance_channels for c in channels):
            return await ctx.send("You can only lock assistance channels.")

        role = self.bot.roles['Helpers'] if is_helper else self.bot.roles['Staff']

        locked_down = await self.lockdown_channels(ctx, channels=channels, level=1, top_role=role)

        if locked_down:
            msg = f"🔒 **Lockdown**: {ctx.author.mention} locked down channels | {author}\n📝 __Channels__: {', '.join(c.mention for c in locked_down)}"
            await self.bot.channels['mod-logs'].send(msg)

    @is_staff('Helper')
    @commands.command()
    async def unlock(self, ctx: GuildContext, channels: commands.Greedy[Union[discord.TextChannel, discord.VoiceChannel]]):
        """Unlock message sending in the channel. Staff only and Helpers only."""
        author = ctx.author

        if not channels:
            if isinstance(ctx.channel, discord.Thread):
                return await ctx.send("You can't unlock a thread.")
            else:
                channels.append(ctx.channel)

        is_helper = not await check_staff_id("HalfOP", author.id)

        if is_helper and any(c not in self.bot.assistance_channels for c in channels):
            return await ctx.send("You can only unlock assistance channels.")

        unlocked = []

        for c in channels:

            db_channel = await crud.get_dbchannel(c.id)

            if not db_channel or db_channel.lock_level == 0:
                await ctx.send(f"{c.mention} is not locked.")
                continue
            elif db_channel.lock_level == 3 and not await check_staff_id("Owner", author.id):
                await ctx.send(f"{c.mention} can only be unlocked by a Owner.")
                continue

            changed_roles = await crud.get_changed_roles(c.id)

            for changed_role in changed_roles:
                role_id = changed_role.role_id
                role = ctx.guild.get_role(role_id)
                if not role:
                    continue
                overwrites = c.overwrites_for(role)
                overwrites.update(send_messages=changed_role.original_value)
                try:
                    await c.set_permissions(role, overwrite=overwrites, reason="Unlock")
                except discord.Forbidden:
                    continue

            await crud.clear_changed_roles(c.id)
            await c.send("🔓 Channel unlocked.")
            await db_channel.update(lock_level=0).apply()
            unlocked.append(c)

        if unlocked:
            msg = f"🔓 **Unlock**: {ctx.author.mention} unlocked channels | {author}\n📝 __Channels__: {', '.join(c.mention for c in unlocked)}"
            await self.bot.channels['mod-logs'].send(msg)


async def setup(bot):
    await bot.add_cog(Lockdown(bot))
