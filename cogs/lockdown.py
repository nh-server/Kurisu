from __future__ import annotations

import discord

from discord.ext import commands
from typing import TYPE_CHECKING, Optional, Union
from utils.checks import is_staff, check_staff

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
        self.configuration = self.bot.configuration
        self.locking_down = False

    async def cog_check(self, ctx: KurisuContext):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        return True

    async def lockdown_channels(self, ctx: GuildContext, *, channels: list[Union[discord.TextChannel, discord.VoiceChannel]], top_role: discord.Role,
                                level: int, message: Optional[str] = None) -> list[discord.TextChannel]:

        locked_down = []
        to_add = []

        reason = f"Level {level} lockdown"

        for c in channels:

            db_channel = await self.configuration.get_channel(c.id)

            if not db_channel:
                await self.configuration.add_channel(c.name, c)
                db_channel = await self.configuration.get_channel(c.id)

            if db_channel and db_channel.lock_level > 0:
                await ctx.send(f"🔒 {c.mention} is already locked down. Use `.unlock` to unlock.")
                continue

            channel_overwrites = c.overwrites

            for target, overwrites in channel_overwrites.items():

                # Bot roles and member overwrites are spared
                if isinstance(target, discord.Object) or isinstance(target, discord.Member) or target.is_bot_managed():
                    continue

                # Only change the send_messages permission for roles that have it set to True and a lower in hierarchy
                # or is the everyone role
                if target is ctx.guild.default_role and overwrites.send_messages is not False \
                        or target < top_role and overwrites.send_messages is True:
                    value = overwrites.send_messages
                    channel_overwrites[target].send_messages = False
                    to_add.append((target.id, value))

            if not to_add:
                await ctx.send(f"No changes done to {c.mention}")
                continue

            try:
                await c.edit(overwrites=channel_overwrites, reason=reason)
            except discord.Forbidden:
                await ctx.send(f"Failed to lock down {c}")
                continue

            await self.configuration.add_changed_roles(to_add, c)
            await self.configuration.set_channel_lock_level(c, lock_level=level)
            locked_down.append(c)

            if message:
                await c.send(message)

        return locked_down

    @is_staff("HalfOP")
    @commands.command(aliases=['lock'])
    async def lockdown(self, ctx: GuildContext, channels: commands.Greedy[Union[discord.TextChannel, discord.VoiceChannel]]):
        """Lock message sending in the channel. Staff only."""

        if self.locking_down:
            return await ctx.send("The bot is already locking down channels.")

        self.locking_down = True

        author = ctx.author

        if not channels:
            if isinstance(ctx.channel, discord.Thread):
                return await ctx.send("You can't lock a thread.")
            else:
                channels.append(ctx.channel)

        locked_down = await self.lockdown_channels(ctx, channels=channels, level=2, top_role=self.bot.roles['Staff'],
                                                   message="🔒 Channel locked down. Only staff members may speak."
                                                           " Do not bring the topic to other channels or risk disciplinary actions.")
        self.locking_down = False

        if locked_down:
            msg = f"🔒 **Lockdown**: {ctx.author.mention} locked down channels | {author}\n📝 __Channels__: {', '.join(c.mention for c in locked_down)}"
            await self.bot.channels['mod-logs'].send(msg)

    @is_staff("Owner")
    @commands.command(aliases=['slock'])
    async def slockdown(self, ctx: GuildContext, channels: commands.Greedy[Union[discord.TextChannel, discord.VoiceChannel]]):
        """Lock message sending in the channel for everyone. Owners only."""

        if self.locking_down:
            return await ctx.send("The bot is already locking down channels.")

        self.locking_down = True

        author = ctx.author

        if not channels:
            if isinstance(ctx.channel, discord.Thread):
                return await ctx.send("You can't lock a thread.")
            else:
                channels.append(ctx.channel)

        locked_down = await self.lockdown_channels(ctx, channels=channels, level=3, top_role=self.bot.roles['Owner'],
                                                   message="🔒 Channel locked down. Only the server Owners may speak."
                                                           " Do not bring the topic to other channels or risk disciplinary actions.")
        self.locking_down = False

        if locked_down:
            msg = f"🔒 **Lockdown**: {ctx.author.mention} locked down channels | {author}\n📝 __Channels__: {', '.join(c.mention for c in locked_down)}"
            await self.bot.channels['mod-logs'].send(msg)

    @is_staff('Helper')
    @commands.command()
    async def softlock(self, ctx: GuildContext, channels: commands.Greedy[Union[discord.TextChannel, discord.VoiceChannel]]):
        """Lock message sending in the channel, without the "disciplinary action" note. Staff and Helpers only."""

        if self.locking_down:
            return await ctx.send("The bot is already locking down channels.")

        self.locking_down = True

        author = ctx.author

        if not channels:
            if isinstance(ctx.channel, discord.Thread):
                return await ctx.send("You can't lock a thread.")
            else:
                channels.append(ctx.channel)

        is_helper = not check_staff(self.bot, 'HalfOP', author.id)

        if is_helper and any(c not in self.bot.assistance_channels for c in channels):
            return await ctx.send("You can only lock assistance channels.")

        role = self.bot.roles['Helpers'] if is_helper else self.bot.roles['Staff']

        locked_down = await self.lockdown_channels(ctx, channels=channels, level=1, top_role=role)
        self.locking_down = False

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

        is_helper = not check_staff(self.bot, "HalfOP", author.id)

        if is_helper and any(c not in self.bot.assistance_channels for c in channels):
            return await ctx.send("You can only unlock assistance channels.")

        unlocked = []

        for c in channels:

            db_channel = await self.configuration.get_channel(c.id)

            if not db_channel or db_channel.lock_level == 0:
                await ctx.send(f"{c.mention} is not locked.")
                continue
            elif db_channel.lock_level == 3 and not check_staff(self.bot, "Owner", author.id):
                await ctx.send(f"{c.mention} can only be unlocked by a Owner.")
                continue

            channel_overwrites = c.overwrites

            async for changed_role in self.configuration.get_changed_roles(c):
                role = ctx.guild.get_role(changed_role.role_id)
                if not role:
                    continue
                channel_overwrites[role].send_messages = changed_role.original_value
            try:
                await c.edit(overwrites=channel_overwrites, reason="Unlock")
            except discord.Forbidden:
                await ctx.send(f"Failed to unlock {c}")
                continue

            await self.configuration.clear_changed_roles(c)
            await c.send("🔓 Channel unlocked.")
            await self.configuration.set_channel_lock_level(c, lock_level=0)
            unlocked.append(c)

        if unlocked:
            msg = f"🔓 **Unlock**: {ctx.author.mention} unlocked channels | {author}\n📝 __Channels__: {', '.join(c.mention for c in unlocked)}"
            await self.bot.channels['mod-logs'].send(msg)


async def setup(bot):
    await bot.add_cog(Lockdown(bot))
