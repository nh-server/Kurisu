import datetime
import discord
import re
import time
from cogs.database import DatabaseCog
from discord.ext import commands
from cogs import converters
from cogs.checks import is_staff, check_staff
import sqlite3


@commands.guild_only()
class KickBan(DatabaseCog):
    """
    Kicking and banning users.
    """

    async def meme(self, beaner, beaned, action, channel, reason):
        await channel.send("Seriously? What makes you think it's okay to try and {} another staff or helper like that?".format(action))
        msg = "{} attempted to {} {}|{}#{} in {} ".format(beaner.mention, action, beaned.mention,
                                                                  self.bot.escape_name(beaned.name),
                                                                  beaned.discriminator, channel.mention)
        if reason != "":
            msg += "for the reason " + reason
        await self.bot.meta_channel.send(msg + (" without a reason" if reason == "" else ""))

    @is_staff("HalfOP")
    @commands.command(name="kick")
    async def kick_member(self, ctx, member: converters.SafeMember, *, reason=""):
        """Kicks a user from the server. Staff only."""
        if check_staff(member.id, 'Helper'):
            await self.meme(ctx.author, member, "kick", ctx.channel, reason)
            return
        msg = "You were kicked from {}.".format(ctx.guild.name)
        if reason != "":
            msg += " The given reason is: " + reason
        msg += "\n\nYou are able to rejoin the server, but please read the rules in #welcome-and-rules before participating again."
        try:
            await member.send(msg)
        except discord.errors.Forbidden:
            pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
        self.bot.actions.append("uk:"+str(member.id))
        try:
            await member.kick(reason=reason if reason else 'No reason')
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
        await ctx.send("{} is now gone. 👌".format(self.bot.help_command.remove_mentions(member.name)))
        msg = "👢 **Kick**: {} kicked {} | {}#{}\n🏷 __User ID__: {}".format(ctx.author.mention, member.mention, self.bot.escape_name(member.name), member.discriminator, member.id)
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.serverlogs_channel.send(msg)
        await self.bot.modlogs_channel.send(msg + ("\nPlease add an explanation below. In the future, it is recommended to use `.kick <user> [reason]` as the reason is automatically sent to the user." if reason == "" else ""))


    @is_staff("OP")
    @commands.command(name="ban")
    async def ban_member(self, ctx, member: converters.SafeMember, *, reason=""):
        """Bans a user from the server. OP+ only."""
        if check_staff(member.id, 'Helper'):
            await self.meme(ctx.author, member, "ban", ctx.channel, reason)
            return
        msg = "You were banned from {}.".format(ctx.guild.name)
        if reason != "":
            msg += " The given reason is: " + reason
        msg += "\n\nThis ban does not expire."
        try:
            await member.send(msg)
        except discord.errors.Forbidden:
            pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
        self.bot.actions.append("ub:"+str(member.id))
        try:
            await member.ban()
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
        await ctx.send("{} is now b&. 👍".format(self.bot.help_command.remove_mentions(member)))
        msg = "⛔ **Ban**: {} banned {} | {}#{}\n🏷 __User ID__: {}".format(ctx.author.mention, member.mention, self.bot.escape_name(member.name), member.discriminator, member.id)
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.serverlogs_channel.send(msg)
        await self.bot.modlogs_channel.send(msg + ("\nPlease add an explanation below. In the future, it is recommended to use `.ban <user> [reason]` as the reason is automatically sent to the user." if reason == "" else ""))

    @is_staff("OP")
    @commands.command(name="banid")
    async def banid_member(self, ctx, userid: int, *, reason=""):
        """Bans a user id from the server. OP+ only."""
        try:
            user = await self.bot.get_user_info(userid)
        except discord.errors.NotFound:
            await ctx.send("No user associated with ID {}.".format(user.id))
        if check_staff(user.id, 'Helper'):
            await ctx.send("You can't ban another staffer with this command!")
            return
        self.bot.actions.append("ub:" + str(user.id))
        try:
            await ctx.guild.ban(user)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
        await ctx.send("User {} | {} is now b&. 👍".format(user.id, user.name))
        msg = "⛔ **Ban**: {} banned ID {}".format(ctx.author.mention, user.id)
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.serverlogs_channel.send(msg)
        await self.bot.modlogs_channel.send(msg + (
            "\nPlease add an explanation below. In the future, it is recommended to use `.banid <userid> [reason]` as the reason is automatically sent to the user." if reason == "" else ""))

    @is_staff("OP")
    @commands.command(name="silentban", hidden=True)
    async def silentban_member(self, ctx, member: converters.SafeMember, *, reason=""):
        """Bans a user from the server, without a notification. OP+ only."""
        if check_staff(member.id, 'Helper'):
            await self.meme(ctx.author, member, "ban", ctx.channel, reason)
            return
        self.bot.actions.append("ub:"+str(member.id))
        try:
            await member.ban()
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
        await ctx.send("{} is now b&. 👍".format(self.bot.escape_name(member)))
        msg = "⛔ **Silent ban**: {} banned {} | {}#{}\n🏷 __User ID__: {}".format(ctx.author.mention, member.mention, self.bot.escape_name(member.name), member.discriminator, member.id)
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.serverlogs_channel.send(msg)
        await self.bot.modlogs_channel.send(msg + ("\nPlease add an explanation below. In the future, it is recommended to use `.silentban <user> [reason]`." if reason == "" else ""))

    @is_staff("OP")
    @commands.command(name="timeban")
    async def timeban_member(self, ctx, member: converters.SafeMember, length, *, reason="no reason"):
        """Bans a user for a limited period of time. OP+ only.\n\nLength format: #d#h#m#s"""
        if check_staff(member.id, 'Helper'):
            await self.meme(ctx.author, member, "timeban", ctx.channel, reason)
            return
        # thanks Luc#5653
        units = {
            "d": 86400,
            "h": 3600,
            "m": 60,
            "s": 1
        }
        seconds = 0
        match = re.findall("([0-9]+[smhd])", length)  # Thanks to 3dshax server's former bot
        if match is None:
            return None
        for item in match:
            seconds += int(item[:-1]) * units[item[-1]]
        timestamp = datetime.datetime.now()
        delta = datetime.timedelta(seconds=seconds)
        unban_time = timestamp + delta
        unban_time_string = unban_time.strftime("%Y-%m-%d %H:%M:%S")
        self.add_timed_restriction(self, member.id, unban_time_string, 'timeban')
        self.bot.timebans[str(member.id)] = [member, unban_time, False]  # last variable is "notified", for <=30 minute notifications
        msg = "You were banned from {}.".format(ctx.guild.name)
        if reason != "":
            msg += " The given reason is: " + reason
        msg += "\n\nThis ban expires {} {}.".format(unban_time_string, time.tzname[0])
        try:
            await member.send(msg)
        except discord.errors.Forbidden:
            pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
        self.bot.actions.append("ub:"+str(member.id))
        try:
            await member.ban(reason=reason)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
        await ctx.send("{} is now b& until {} {}. 👍".format(self.bot.escape_name(member), unban_time_string, time.tzname[0]))
        msg = "⛔ **Time ban**: {} banned {} until {} | {}#{}\n🏷 __User ID__: {}".format(ctx.author.mention, member.mention, unban_time_string, self.bot.escape_name(member.name), member.discriminator, member.id)
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.serverlogs_channel.send(msg)
        await self.bot.modlogs_channel.send(msg + ("\nPlease add an explanation below. In the future, it is recommended to use `.timeban <user> <length> [reason]` as the reason is automatically sent to the user." if reason == "" else ""))

    @is_staff("OP")
    @commands.command(name="softban")
    async def softban_member(self, ctx, member: converters.SafeMember, *, reason):
        """Soft-ban a user. OP+ only.\n\nThis "bans" the user without actually doing a ban on Discord. The bot will instead kick the user every time they join. Discord bans are account- and IP-based."""
        if check_staff(member.id, 'Helper'):
            await self.meme(ctx.author, member, "softban", ctx.channel, reason)
            return
        self.add_softban(ctx, member, reason)
        msg = "This account is no longer permitted to participate in {}. The reason is: {}".format(ctx.guild.name, reason)
        await member.send(msg)
        try:
            await member.kick(reason=reason)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
        await ctx.send("{} is now b&. 👍".format(self.bot.help_command.remove_mentions(member)))
        msg = "⛔ **Soft-ban**: {} soft-banned {} | {}#{}\n🏷 __User ID__: {}\n✏️ __Reason__: {}".format(ctx.author.mention, member.mention, self.bot.help_command.remove_mentions(member.name), member.discriminator, member.id, reason)
        await self.bot.modlogs_channel.send(msg)
        await self.bot.serverlogs_channel.send(msg)

    @is_staff("OP")
    @commands.command(name="softbanid")
    async def softbanid_member(self, ctx, user_id: int, *, reason):
        """Soft-ban a user based on ID. OP+ only.\n\nThis "bans" the user without actually doing a ban on Discord. The bot will instead kick the user every time they join. Discord bans are account- and IP-based."""
        if check_staff(str(user_id), 'Helper'):
            await ctx.send("You can't softban another staffer with this command!")
            return
        user = await self.bot.get_user_info(user_id)
        try:
            self.add_softban(ctx, user, reason)
        except sqlite3.IntegrityError:
            await ctx.send('User is already softbanned.')
            return
        await ctx.send("ID {} is now b&. 👍".format(user_id))
        msg = "⛔ **Soft-ban**: {} soft-banned ID {}\n✏️ __Reason__: {}".format(ctx.author.mention, user_id, reason)
        await self.bot.modlogs_channel.send(msg)
        await self.bot.serverlogs_channel.send(msg)

    @is_staff("OP")
    @commands.command(name="unsoftban")
    async def unsoftban_member(self, ctx, user_id: int):
        """Un-soft-ban a user based on ID. OP+ only."""
        self.remove_softban(user_id)
        user = await self.bot.get_user_info(user_id)
        await ctx.send("{} has been unbanned!".format(self.bot.help_command.remove_mentions(user.name)))
        msg = "⚠️ **Un-soft-ban**: {} un-soft-banned {}".format(ctx.author.mention, self.bot.help_command.remove_mentions(user.name))
        await self.bot.modlogs_channel.send(msg)

def setup(bot):
    bot.add_cog(KickBan(bot))
