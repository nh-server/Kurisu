import discord
import time
import datetime

from discord.ext import commands
from typing import Optional, Union
from utils import utils, crud
from utils.checks import is_staff, check_bot_or_staff


class KickBan(commands.Cog):
    """
    Kicking and banning users.
    """

    def __init__(self, bot):
        self.bot = bot

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
    async def kick_member(self, ctx, member: discord.Member, *, reason=""):
        """Kicks a user from the server. Staff only."""
        if await check_bot_or_staff(ctx, member, "kick"):
            return
        msg = f"You were kicked from {ctx.guild.name}."
        if reason != "":
            msg += " The given reason is: " + reason
        msg += "\n\nYou are able to rejoin the server, but please read the rules in #welcome-and-rules before participating again."
        await utils.send_dm_message(member, msg, ctx)
        try:
            self.bot.actions.append("uk:" + str(member.id))
            await member.kick(reason=reason)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
            return
        await ctx.send(f"{member} is now gone. 👌")
        msg = f"👢 **Kick**: {ctx.author.mention} kicked {member.mention} | {self.bot.escape_text(member)}\n🏷 __User ID__: {member.id}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.channels['server-logs'].send(msg)
        signature = utils.command_signature(ctx.command)
        await self.bot.channels['mod-logs'].send(msg + (f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user." if reason == "" else ""))

    @is_staff("OP")
    @commands.bot_has_permissions(ban_members=True)
    @commands.command(name="ban", aliases=["yeet"])
    async def ban_member(self, ctx, member: Union[discord.Member, discord.User], days: Optional[int] = 0, *, reason=""):
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
            await utils.send_dm_message(member, msg, ctx)
        try:
            await crud.remove_timed_restriction(member.id, 'timeban')
            self.bot.actions.append("ub:" + str(member.id))
            await ctx.guild.ban(member, reason=reason, delete_message_days=days)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
            return
        await ctx.send(f"{member} is now b&. 👍")
        msg = f"⛔ **Ban**: {ctx.author.mention} banned {member.mention} | {self.bot.escape_text(member)}\n🏷 __User ID__: {member.id}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.channels['server-logs'].send(msg)
        signature = utils.command_signature(ctx.command)
        await self.bot.channels['mod-logs'].send(msg + (f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user." if reason == "" else ""))

    @is_staff("OP")
    @commands.bot_has_permissions(ban_members=True)
    @commands.command(name="superban", aliases=["superyeet"])
    async def superban(self, ctx, member: Union[discord.Member, discord.User], days: Optional[int] = 0, *, reason=""):
        """Bans a user from the server. OP+ only. Optional: [days] Specify up to 7 days of messages to delete."""
        if await check_bot_or_staff(ctx, member, "ban"):
            return
        if days > 7:
            days = 7
        elif days < 0:
            days = 0
        if isinstance(member, discord.Member):
            msg = f"You were superbanned from {ctx.guild.name}."
            if reason != "":
                msg += " The given reason is: " + reason
            msg += "\n\nThis ban does not expire.\n\nhttps://nintendohomebrew.com/assets/img/banned.gif"
            await utils.send_dm_message(member, msg, ctx)
        try:
            await crud.remove_timed_restriction(member.id, 'timeban')
            self.bot.actions.append("ub:" + str(member.id))
            await ctx.guild.ban(member, reason=reason, delete_message_days=days)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
            return
        await ctx.send(f"{member} is now SUPER BANNED. 👍 https://nintendohomebrew.com/assets/img/banned.gif")
        msg = f"⛔ **Ban**: {ctx.author.mention} banned {member.mention} | {self.bot.escape_text(member)}\n🏷 __User ID__: {member.id}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.channels['server-logs'].send(msg)
        signature = utils.command_signature(ctx.command)
        await self.bot.channels['mod-logs'].send(msg + (f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user." if reason == "" else ""))

    @is_staff("OP")
    @commands.bot_has_permissions(ban_members=True)
    @commands.command(name="unban", aliases=["unyeet"])
    async def unban_member(self, ctx, user: Union[discord.Member, discord.User], *, reason=""):
        """Unbans a user from the server. OP+ only."""

        if reason == "":
            reason = "No reason provided."

        try:
            await ctx.guild.fetch_ban(user)
        except discord.errors.NotFound:
            return await ctx.send(f"{user} is not banned!")

        await crud.remove_timed_restriction(user.id, 'timeban')
        self.bot.actions.append("tbr:" + str(user.id))
        await ctx.guild.unban(user, reason=reason)
        await ctx.send(f"{user} is now unbanned.")
        msg = f"⚠ **Unban**: {ctx.author.mention} unbanned {user.mention} | {self.bot.escape_text(user)}\n🏷 __User ID__: {user.id}\n✏️ __Reason__: {reason}"
        await self.bot.channels['mod-logs'].send(msg)
        await self.bot.channels['server-logs'].send(msg)

    @is_staff("OP")
    @commands.bot_has_permissions(ban_members=True)
    @commands.command(name="silentban", aliases=["quietyeet"])
    async def silentban_member(self, ctx, member: discord.Member, days: Optional[int] = 0, *, reason=""):
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
        await ctx.send(f"{member} is now b&. 👍")
        msg = f"⛔ **Silent ban**: {ctx.author.mention} banned {member.mention} | {self.bot.escape_text(member)}\n"\
              f"🏷 __User ID__: {member.id}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.channels['server-logs'].send(msg)
        signature = utils.command_signature(ctx.command)
        await self.bot.channels['mod-logs'].send(msg + (f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}`." if reason == "" else ""))

    @is_staff("OP")
    @commands.bot_has_permissions(ban_members=True)
    @commands.command(name="timeban", aliases=["timeyeet"])
    async def timeban_member(self, ctx, member: Union[discord.Member, discord.User], length, *, reason=""):
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
            await utils.send_dm_message(member, msg, ctx)
        try:
            self.bot.actions.append("ub:" + str(member.id))
            await ctx.guild.ban(member, reason=reason, delete_message_days=0)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
            return
        await crud.add_timed_restriction(member.id, unban_time, 'timeban')
        await ctx.send(f"{member} is now b& until {unban_time_string} {time.tzname[0]}. 👍")
        msg = f"⛔ **Time ban**: {ctx.author.mention} banned {member.mention} until {unban_time_string} | {member}\n🏷 __User ID__: {member.id}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.channels['server-logs'].send(msg)
        signature = utils.command_signature(ctx.command)
        await self.bot.channels['mod-logs'].send(msg + (f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user." if reason == "" else ""))

    @is_staff("OP")
    @commands.bot_has_permissions(kick_members=True)
    @commands.command(name="softban", aliases=["gentleyeet"])
    async def softban_member(self, ctx, member: Union[discord.Member, discord.User], *, reason):
        """Soft-ban a user. OP+ only.

        This "bans" the user without actually doing a ban on Discord. The bot will instead kick the user every time they join. Discord bans are account- and IP-based."""
        if await check_bot_or_staff(ctx, member, "softban"):
            return

        await crud.add_softban(member.id, ctx.author.id, reason)

        if isinstance(member, discord.Member):
            msg = f"This account is no longer permitted to participate in {ctx.guild.name}. The reason is: {reason}"
            await utils.send_dm_message(member, msg, ctx)
            try:
                await member.kick(reason=reason)
            except discord.errors.Forbidden:
                await ctx.send("💢 I don't have permission to do this.")
                return
        await ctx.send(f"{member} is now b&. 👍")
        msg = f"⛔ **Soft-ban**: {ctx.author.mention} soft-banned {member.mention} | {self.bot.escape_text(member)}\n🏷 __User ID__: {member.id}\n✏️ __Reason__: {reason}"
        await self.bot.channels['mod-logs'].send(msg)
        await self.bot.channels['server-logs'].send(msg)

    @is_staff("OP")
    @commands.command(name="unsoftban")
    async def unsoftban_member(self, ctx, user: Union[discord.Member, discord.User]):
        """Un-soft-ban a user based on ID. OP+ only."""
        await crud.remove_softban(user.id)
        await ctx.send(f"{user} has been unbanned!")
        msg = f"⚠️ **Un-soft-ban**: {ctx.author.mention} un-soft-banned {self.bot.escape_text(user)}"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("SuperOP")
    @commands.command(name="scamban")
    async def scamban_member(self, ctx, member: discord.Member, site: str):
        """Bans member deleting message from last day and add a scamming site to the filter"""
        if site in self.bot.wordfilter.filter['scamming site']:
            await ctx.send("Site is already in the filter!")
        elif ' ' in site or '-' in site:
            await ctx.send("Filtered words can't contain dashes or spaces, please add the site properly with wordfilter command.")
        else:
            await self.bot.wordfilter.add(word=site, kind="scamming site")
            await self.bot.channels['mod-logs'].send(f"🆕 **Added**: {ctx.author.mention} added `{site}` to the word filter!")
        await member.ban(reason="Linking scamming site", delete_message_days=1)
        await ctx.send(f"{member} is now b&. 👍")
        msg = f"⛔ **Ban**: {ctx.author.mention} banned {member.mention} | {self.bot.escape_text(member)}\n🏷 __User ID__: {member.id}\n✏️ __Reason__: Linking scamming site"
        await self.bot.channels['server-logs'].send(msg)
        await self.bot.channels['mod-logs'].send(msg)


def setup(bot):
    bot.add_cog(KickBan(bot))
