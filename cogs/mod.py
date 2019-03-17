import datetime
import re
import time
import discord
from discord.ext import commands
from subprocess import call
from cogs.checks import is_staff
from cogs.database import DatabaseCog
from cogs.converters import SafeMember


class Mod(DatabaseCog):
    """
    Staff commands.
    """

    @is_staff("Owner")
    @commands.command()
    async def quit(self, ctx):
        """Stops the bot."""
        await ctx.send("👋 Bye bye!")
        self.bot.conn.close()
        await self.bot.close()

    @is_staff("SuperOP")
    @commands.command()
    async def pull(self, ctx):
        """Pull new changes from GitHub and restart."""
        await ctx.send("Pulling changes...")
        call(['git', 'pull'])
        await ctx.send("👋 Restarting bot!")
        await self.quit(ctx)

    @is_staff("Helper")
    @commands.command(hidden=True, )
    async def userinfo(self, ctx, u: discord.Member = None):
        """Gets user info. Staff and Helpers only."""
        role = u.top_role.name
        await ctx.send(
            "name = {}\nid = {}\ndiscriminator = {}\navatar = {}\nbot = {}\navatar_url = {}\ndefault_avatar = {}\ndefault_avatar_url = <{}>\ncreated_at = {}\ndisplay_name = {}\njoined_at = {}\nstatus = {}\ngame = {}\ncolour = {}\ntop_role = {}\n".format(
                u.name, u.id, u.discriminator, u.avatar, u.bot, u.avatar_url, u.default_avatar, u.default_avatar_url,
                u.created_at, u.display_name, u.joined_at, u.status, u.game, u.colour,
                self.bot.help_command.remove_mentions(role)))

    @is_staff("HalfOP")
    @commands.command(hidden=True)
    async def matchuser(self, ctx, *, rgx: str):
        """Match users by regex."""
        author = ctx.author
        msg = "```\nmembers:\n"
        for m in self.bot.guild.members:
            if bool(re.search(rgx, m.name, re.IGNORECASE)):
                msg += "{} - {}#{}\n".format(m.id, m.name, m.discriminator)
        msg += "```"
        await author.send(msg)

    @is_staff("Owner")
    @commands.command(hidden=True)
    async def multiban(self, ctx, users : commands.Greedy[SafeMember]):
        """Multi-ban users."""
        author = ctx.author
        msg = "```\nbanned:\n"
        for m in users:
            msg += "{} - {}#{}\n".format(m.id, m.name, m.discriminator)
            try:
                await m.ban()
            except discord.errors.NotFound:
                pass
        msg += "```"
        await author.send(msg)

    @is_staff("Owner")
    @commands.command(hidden=True)
    async def multibanre(self, ctx, *, rgx: str):
        """Multi-ban users by regex."""
        author = ctx.author
        msg = "```\nbanned:\n"
        toban = []  # because "dictionary changed size during iteration"
        for m in self.bot.guild.members:
            if bool(re.search(rgx, m.name, re.IGNORECASE)):
                msg += "{} - {}#{}\n".format(m.id, m.name, m.discriminator)
                toban.append(m)
        for m in toban:
            try:
                await m.ban()
            except discord.errors.NotFound:
                pass
        msg += "```"
        await author.send(msg)

    @is_staff("HalfOP")
    @commands.command(aliases=["clear"])
    async def purge(self, ctx, limit: int):
        """Clears a given number of messages. Staff only."""
        try:
            await ctx.channel.purge(limit=limit)
            msg = "🗑 **Cleared**: {} cleared {} messages in {}".format(ctx.author.mention, limit, ctx.channel.mention)
            await self.bot.modlogs_channel.send(msg)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.command()
    async def mute(self, ctx, member: SafeMember, *, reason=""):
        """Mutes a user so they can't speak. Staff only."""
        try:
            self.add_restriction(member.id, "Muted")
            await member.add_roles(self.bot.muted_role)
            msg_user = "You were muted!"
            if reason != "":
                msg_user += " The given reason is: " + reason
            try:
                await member.send(msg_user)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await ctx.send("{} can no longer speak.".format(member.mention))
            msg = "🔇 **Muted**: {} muted {} | {}#{}".format(ctx.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            else:
                msg += "\nPlease add an explanation below. In the future, it is recommended to use `.mute <user> [reason]` as the reason is automatically sent to the user."
            await self.bot.modlogs_channel.send(msg)
            # change to permanent mute
            self.remove_timed_restriction(member.id, 'timemute')
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.command()
    async def timemute(self, ctx, member: SafeMember, length, *, reason=""):
        """Mutes a user for a limited period of time so they can't speak. Staff only.\n\nLength format: #d#h#m#s"""
        try:
            self.add_restriction(member.id, "Muted")
            await member.add_roles(self.bot.muted_role)
            issuer = ctx.author
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
            unmute_time = timestamp + delta
            unmute_time_string = unmute_time.strftime("%Y-%m-%d %H:%M:%S")
            self.add_timed_restriction(member.id, unmute_time_string, 'timemute')
            #self.add_restriction(member.id, 'Muted')
            msg_user = "You were muted!"
            if reason != "":
                msg_user += " The given reason is: " + reason
            msg_user += "\n\nThis mute expires {} {}.".format(unmute_time_string, time.tzname[0])
            try:
                await member.send(msg_user)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await ctx.send("{} can no longer speak.".format(member.mention))
            msg = "🔇 **Timed mute**: {} muted {} until {} | {}#{}".format(issuer.mention, member.mention, unmute_time_string, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            else:
                msg += "\nPlease add an explanation below. In the future, it is recommended to use `.timemute <user> <length> [reason]` as the reason is automatically sent to the user."
            await self.bot.modlogs_channel.send(msg)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.command()
    async def unmute(self, ctx, member: SafeMember):
        """Unmutes a user so they can speak. Staff only."""
        try:
            self.remove_restriction(member.id, "Muted")
            await member.remove_roles(self.bot.muted_role)
            await ctx.send("{} can now speak again.".format(member.mention))
            msg = "🔈 **Unmuted**: {} unmuted {} | {}#{}".format(ctx.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            await self.bot.modlogs_channel.send(msg)
            self.remove_timed_restriction(member.id, 'timemute')
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.command()
    async def elsewhere(self, ctx, member: SafeMember):
        """Restore elsewhere access for a user. Staff only."""
        try:
            self.remove_restriction(member.id, "no-elsewhere")
            await self.member.remove_roles(self.bot.noelsewhere_role)
            await ctx.send("{} can access elsewhere again.".format(member.mention))
            msg = "⭕️ **Restored elsewhere**: {} restored elsewhere access to {} | {}#{}".format(ctx.author.mention, member.mention, self.bot.escape_name(member.name), member.discriminator)
            await self.bot.modlogs_channel.send(msg)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.command()
    async def noelsewhere(self, ctx, member: SafeMember, *, reason=""):
        """Removes elsewhere access from a user. Staff only."""
        try:
            self.add_restriction(member.id, "no-elsewhere")
            member.add_roles(self.bot.noelsewhere_role)
            member.remove_roles(self.bot.elsewhere_role)
            await ctx.send("{} can no longer access elsewhere.".format(member.mention))
            msg = "🚫 **Removed elsewhere**: {} removed elsewhere access from {} | {}#{}".format(ctx.author.mention, member.mention, self.bot.escape_name(member.name), member.discriminator)
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            else:
                msg += "\nPlease add an explanation below. In the future, it is recommended to use `.noelsewhere <user> [reason]` as the reason is automatically sent to the user."
            await self.bot.modlogs_channel.send(msg)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.command()
    async def noembed(self, ctx, member: SafeMember, *, reason=""):
        """Removes embed permissions from a user. Staff only."""
        try:
            self.add_restriction(member.id, "No-Embed")
            await member.add_roles(self.bot.noembed_role)
            msg_user = "You lost embed and upload permissions!"
            if reason != "":
                msg_user += " The given reason is: " + reason
            msg_user += "\n\nIf you feel this was unjustified, you may appeal in <#270890866820775946>."
            try:
                await member.send(msg_user)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await ctx.send("{} can no longer embed links or attach files.".format(member.mention))
            msg = "🚫 **Removed Embed**: {} removed embed from {} | {}#{}".format(ctx.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            else:
                msg += "\nPlease add an explanation below. In the future, it is recommended to use `.noembed <user> [reason]` as the reason is automatically sent to the user."
            await self.bot.modlogs_channel.send(msg)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.command()
    async def embed(self, ctx, member: SafeMember):
        """Restore embed permissios for a user. Staff only."""
        try:
            self.remove_restriction(member.id, "No-Embed")
            await self.member.remove_roles(self.bot.noembed_role)
            await ctx.send("{} can now embed links and attach files again.".format(member.mention))
            msg = "⭕️ **Restored Embed**: {} restored embed to {} | {}#{}".format(ctx.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            await self.bot.modlogs_channel.send(msg)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("Helper")
    @commands.command()
    async def takehelp(self, ctx, member: SafeMember, *, reason=""):
        """Remove access to help-and-questions. Staff and Helpers only."""
        try:
            self.add_restriction(member.id, "No-Help")
            await member.add_roles(self.bot.nohelp_role)
            msg_user = "You lost access to help channels!"
            if reason != "":
                msg_user += " The given reason is: " + reason
            msg_user += "\n\nIf you feel this was unjustified, you may appeal in <#270890866820775946>."
            try:
                await member.send(msg_user)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await ctx.send("{} can no longer access the help channels.".format(member.mention))
            msg = "🚫 **Help access removed**: {} removed access to help channels from {} | {}#{}".format(ctx.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            else:
                msg += "\nPlease add an explanation below. In the future, it is recommended to use `.takehelp <user> [reason]` as the reason is automatically sent to the user."
            await self.bot.modlogs_channel.send(msg)
            await self.bot.helpers_channel.send(msg)
            #add to .takehelp
            self.remove_timed_restriction(member.id, 'timetakehelp')
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("Helper")
    @commands.command()
    async def givehelp(self, ctx, member: SafeMember):
        """Restore access to help-and-questions. Staff and Helpers only."""
        try:
            self.remove_restriction(member.id, "No-Help")
            await self.member.remove_roles(self.bot.nohelp_role)
            await ctx.send("{} can access the help channels again.".format(member.mention))
            msg = "⭕️ **Help access restored**: {} restored access to help channels to {} | {}#{}".format(ctx.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            await self.bot.modlogs_channel.send(msg)
            await self.bot.helpers_channel.send(msg)
            #add to .givehelp
            self.remove_timed_restriction(member.id, 'timetakehelp')
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("Helper")
    @commands.command()
    async def timetakehelp(self, ctx, member: SafeMember, length, *, reason=""):
        """Restricts a user from Assistance Channels for a limited period of time. Staff and Helpers only.\n\nLength format: #d#h#m#s"""
        try:
            self.add_restriction(member.id, "No-Help")
            await member.add_roles(self.bot.nohelp_role)
            issuer = ctx.author
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
            unnohelp_time = timestamp + delta
            unnohelp_time_string = unnohelp_time.strftime("%Y-%m-%d %H:%M:%S")
            self.add_timed_restriction(member.id, unnohelp_time_string, 'timetakehelp')
            self.add_restriction(member.id, "No-Help")
            msg_user = "You lost access to help channels temporarily!"
            if reason != "":
                msg_user += " The given reason is: " + reason
            msg_user += "\n\nIf you feel this was unjustified, you may appeal in <#270890866820775946>."
            msg_user += "\n\nThis restriction expires {} {}.".format(unnohelp_time_string, time.tzname[0])
            try:
                await member.send(msg_user)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await ctx.send("{} can no longer speak in Assistance Channels.".format(member.mention))
            msg = "🚫 **Timed No-Help**: {} restricted {} until {} | {}#{}".format(issuer.mention, member.mention, unnohelp_time_string, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            else:
                msg += "\nPlease add an explanation below. In the future, it is recommended to use `.timetakehelp <user> <length> [reason]` as the reason is automatically sent to the user."
            await self.bot.modlogs_channel.send(msg)
            await self.bot.helpers_channel.send(msg)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
            
    @is_staff("Helper")
    @commands.command()
    async def takesmallhelp(self, ctx, members: commands.Greedy[SafeMember]):
        """Remove access to small help channel. Staff and Helpers only."""
        for member in members:
            try:
                await member.remove_roles(self.bot.smallhelp_role)
            except discord.errors.Forbidden:
                await ctx.send("💢 I don't have permission to do this.")
        await ctx.send("{} can no longer access the small help channel.".format(', '.join([x.mention for x in members])))
        msg = "⭕️ **Small help access revoked**: {} revoked access to small help channel from {}".format(ctx.author.mention,', '.join(["{} | {}#{}".format(x.mention, x.name, x.discriminator) for x in members]))
        await self.bot.modlogs_channel.send(msg)
        await self.bot.helpers_channel.send(msg)
       
    @is_staff("Helper")
    @commands.command()
    async def givesmallhelp(self, ctx, members: commands.Greedy[SafeMember]):
        """Provide access to small help channel for 1-on-1 help. Staff and Helpers only."""
        for member in members:
            try:
                await member.add_roles(self.bot.smallhelp_role)
            except discord.errors.Forbidden:
                await ctx.send("💢 I don't have permission to do this.")
        await ctx.send("{} can access the small help channel.".format(', '.join([x.mention for x in members])))
        msg = "⭕️ **Small help access granted**: {} granted access to small help channel to {}".format(ctx.author.mention, ', '.join(["{} | {}#{}".format(x.mention, x.name, x.discriminator) for x in members]))
        await self.bot.modlogs_channel.send(msg)
        await self.bot.helpers_channel.send(msg)
            
    @is_staff("Helper")
    @commands.command(pass_context=True, name="probate")
    async def probate(self, ctx, member: SafeMember, *, reason=""):
        """Probate a user. Staff and Helpers only."""
        try:
            self.add_restriction(member.id, "Probation")
            await member.add_roles(self.bot.probation_role)
            msg_user = "You are under probation!"
            if reason != "":
                msg_user += " The given reason is: " + reason
            try:
                await member.send(msg_user)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await ctx.send("{} is now in probation.".format(member.mention))
            msg = "🚫 **Probated**: {} probated {} | {}#{}".format(ctx.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            else:
                msg += "\nPlease add an explanation below. In the future, it is recommended to use `.probate <user> [reason]` as the reason is automatically sent to the user."
            await self.bot.modlogs_channel.send(msg)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("Helper")
    @commands.command()
    async def unprobate(self, ctx, member: SafeMember):
        """Unprobate a user. Staff and Helpers only."""
        try:
            self.remove_restriction(member.id, "Probation")
            await self.member.remove_roles(self.bot.probation_role)
            await ctx.send("{} is out of probation.".format(member.mention))
            msg = "⭕️ **Un-probated**: {} un-probated {} | {}#{}".format(ctx.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            await self.bot.modlogs_channel.send(msg)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("OP")
    @commands.command()
    async def playing(self, ctx, *gamename):
        """Sets playing message. Staff only."""
        try:
            await self.bot.change_presence(activity=discord.Game(name='{}'.format(" ".join(gamename))))
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("OP")
    @commands.command()
    async def status(self, ctx, status):
        """Sets status. Staff only."""
        try:
            if status == "online":
                await self.bot.change_presence(status=discord.Status.online)
            elif status == "offline":
                await self.bot.change_presence(status=discord.Status.offline)
            elif status == "idle":
                await self.bot.change_presence(status=discord.Status.idle)
            elif status == "dnd":
                await self.bot.change_presence(status=discord.Status.dnd)
            elif status == "invisible":
                await self.bot.change_presence(status=discord.Status.invisible)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("OP")
    @commands.command(hidden=True)
    async def username(self, ctx, *, username):
        """Sets bot name. Staff only."""
        try:
            await self.bot.user.edit(username=('{}'.format(username)))
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("OP")
    @commands.command(hidden=True)
    async def updatestaff(self, ctx):
        """Updates the staff list based on staff member in the server."""
        removed = []
        for staffmember in self.get_staff():
            if ctx.guild.get_member(staffmember) is None:
                self.remove_staff(staffmember)
                removed.append(await self.bot.get_user_info(staffmember))

        for helper in self.get_helpers():
            if ctx.guild.get_member(helper) is None:
                self.remove_helper(helper)
                removed.append(await self.bot.get_user_info(helper))
        if not removed:
            await ctx.send("Updated Staff list, no staff removed!")
        else:
            msg = "Updated staff list. Removed {}.".format(", ".join([x.name for x in removed]))
            await ctx.send(msg)
            modmsg = "🛠 **Updated Staff list**: {} updated the staff list.\n:pencil: __Users removed__: {}".format(ctx.author.mention,", ".join(["{} | {}#{}".format(x.id,x.name,x.discriminator) for x in removed]))
            await self.bot.modlogs_channel.send(modmsg)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send("{} You don't have permission to use this command.".format(ctx.author.mention))


def setup(bot):
    bot.add_cog(Mod(bot))
