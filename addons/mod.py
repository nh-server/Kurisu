import datetime
import discord
import json
import re
import time
from discord.ext import commands
from subprocess import call
from addons.checks import is_staff
from addons import converters

class Mod:
    """
    Staff commands.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    async def add_restriction(self, member, rst):
        with open("data/restrictions.json", "r") as f:
            rsts = json.load(f)
        if member.id not in rsts:
            rsts[member.id] = []
        if rst not in rsts[member.id]:
            rsts[member.id].append(rst)
        with open("data/restrictions.json", "w") as f:
            json.dump(rsts, f)

    async def remove_restriction(self, member, rst):
        with open("data/restrictions.json", "r") as f:
            rsts = json.load(f)
        if member.id not in rsts:
            rsts[member.id] = []
        if rst in rsts[member.id]:
            rsts[member.id].remove(rst)
        with open("data/restrictions.json", "w") as f:
            json.dump(rsts, f)

    @is_staff("Owner")
    @commands.command()
    async def quit(self, *gamename):
        """Stops the bot."""
        await self.bot.say("👋 Bye bye!")
        await self.bot.close()

    @is_staff("SuperOP")
    @commands.command(hidden=True)
    async def pull(self, *gamename):
        """Pull new changes from GitHub and restart."""
        await self.bot.say("Pulling changes...")
        call(['git', 'pull'])
        await self.bot.say("👋 Restarting bot!")
        await self.bot.close()

    @is_staff("Helper")
    @commands.command(pass_context=True, hidden=True)
    async def userinfo(self, ctx, u: discord.Member = None):
        """Gets user info. Staff and Helpers only."""
        role = u.top_role.name
        if role == "@everyone":
            role = "@ everyone"
        await self.bot.say("name = {}\nid = {}\ndiscriminator = {}\navatar = {}\nbot = {}\navatar_url = {}\ndefault_avatar = {}\ndefault_avatar_url = <{}>\ncreated_at = {}\ndisplay_name = {}\njoined_at = {}\nstatus = {}\ngame = {}\ncolour = {}\ntop_role = {}\n".format(u.name, u.id, u.discriminator, u.avatar, u.bot, u.avatar_url, u.default_avatar, u.default_avatar_url, u.created_at, u.display_name, u.joined_at, u.status, u.game, u.colour, role))

    @is_staff("HalfOP")
    @commands.command(pass_context=True, hidden=True)
    async def matchuser(self, ctx, *, rgx: str):
        """Match users by regex."""
        author = ctx.message.author
        msg = "```\nmembers:\n"
        for m in self.bot.server.members:
            if bool(re.search(rgx, m.name, re.IGNORECASE)):
                msg += "{} - {}#{}\n".format(m.id, m.name, m.discriminator)
        msg += "```"
        await self.bot.send_message(author, msg)

    @is_staff("Owner")
    @commands.command(pass_context=True, hidden=True)
    async def multiban(self, ctx, *, members: str):
        """Multi-ban users."""
        author = ctx.message.author
        msg = "```\nbanned:\n"
        for m in ctx.message.mentions:
            msg += "{} - {}#{}\n".format(m.id, m.name, m.discriminator)
            try:
                await self.bot.ban(m)
            except discord.error.NotFound:
                pass
        msg += "```"
        await self.bot.send_message(author, msg)

    @is_staff("Owner")
    @commands.command(pass_context=True, hidden=True)
    async def multibanre(self, ctx, *, rgx: str):
        """Multi-ban users by regex."""
        author = ctx.message.author
        msg = "```\nbanned:\n"
        toban = []  # because "dictionary changed size during iteration"
        for m in self.bot.server.members:
            if bool(re.search(rgx, m.name, re.IGNORECASE)):
                msg += "{} - {}#{}\n".format(m.id, m.name, m.discriminator)
                toban.append(m)
        for m in toban:
            try:
                await self.bot.ban(m)
            except discord.error.NotFound:
                pass
        msg += "```"
        await self.bot.send_message(author, msg)

    @is_staff("HalfOP")
    @commands.command(pass_context=True, name="clear")
    async def purge(self, ctx, limit: int):
        """Clears a given number of messages. Staff only."""
        try:
            await self.bot.purge_from(ctx.message.channel, limit=limit)
            msg = "🗑 **Cleared**: {} cleared {} messages in {}".format(ctx.message.author.mention, limit, ctx.message.channel.mention)
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.command(pass_context=True, name="mute")
    async def mute(self, ctx, member: converters.SafeMember, *, reason=""):
        """Mutes a user so they can't speak. Staff only."""
        try:
            await self.add_restriction(member, "Muted")
            await self.bot.add_roles(member, self.bot.muted_role)
            msg_user = "You were muted!"
            if reason != "":
                msg_user += " The given reason is: " + reason
            try:
                await self.bot.send_message(member, msg_user)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await self.bot.say("{} can no longer speak.".format(member.mention))
            msg = "🔇 **Muted**: {} muted {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            else:
                msg += "\nPlease add an explanation below. In the future, it is recommended to use `.mute <user> [reason]` as the reason is automatically sent to the user."
            await self.bot.send_message(self.bot.modlogs_channel, msg)
            # change to permanent mute
            if member.id in self.bot.timemutes:
                self.bot.timemutes.pop(member.id)
                with open("data/timemutes.json", "r") as f:
                    timemutes = json.load(f)
                timemutes.pop(member.id)
                with open("data/timemutes.json", "w") as f:
                    json.dump(timemutes, f)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.command(pass_context=True, name="timemute")
    async def timemute(self, ctx, member: converters.SafeMember, length, *, reason=""):
        """Mutes a user for a limited period of time so they can't speak. Staff only.\n\nLength format: #d#h#m#s"""
        try:
            await self.add_restriction(member, "Muted")
            await self.bot.add_roles(member, self.bot.muted_role)
            issuer = ctx.message.author
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
            with open("data/timemutes.json", "r") as f:
                timemutes = json.load(f)
            timemutes[member.id] = unmute_time_string
            self.bot.timemutes[member.id] = [unmute_time, False]  # last variable is "notified", for <=10 minute notifications
            with open("data/timemutes.json", "w") as f:
                json.dump(timemutes, f)
            msg_user = "You were muted!"
            if reason != "":
                msg_user += " The given reason is: " + reason
            msg_user += "\n\nThis mute expires {} {}.".format(unmute_time_string, time.tzname[0])
            try:
                await self.bot.send_message(member, msg_user)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await self.bot.say("{} can no longer speak.".format(member.mention))
            msg = "🔇 **Timed mute**: {} muted {} until {} | {}#{}".format(issuer.mention, member.mention, unmute_time_string, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            else:
                msg += "\nPlease add an explanation below. In the future, it is recommended to use `.timemute <user> <length> [reason]` as the reason is automatically sent to the user."
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.command(pass_context=True, name="unmute")
    async def unmute(self, ctx, member: converters.SafeMember):
        """Unmutes a user so they can speak. Staff only."""
        try:
            await self.remove_restriction(member, "Muted")
            await self.bot.remove_roles(member, self.bot.muted_role)
            await self.bot.say("{} can now speak again.".format(member.mention))
            msg = "🔈 **Unmuted**: {} unmuted {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            await self.bot.send_message(self.bot.modlogs_channel, msg)
            if member.id in self.bot.timemutes:
                self.bot.timemutes.pop(member.id)
                with open("data/timemutes.json", "r") as f:
                    timemutes = json.load(f)
                timemutes.pop(member.id)
                with open("data/timemutes.json", "w") as f:
                    json.dump(timemutes, f)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.command(pass_context=True)
    async def art(self, ctx, member: converters.SafeMember):
        """Restore art-discussion access for a user. Staff only."""
        try:
            await self.remove_restriction(member, "no-art")
            await self.bot.remove_roles(member, self.bot.noart_role)
            await self.bot.say("{} can access art-discussion again.".format(member.mention))
            msg = "⭕️ **Restored art**: {} restored art access to {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.command(pass_context=True)
    async def noart(self, ctx, member: converters.SafeMember, *, reason=""):
        """Removes art-discussion access from a user. Staff only."""
        try:
            await self.add_restriction(member, "no-art")
            roles = member.roles

            roles = [x for x in roles if x != self.bot.art_role]
            if self.bot.noart_role not in roles:
                roles.append(self.bot.noart_role)
            await self.bot.replace_roles(member, *roles)
            await self.bot.say("{} can no longer access art-discussion.".format(member.mention))
            msg = "🚫 **Removed art**: {} removed art access from {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            else:
                msg += "\nPlease add an explanation below. In the future, it is recommended to use `.noart <user> [reason]` as the reason is automatically sent to the user."
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.command(pass_context=True)
    async def elsewhere(self, ctx, member: converters.SafeMember):
        """Restore elsewhere access for a user. Staff only."""
        try:
            await self.remove_restriction(member, "no-elsewhere")
            await self.bot.remove_roles(member, self.bot.noelsewhere_role)
            await self.bot.say("{} can access elsewhere again.".format(member.mention))
            msg = "⭕️ **Restored elsewhere**: {} restored elsewhere access to {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.command(pass_context=True)
    async def noelsewhere(self, ctx, member: converters.SafeMember, *, reason=""):
        """Removes elsewhere access from a user. Staff only."""
        try:
            await self.add_restriction(member, "no-elsewhere")
            roles = member.roles

            roles = [x for x in roles if x != self.bot.elsewhere_role]
            if self.bot.noelsewhere_role not in roles:
                roles.append(self.bot.noelsewhere_role)
            await self.bot.replace_roles(member, *roles)
            await self.bot.say("{} can no longer access elsewhere.".format(member.mention))
            msg = "🚫 **Removed elsewhere**: {} removed elsewhere access from {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            else:
                msg += "\nPlease add an explanation below. In the future, it is recommended to use `.noelsewhere <user> [reason]` as the reason is automatically sent to the user."
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.command(pass_context=True, name="noembed")
    async def noembed(self, ctx, member: converters.SafeMember, *, reason=""):
        """Removes embed permissions from a user. Staff only."""
        try:
            await self.add_restriction(member, "No-Embed")
            await self.bot.add_roles(member, self.bot.noembed_role)
            msg_user = "You lost embed and upload permissions!"
            if reason != "":
                msg_user += " The given reason is: " + reason
            msg_user += "\n\nIf you feel this was unjustified, you may appeal in <#270890866820775946>."
            try:
                await self.bot.send_message(member, msg_user)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await self.bot.say("{} can no longer embed links or attach files.".format(member.mention))
            msg = "🚫 **Removed Embed**: {} removed embed from {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            else:
                msg += "\nPlease add an explanation below. In the future, it is recommended to use `.noembed <user> [reason]` as the reason is automatically sent to the user."
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.command(pass_context=True, name="embed")
    async def embed(self, ctx, member: converters.SafeMember):
        """Restore embed permissios for a user. Staff only."""
        try:
            await self.remove_restriction(member, "No-Embed")
            await self.bot.remove_roles(member, self.bot.noembed_role)
            await self.bot.say("{} can now embed links and attach files again.".format(member.mention))
            msg = "⭕️ **Restored Embed**: {} restored embed to {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @is_staff("Helper")
    @commands.command(pass_context=True, name="takehelp", aliases=["nohelp"])
    async def takehelp(self, ctx, member: converters.SafeMember, *, reason=""):
        """Remove access to help-and-questions. Staff and Helpers only."""
        try:
            await self.add_restriction(member, "No-Help")
            await self.bot.add_roles(member, self.bot.nohelp_role)
            msg_user = "You lost access to help channels!"
            if reason != "":
                msg_user += " The given reason is: " + reason
            msg_user += "\n\nIf you feel this was unjustified, you may appeal in <#270890866820775946>."
            try:
                await self.bot.send_message(member, msg_user)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await self.bot.say("{} can no longer access the help channels.".format(member.mention))
            msg = "🚫 **Help access removed**: {} removed access to help channels from {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            else:
                msg += "\nPlease add an explanation below. In the future, it is recommended to use `.takehelp <user> [reason]` as the reason is automatically sent to the user."
            await self.bot.send_message(self.bot.modlogs_channel, msg)
            await self.bot.send_message(self.bot.helpers_channel, msg)
            #add to .takehelp
            if member.id in self.bot.timenohelp:
                self.bot.timenohelp.pop(member.id)
                with open("data/timenohelp.json", "r") as f:
                    timenohelp = json.load(f)
                timenohelp.pop(member.id)
                with open("data/timenohelp.json", "w") as f:
                    json.dump(timenohelp, f)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @is_staff("Helper")
    @commands.command(pass_context=True, name="givehelp")
    async def givehelp(self, ctx, member: converters.SafeMember):
        """Restore access to help-and-questions. Staff and Helpers only."""
        try:
            await self.remove_restriction(member, "No-Help")
            await self.bot.remove_roles(member, self.bot.nohelp_role)
            await self.bot.say("{} can access the help channels again.".format(member.mention))
            msg = "⭕️ **Help access restored**: {} restored access to help channels to {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            await self.bot.send_message(self.bot.modlogs_channel, msg)
            await self.bot.send_message(self.bot.helpers_channel, msg)
            #add to .givehelp
            if member.id in self.bot.timenohelp:
                self.bot.timenohelp.pop(member.id)
                with open("data/timenohelp.json", "r") as f:
                    timenohelp = json.load(f)
                timenohelp.pop(member.id)
                with open("data/timenohelp.json", "w") as f:
                    json.dump(timenohelp, f)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @is_staff("Helper")
    @commands.command(pass_context=True, name="timetakehelp", aliases=["timenohelp"])
    async def timetakehelp(self, ctx, member: converters.SafeMember, length, *, reason=""):
        """Restricts a user from Assistance Channels for a limited period of time. Staff and Helpers only.\n\nLength format: #d#h#m#s"""
        try:
            await self.add_restriction(member, "No-Help")
            await self.bot.add_roles(member, self.bot.nohelp_role)
            issuer = ctx.message.author
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
            with open("data/timenohelp.json", "r") as f:
                timenohelp = json.load(f)
            timenohelp[member.id] = unnohelp_time_string
            self.bot.timenohelp[member.id] = [unnohelp_time, False]  # last variable is "notified", for <=10 minute notifications
            with open("data/timenohelp.json", "w") as f:
                json.dump(timenohelp, f)
            msg_user = "You lost access to help channels temporarily!"
            if reason != "":
                msg_user += " The given reason is: " + reason
            msg_user += "\n\nIf you feel this was unjustified, you may appeal in <#270890866820775946>."
            msg_user += "\n\nThis restriction expires {} {}.".format(unnohelp_time_string, time.tzname[0])
            try:
                await self.bot.send_message(member, msg_user)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await self.bot.say("{} can no longer speak in Assistance Channels.".format(member.mention))
            msg = "🚫 **Timed No-Help**: {} restricted {} until {} | {}#{}".format(issuer.mention, member.mention, unnohelp_time_string, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            else:
                msg += "\nPlease add an explanation below. In the future, it is recommended to use `.timetakehelp <user> <length> [reason]` as the reason is automatically sent to the user."
            await self.bot.send_message(self.bot.modlogs_channel, msg)
            await self.bot.send_message(self.bot.helpers_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("?? I don't have permission to do this.")
            
    @is_staff("Helper")
    @commands.command(pass_context=True, name="takesmallhelp")
    async def takesmallhelp(self, ctx, *, members: str):
        """Remove access to small help channel. Staff and Helpers only."""
        cvr = converters.SafeMember
        meb = [cvr(ctx, x).convert() for x in members.split()]
        for member in meb:
            try:
                await self.bot.remove_roles(member, self.bot.smallhelp_role)
            except discord.errors.Forbidden:
                await self.bot.say("💢 I don't have permission to do this.")
        await self.bot.say("{} can no longer access the small help channel.".format(', '.join([x.mention for x in meb])))
        msg = "⭕️ **Small help access revoked**: {} revoked access to small help channel from {}".format(ctx.message.author.mention,', '.join(["{} | {}#{}".format(x.mention, x.name, x.discriminator) for x in meb]))
        await self.bot.send_message(self.bot.modlogs_channel, msg)
        await self.bot.send_message(self.bot.helpers_channel, msg)
       
    @is_staff("Helper")
    @commands.command(pass_context=True, name="givesmallhelp")
    async def givesmallhelp(self, ctx, *, members: str):
        """Provide access to small help channel for 1-on-1 help. Staff and Helpers only."""
        cvr = converters.SafeMember
        meb = [cvr(ctx, x).convert() for x in members.split()]
        for member in meb:
            try:
                await self.bot.add_roles(member, self.bot.smallhelp_role)
            except discord.errors.Forbidden:
                await self.bot.say("💢 I don't have permission to do this.")
        await self.bot.say("{} can access the small help channel.".format(', '.join([x.mention for x in meb])))
        msg = "⭕️ **Small help access granted**: {} granted access to small help channel to {}".format(ctx.message.author.mention, ', '.join(["{} | {}#{}".format(x.mention, x.name, x.discriminator) for x in meb]))
        await self.bot.send_message(self.bot.modlogs_channel, msg)
        await self.bot.send_message(self.bot.helpers_channel, msg)
            
    @is_staff("Helper")
    @commands.command(pass_context=True, name="probate")
    async def probate(self, ctx, member: converters.SafeMember, *, reason=""):
        """Probate a user. Staff and Helpers only."""
        try:
            await self.add_restriction(member, "Probation")
            await self.bot.add_roles(member, self.bot.probation_role)
            msg_user = "You are under probation!"
            if reason != "":
                msg_user += " The given reason is: " + reason
            try:
                await self.bot.send_message(member, msg_user)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await self.bot.say("{} is now in probation.".format(member.mention))
            msg = "🚫 **Probated**: {} probated {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            else:
                msg += "\nPlease add an explanation below. In the future, it is recommended to use `.probate <user> [reason]` as the reason is automatically sent to the user."
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @is_staff("Helper")
    @commands.command(pass_context=True, name="unprobate")
    async def unprobate(self, ctx, member: converters.SafeMember):
        """Unprobate a user. Staff and Helpers only."""
        try:
            await self.remove_restriction(member, "Probation")
            await self.bot.remove_roles(member, self.bot.probation_role)
            await self.bot.say("{} is out of probation.".format(member.mention))
            msg = "⭕️ **Un-probated**: {} un-probated {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @is_staff("OP")
    @commands.command(pass_context=True)
    async def playing(self, ctx, *gamename):
        """Sets playing message. Staff only."""
        try:
            await self.bot.change_presence(game=discord.Game(name='{}'.format(" ".join(gamename))))
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @is_staff("OP")
    @commands.command(pass_context=True)
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
            await self.bot.say("💢 I don't have permission to do this.")

    @is_staff("OP")
    @commands.command(pass_context=True, hidden=True)
    async def username(self, ctx, *, username):
        """Sets bot name. Staff only."""
        try:
            await self.bot.edit_profile(username=('{}'.format(username)))
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @mute.error
    @timemute.error
    @unmute.error
    @noembed.error
    @embed.error
    @takehelp.error
    @givehelp.error
    @timetakehelp.error
    @takesmallhelp.error
    @givesmallhelp.error
    @probate.error
    @unprobate.error
    async def mod_action_error_handler(self, error, ctx):
        if isinstance(error, commands.errors.BadArgument):
            await self.bot.say(error)

def setup(bot):
    bot.add_cog(Mod(bot))
