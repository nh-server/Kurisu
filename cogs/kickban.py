from __future__ import annotations

import discord
import datetime

from discord import app_commands
from discord.ext import commands
from discord.utils import format_dt
from typing import Union, Literal, TYPE_CHECKING, Optional
from utils.converters import TimeTransformer, DateOrTimeToSecondsConverter
from utils.checks import is_staff, is_staff_app, check_bot_or_staff
from utils.utils import send_dm_message
from utils import Restriction
from utils.database import FilterKind

if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.context import KurisuContext, GuildContext


class KickBan(commands.Cog):
    """
    Kicking and banning users.
    """

    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.emoji = discord.PartialEmoji.from_str('🚷')
        self.restrictions = bot.restrictions
        self.filters = bot.filters
        self.logs = bot.logs

    async def cog_check(self, ctx: KurisuContext):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        return True

    async def meme(self, beaner: discord.Member, beaned: discord.Member, action: str, channel: discord.TextChannel, reason: Optional[str] = None):
        await channel.send(f"Seriously? What makes you think it's okay to try and {action} another staff or helper like that?")
        msg = f"{beaner.mention} attempted to {action} {beaned.mention}|{beaned} in {channel.mention} "
        if reason:
            msg += f"for the reason {reason}"
        else:
            msg += " without a reason"
        await self.bot.channels['meta'].send(msg)

    @is_staff("HalfOP")
    @commands.bot_has_permissions(kick_members=True)
    @commands.command(name="kick")
    async def kick_member(self, ctx: GuildContext, member: discord.Member, *, reason: Optional[str] = None):
        """Kicks a user from the server. Staff only."""
        if await check_bot_or_staff(ctx, member, "kick"):
            return
        msg = f"You were kicked from {ctx.guild.name}."
        if reason:
            msg += " The given reason is: " + reason
        msg += "\n\nYou are able to rejoin the server, but please read the rules in #welcome-and-rules before participating again."
        await send_dm_message(member, msg, ctx)
        try:
            self.bot.actions.append("uk:" + str(member.id))
            await member.kick(reason=reason)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
            return
        await ctx.send(f"{member} is now gone. 👌")
        await self.bot.logs.post_action_log(ctx.author, member, 'kick', reason=reason)

    @is_staff("OP")
    @commands.bot_has_permissions(ban_members=True)
    @commands.command(name="ban", aliases=["yeet"])
    async def ban_member(self, ctx: GuildContext, member: Union[discord.Member, discord.User], days: Optional[Literal[0, 1, 2, 3, 4, 5, 6, 7]] = 0, *, reason: Optional[str] = None):
        """Bans a user from the server. OP+ only. Optional: [days] Specify up to 7 days of messages to delete."""
        if await check_bot_or_staff(ctx, member, "ban"):
            return

        if isinstance(member, discord.Member):
            msg = f"You were banned from {ctx.guild.name}."
            if reason:
                msg += " The given reason is: " + reason
            msg += "\n\nThis ban does not expire."
            await send_dm_message(member, msg, ctx)

        try:
            self.bot.actions.append("ub:" + str(member.id))
            await ctx.guild.ban(member, reason=reason, delete_message_days=days)  # type: ignore
        except discord.errors.Forbidden:
            await ctx.send("Failed to ban member.")
            return

        # Remove any timeban
        await self.restrictions.remove_restriction(member, Restriction.Ban)

        await ctx.send(f"{member} is now b&. 👍")
        await self.bot.logs.post_action_log(ctx.author, member, 'ban', reason=reason)

    @is_staff_app("OP")
    @app_commands.default_permissions(ban_members=True)
    @app_commands.guild_only()
    @app_commands.command(name='ban')
    async def ban_member_slash(self,
                               interaction: discord.Interaction,
                               member: discord.Member,
                               reason: Optional[str] = None,
                               delete_messages: app_commands.Range[int, 0, 7] = 0,
                               duration: app_commands.Transform[Optional[int], TimeTransformer] = None):
        """Bans a user from the server. OP+ only.

        Args:
            member: Member to ban.
            reason: Reason for the ban.
            delete_messages: Number of days to delete messages. Max 7 days.
            duration: This will convert the ban to a time ban. Length format: #d#h#m#s."""

        assert interaction.guild is not None

        if await check_bot_or_staff(interaction, member, "ban"):
            return

        msg = f"You were banned from {interaction.guild.name}."
        if reason:
            msg += " The given reason is: " + reason

        if duration is not None:
            timestamp = datetime.datetime.now(self.bot.tz)
            delta = datetime.timedelta(seconds=duration)
            unban_time = timestamp + delta
            unban_time_string = format_dt(unban_time)

            try:
                self.bot.actions.append("ub:" + str(member.id))
                await interaction.guild.ban(member, reason=reason, delete_message_days=delete_messages)
            except discord.errors.Forbidden:
                await interaction.response.send_message("Failed to ban member.")
                return

            await self.restrictions.add_restriction(member, Restriction.Ban, reason, end_date=unban_time)
            msg += f"\n\nThis ban expires in {unban_time_string}."
            msg_send = await send_dm_message(member, msg)
            await interaction.response.send_message(f"{member} is now b& until {unban_time_string}. 👍" + ("\nFailed to send DM message" if not msg_send else ""))
        else:
            unban_time = None
            try:
                self.bot.actions.append("ub:" + str(member.id))
                await interaction.guild.ban(member, reason=reason, delete_message_days=delete_messages)
            except discord.errors.Forbidden:
                await interaction.response.send_message("Failed to ban member.")
                return

            await self.restrictions.remove_restriction(member, Restriction.Ban)
            msg += "\n\nThis ban does not expire."
            msg_send = await send_dm_message(member, msg)
            await interaction.response.send_message(f"{member} is now b&. 👍" + ("\nFailed to send DM message" if not msg_send else ""))
        await self.bot.logs.post_action_log(interaction.user, member, 'ban', reason=reason, until=unban_time)

    @is_staff("OP")
    @commands.bot_has_permissions(ban_members=True)
    @commands.command(name="superban", aliases=["superyeet"])
    async def superban(self, ctx: GuildContext, member: Union[discord.Member, discord.User], days: Optional[Literal[0, 1, 2, 3, 4, 5, 6, 7]] = 0, *, reason: Optional[str] = None):
        """Bans a user from the server. OP+ only. Optional: [days] Specify up to 7 days of messages to delete."""
        if await check_bot_or_staff(ctx, member, "ban"):
            return

        if isinstance(member, discord.Member):
            msg = f"You were superbanned from {ctx.guild.name}."
            if reason:
                msg += " The given reason is: " + reason
            msg += "\n\nThis ban does not expire.\n\nhttps://nintendohomebrew.com/assets/img/banned.gif"
            await send_dm_message(member, msg, ctx)
        try:
            self.bot.actions.append("ub:" + str(member.id))
            await ctx.guild.ban(member, reason=reason, delete_message_days=days)  # type: ignore
        except discord.errors.Forbidden:
            await ctx.send("Failed to ban member.")
            return
        await self.restrictions.remove_restriction(member, Restriction.Ban)
        await ctx.send(f"{member} is now SUPER BANNED. 👍 https://nintendohomebrew.com/assets/img/banned.gif")
        await self.bot.logs.post_action_log(ctx.author, member, 'ban', reason=reason)

    @commands.bot_has_permissions(ban_members=True)
    @commands.command(name="unban", aliases=["unyeet"])
    async def unban_member(self, ctx: GuildContext, user: Union[discord.Member, discord.User], *, reason: Optional[str] = None):
        """Unbans a user from the server. OP+ only."""
        try:
            await ctx.guild.fetch_ban(user)
        except discord.errors.NotFound:
            return await ctx.send(f"{user} is not banned!")

        await self.restrictions.remove_restriction(user, Restriction.Ban)
        self.bot.actions.append(f'bu:{user.id}')
        await ctx.guild.unban(user, reason=reason)
        await ctx.send(f"{user} is now unbanned.")
        await self.bot.logs.post_action_log(ctx.author, user, 'unban', reason=reason)

    @is_staff("OP")
    @commands.bot_has_permissions(ban_members=True)
    @commands.command(name="silentban", aliases=["quietyeet"])
    async def silentban_member(self, ctx: GuildContext, member: discord.Member, days: Optional[Literal[0, 1, 2, 3, 4, 5, 6, 7]] = 0, *, reason: Optional[str] = None):
        """Bans a user from the server, without a notification. OP+ only.  Optional: [days] Specify up to 7 days of messages to delete."""
        if await check_bot_or_staff(ctx, member, "ban"):
            return

        try:
            self.bot.actions.append("ub:" + str(member.id))
            await member.ban(reason=reason, delete_message_days=days)  # type: ignore
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
            return

        await self.restrictions.remove_restriction(member, Restriction.Ban)
        await ctx.send(f"{member} is now b&. 👍")
        await self.bot.logs.post_action_log(ctx.author, member, 'silentban', reason=reason)

    @is_staff("OP")
    @commands.bot_has_permissions(ban_members=True)
    @commands.command(name="timeban", aliases=["timeyeet"])
    async def timeban_member(self, ctx: GuildContext, member: Union[discord.Member, discord.User], length: int = commands.parameter(converter=DateOrTimeToSecondsConverter), *, reason: Optional[str] = None):
        """Bans a user for a limited period of time. OP+ only.\n\nLength format: #d#h#m#s"""
        if await check_bot_or_staff(ctx, member, "timeban"):
            return

        timestamp = datetime.datetime.now(self.bot.tz)
        delta = datetime.timedelta(seconds=length)
        unban_time = timestamp + delta
        unban_time_string = format_dt(unban_time)

        await self.restrictions.add_restriction(member, Restriction.Ban, reason, end_date=unban_time)

        if isinstance(member, discord.Member):
            msg = f"You were banned from {ctx.guild.name}."
            if reason:
                msg += " The given reason is: " + reason
            msg += f"\n\nThis ban lasts until {unban_time_string}."
            await send_dm_message(member, msg, ctx)
        try:
            self.bot.actions.append("ub:" + str(member.id))
            await ctx.guild.ban(member, reason=reason, delete_message_days=0)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
            return

        await ctx.send(f"{member} is now b& until {unban_time_string}. 👍")
        await self.bot.logs.post_action_log(ctx.author, member, 'timeban', reason=reason, until=unban_time)

    @is_staff("OP")
    @commands.bot_has_permissions(kick_members=True)
    @commands.command(name="softban", aliases=["gentleyeet"])
    async def softban_member(self, ctx: GuildContext, member: Union[discord.Member, discord.User], *, reason: str):
        """Soft-ban a user. OP+ only.

        This "bans" the user without actually doing a ban on Discord.
        The bot will instead kick the user every time they join.
        Discord bans are account- and IP-based."""
        if await check_bot_or_staff(ctx, member, "softban"):
            return

        if member.id in self.restrictions.softbans:
            return await ctx.send("This user is already softbanned!")

        await self.restrictions.add_softban(member, ctx.author, reason)

        await ctx.send(f"{member} is now b&. 👍")
        await self.bot.logs.post_action_log(ctx.author, member, 'softban', reason=reason)

    @is_staff("OP")
    @commands.command(name="unsoftban")
    async def unsoftban_member(self, ctx: GuildContext, user: Union[discord.Member, discord.User]):
        """Un-soft-ban a user based on ID. OP+ only."""
        if user.id not in self.restrictions.softbans:
            return await ctx.send("This user is not softbanned!")
        await self.restrictions.delete_softban(user)
        await ctx.send(f"{user} has been unbanned!")
        msg = f"⚠️ **Un-soft-ban**: {ctx.author.mention} un-soft-banned {self.bot.escape_text(user)}"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("OP")
    @commands.command(name="scamban")
    async def scamban_member(self, ctx: GuildContext, member: discord.Member, site: str):
        """Bans member deleting message from last day and add a scamming site to the filter"""

        site = site.lower()

        if await check_bot_or_staff(ctx, member, "scamban"):
            return

        if discord.utils.get(self.filters.filtered_words, word=site):
            await ctx.send("Site is already in the filter!")
        elif ' ' in site or '-' in site:
            await ctx.send("Filtered words can't contain dashes or spaces, please add the site properly with wordfilter command.")
        else:
            await self.filters.add_filtered_word(site, FilterKind.ScammingSite)
            await self.bot.channels['mod-logs'].send(f"🆕 **Added**: {ctx.author.mention} added `{site}` to the word filter!")
        ban_msg = ("You have been banned from Nintendo Homebrew for linking scamming sites in the server."
                   "If you think this is a mistake contact ❅FrozenFire❆#0700 on discord or send a email to staff@nintendohomebrew.com")
        await send_dm_message(member, ban_msg)
        reason = "Linking scamming site"
        await member.ban(reason=reason, delete_message_days=1)
        await ctx.send(f"{member} is now b&. 👍")
        await self.bot.logs.post_action_log(ctx.author, member, 'ban', reason=reason)


async def setup(bot):
    await bot.add_cog(KickBan(bot))
