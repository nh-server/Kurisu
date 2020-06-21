import discord
import time
import typing
import datetime

from utils.converters import SafeMember, FetchMember
from utils import utils
from utils.checks import is_staff, check_bot_or_staff
from utils.database import DatabaseCog
from discord.ext import commands


class KickBan(DatabaseCog):
    """
    Kicking and banning users.
    """

    async def cog_check(self, ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        return True

    async def meme(self, beaner: discord.Member, beaned: discord.Member, action: str, channel: discord.TextChannel, reason: str):
        await channel.send(f"Seriously? What makes you think it's okay to try and {action} another staff or helper like that?")
        msg = f"{beaner.mention} attempted to {action} {beaned.mention}|{beaned} in {channel.mention} "
        if reason != "":
            msg += "for the reason " + reason
        await self.bot.channels['meta'].send(msg + (" without a reason" if reason == "" else ""))

    @is_staff("HalfOP")
    @commands.bot_has_permissions(kick_members=True)
    @commands.command(name="kick")
    async def kick_member(self, ctx, member: SafeMember, *, reason=""):
        """Kicks a user from the server. Staff only."""
        if await check_bot_or_staff(ctx, member, "kick"):
            return
        msg = f"You were kicked from {ctx.guild.name}."
        if reason != "":
            msg += " The given reason is: " + reason
        msg += "\n\nYou are able to rejoin the server, but please read the rules in #welcome-and-rules before participating again."
        await utils.send_dm_message(member, msg)
        try:
            self.bot.actions.append("uk:" + str(member.id))
            await member.kick(reason=reason)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
            return
        await ctx.safe_send(f"{member} is now gone. 👌")
        msg = f"👢 **Kick**: {ctx.author.mention} kicked {member.mention} | {self.bot.escape_text(member)}\n🏷 __User ID__: {member.id}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + self.bot.escape_text(reason)
        await self.bot.channels['server-logs'].send(msg)
        signature = utils.command_signature(ctx.command)
        await self.bot.channels['mod-logs'].send(msg + (f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user." if reason == "" else ""))

    @is_staff("OP")
    @commands.bot_has_permissions(ban_members=True)
    @commands.command(name="ban", aliases=["yeet", "banid"])
    async def ban_member(self, ctx, member: FetchMember, days: typing.Optional[int] = 0, *, reason=""):
        """Bans a user from the server. OP+ only. Optional: [days] Specify up to 7 days of messages to delete."""
        if await check_bot_or_staff(ctx, member, "ban"):
            return
        if days > 7:
            days = 7
        elif days < 0:
            days = 0
        if isinstance(member, discord.Member):
            msg = f"You were banned from {ctx.guild.name}."
            if reason != "":
                msg += " The given reason is: " + reason
            msg += "\n\nThis ban does not expire."
            await utils.send_dm_message(member, msg)
        try:
            await ctx.cog.remove_timed_restriction(member.id, 'timeban')
            self.bot.actions.append("ub:" + str(member.id))
            await ctx.guild.ban(member, reason=reason, delete_message_days=days)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
            return
        await ctx.safe_send(f"{member} is now b&. 👍")
        msg = f"⛔ **Ban**: {ctx.author.mention} banned {member.mention} | {self.bot.escape_text(member)}\n🏷 __User ID__: {member.id}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + self.bot.escape_text(reason)
        await self.bot.channels['server-logs'].send(msg)
        signature = utils.command_signature(ctx.command)
        await self.bot.channels['mod-logs'].send(msg + (f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user." if reason == "" else ""))

    @is_staff("OP")
    @commands.bot_has_permissions(ban_members=True)
    @commands.command(name="silentban", aliases=["quietyeet"])
    async def silentban_member(self, ctx, member: SafeMember, days: typing.Optional[int] = 0, *, reason=""):
        """Bans a user from the server, without a notification. OP+ only.  Optional: [days] Specify up to 7 days of messages to delete."""
        if await check_bot_or_staff(ctx, member, "ban"):
            return
        if days > 7:
            days = 7
        elif days < 0:
            days = 0
        try:
            self.bot.actions.append("ub:" + str(member.id))
            await ctx.cog.remove_timed_restriction(member.id, 'timeban')
            await member.ban(reason=reason, delete_message_days=days)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
            return
        await ctx.safe_send(f"{member} is now b&. 👍")
        reason = self.bot.escape_text(reason)
        msg = f"⛔ **Silent ban**: {ctx.author.mention} banned {member.mention} | {self.bot.escape_text(member)}\n"\
              f"🏷 __User ID__: {member.id}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + self.bot.escape_text(reason)
        await self.bot.channels['server-logs'].send(msg)
        signature = utils.command_signature(ctx.command)
        await self.bot.channels['mod-logs'].send(msg + (f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}`." if reason == "" else ""))

    @is_staff("OP")
    @commands.bot_has_permissions(ban_members=True)
    @commands.command(name="timeban", aliases=["timeyeet"])
    async def timeban_member(self, ctx, member: FetchMember, length, *, reason=""):
        """Bans a user for a limited period of time. OP+ only.\n\nLength format: #d#h#m#s"""
        if await check_bot_or_staff(ctx, member, "timeban"):
            return

        if (seconds := utils.parse_time(length)) == -1:
            return await ctx.send("💢 I don't understand your time format.")

        timestamp = datetime.datetime.now()
        delta = datetime.timedelta(seconds=seconds)
        unban_time = timestamp + delta
        unban_time_string = unban_time.strftime("%Y-%m-%d %H:%M:%S")

        if isinstance(member, discord.Member):
            msg = f"You were banned from {ctx.guild.name}."
            if reason != "":
                msg += " The given reason is: " + reason
            msg += f"\n\nThis ban expires {unban_time_string} {time.tzname[0]}."
            await utils.send_dm_message(member, msg)
        try:
            self.bot.actions.append("ub:" + str(member.id))
            await ctx.guild.ban(member, reason=reason, delete_message_days=0)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
            return
        await self.add_timed_restriction(member.id, unban_time_string, 'timeban')
        await ctx.safe_send(f"{member} is now b& until {unban_time_string} {time.tzname[0]}. 👍")
        msg = f"⛔ **Time ban**: {ctx.author.mention} banned {member.mention} until {unban_time_string} | {member}\n🏷 __User ID__: {member.id}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + self.bot.escape_text(reason)
        await self.bot.channels['server-logs'].send(msg)
        signature = utils.command_signature(ctx.command)
        await self.bot.channels['mod-logs'].send(msg + (f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user." if reason == "" else ""))

    @is_staff("OP")
    @commands.bot_has_permissions(kick_members=True)
    @commands.command(name="softban", aliases=["gentleyeet"])
    async def softban_member(self, ctx, member: FetchMember, *, reason):
        """Soft-ban a user. OP+ only.

        This "bans" the user without actually doing a ban on Discord. The bot will instead kick the user every time they join. Discord bans are account- and IP-based."""
        if await check_bot_or_staff(ctx, member, "softban"):
            return
        if isinstance(member, discord.Member):
            msg = f"This account is no longer permitted to participate in {ctx.guild.name}. The reason is: {reason}"
            await utils.send_dm_message(member, msg)
            try:
                await member.kick(reason=reason)
            except discord.errors.Forbidden:
                await ctx.send("💢 I don't have permission to do this.")
                return
        await ctx.safe_send(f"{member} is now b&. 👍")
        msg = f"⛔ **Soft-ban**: {ctx.author.mention} soft-banned {member.mention} | {self.bot.escape_text(member)}\n🏷 __User ID__: {member.id}\n✏️ __Reason__: {reason}"
        await self.bot.channels['mod-logs'].send(msg)
        await self.bot.channels['server-logs'].send(msg)

    @is_staff("OP")
    @commands.command(name="unsoftban")
    async def unsoftban_member(self, ctx, user: FetchMember):
        """Un-soft-ban a user based on ID. OP+ only."""
        await self.remove_softban(user.id)
        await ctx.safe_send(f"{user} has been unbanned!")
        msg = f"⚠️ **Un-soft-ban**: {ctx.author.mention} un-soft-banned {self.bot.escape_text(user)}"
        await self.bot.channels['mod-logs'].send(msg)


def setup(bot):
    bot.add_cog(KickBan(bot))
