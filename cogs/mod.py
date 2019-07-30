import datetime
import re
import time
from subprocess import call
import discord
from discord.ext import commands
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
        await self.bot.close()

    @is_staff("SuperOP")
    @commands.command()
    async def pull(self, ctx):
        """Pull new changes from GitHub and restart."""
        await ctx.send("Pulling changes...")
        call(['git', 'pull'])
        await ctx.send("👋 Restarting bot!")
        await self.bot.close()

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command(hidden=True)
    async def userinfo(self, ctx, u: discord.Member):
        """Gets member info. Staff and Helpers only."""
        role = u.top_role.name
        await ctx.send(f"name = {u.name}\nid = {u.id}\ndiscriminator = {u.discriminator}\navatar = {u.avatar}\nbot = {u.bot}\navatar_url = {u.avatar_url}\ndefault_avatar = {u.default_avatar}\ndefault_avatar_url = <{u.default_avatar_url}>\ncreated_at = {u.created_at}\ndisplay_name = {self.bot.escape_text(u.display_name)}\njoined_at = {u.joined_at}\nstatus = {u.status}\nactivity = {u.activity.name if u.activity else None}\ncolour = {u.colour}\ntop_role = {self.bot.escape_text(role)}\n")

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command(hidden=True)
    async def userinfoid(self, ctx, id):
        """Gets a user id info. Staff and Helpers only."""
        try:
            u = await self.bot.fetch_user(id)
        except discord.NotFound:
            await ctx.send(f"No user matching id `{id}`.")
            return
        await ctx.send(f"name = {u.name}\nid = {u.id}\ndiscriminator = {u.discriminator}\navatar = {u.avatar}\nbot = {u.bot}\navatar_url = {u.avatar_url}\ndefault_avatar_url = <{u.default_avatar_url}>\ncreated_at = {u.created_at}\ncolour = {u.colour}\n")

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command(hidden=True)
    async def matchuser(self, ctx, *, rgx: str):
        """Match users by regex."""
        author = ctx.author
        msg = "```\nmembers:\n"
        for m in self.bot.guild.members:
            if bool(re.search(rgx, m.name, re.IGNORECASE)):
                msg += f"{m.id} - {m}\n"
        msg += "```"
        await author.send(msg)

    @is_staff("Owner")
    @commands.guild_only()
    @commands.command(hidden=True)
    async def multiban(self, ctx, users: commands.Greedy[SafeMember]):
        """Multi-ban users."""
        author = ctx.author
        msg = "```\nbanned:\n"
        for m in users:
            msg += f"{m.id} - {m}\n"
            try:
                await m.ban()
            except discord.errors.NotFound:
                pass
        msg += "```"
        await author.send(msg)

    @is_staff("Owner")
    @commands.guild_only()
    @commands.command(hidden=True)
    async def multibanre(self, ctx, *, rgx: str):
        """Multi-ban users by regex."""
        author = ctx.author
        msg = "```\nbanned:\n"
        toban = []  # because "dictionary changed size during iteration"
        for m in self.bot.guild.members:
            if bool(re.search(rgx, m.name, re.IGNORECASE)):
                msg += f"{m.id} - {m}\n"
                toban.append(m)
        for m in toban:
            try:
                await m.ban()
            except discord.errors.NotFound:
                pass
        msg += "```"
        await author.send(msg)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command(aliases=["clear"])
    async def purge(self, ctx, limit: int):
        """Clears a given number of messages. Staff only."""
        await ctx.channel.purge(limit=limit+1)
        msg = f"🗑 **Cleared**: {ctx.author.mention} cleared {limit} messages in {ctx.channel.mention}"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def mute(self, ctx, member: SafeMember, *, reason=""):
        """Mutes a user so they can't speak. Staff only."""
        if not await self.add_restriction(member.id, self.bot.roles['Muted']):
            await ctx.send("User is already muted!")
            return
        await member.add_roles(self.bot.roles['Muted'])
        msg_user = "You were muted!"
        if reason != "":
            msg_user += " The given reason is: " + reason
        try:
            await member.send(msg_user)
        except discord.errors.Forbidden:
            pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
        await ctx.send(f"{member.mention} can no longer speak.")
        msg = f"🔇 **Muted**: {ctx.author.mention} muted {member.mention} | {member}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        else:
            msg += "\nPlease add an explanation below. In the future, it is recommended to use `.mute <user> [reason]` as the reason is automatically sent to the user."
        await self.bot.channels['mod-logs'].send(msg)
        # change to permanent mute
        await self.remove_timed_restriction(member.id, 'timemute')

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def timemute(self, ctx, member: SafeMember, length, *, reason=""):
        """Mutes a user for a limited period of time so they can't speak. Staff only.\n\nLength format: #d#h#m#s"""

        await self.add_restriction(member.id, self.bot.roles['Muted'])
        await member.add_roles(self.bot.roles['Muted'])
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
        await self.add_timed_restriction(member.id, unmute_time_string, 'timemute')
        await self.add_restriction(member.id, self.bot.roles['Muted'])
        msg_user = "You were muted!"
        if reason != "":
            msg_user += " The given reason is: " + reason
        msg_user += f"\n\nThis mute expires {unmute_time_string} {time.tzname[0]}."
        try:
            await member.send(msg_user)
        except discord.errors.Forbidden:
            pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
        await ctx.send(f"{member.mention} can no longer speak.")
        msg = f"🔇 **Timed mute**: {issuer.mention} muted {member.mention} until {unmute_time_string} | {member}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        else:
            msg += "\nPlease add an explanation below. In the future, it is recommended to use `.timemute <user> <length> [reason]` as the reason is automatically sent to the user."
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def unmute(self, ctx, member: SafeMember):
        """Unmutes a user so they can speak. Staff only."""
        try:
            await self.remove_restriction(member.id, self.bot.roles["Muted"])
            await member.remove_roles(self.bot.roles['Muted'])
            await ctx.send(f"{member.mention} can now speak again.")
            msg = f"🔈 **Unmuted**: {ctx.author.mention} unmuted {member.mention} | {member}"
            await self.bot.channels['mod-logs'].send(msg)
            await self.remove_timed_restriction(member.id, 'timemute')
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.command()
    async def art(self, ctx, member: SafeMember):
        """Restore art-discussion access for a user. Staff only."""
        await self.remove_restriction(member.id , self.bot.roles['no-art'])
        try:
            await member.remove_roles(self.bot.roles['no-art'])
        except discord.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
        await ctx.send(f"{member.mention} can access art-discussion again.")
        msg = f"⭕️ **Restored art**: {ctx.message.author.mention} restored art access to {member.mention} | {member}"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("HalfOP")
    @commands.command()
    async def noart(self, ctx, member: SafeMember, *, reason=""):
        """Removes art-discussion access from a user. Staff only."""
        await self.add_restriction(member.id, self.bot.roles['no-art'])
        try:
            await member.add_roles(self.bot.roles['no-art'])
        except discord.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
        await ctx.send(f"{member.mention} can no longer access art-discussion.")
        msg = f"🚫 **Removed art**: {ctx.message.author.mention} removed art access from {member.mention} | {member}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        else:
            msg += "\nPlease add an explanation below. In the future, it is recommended to use `.noart <user> [reason]` as the reason is automatically sent to the user."
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def elsewhere(self, ctx, member: SafeMember):
        """Restore elsewhere access for a user. Staff only."""
        try:
            await self.remove_restriction(member.id, self.bot.roles["no-elsewhere"])
            await member.remove_roles(self.bot.roles['no-elsewhere'])
            await ctx.send(f"{member.mention} can access elsewhere again.")
            msg = f"⭕️ **Restored elsewhere**: {ctx.author.mention} restored elsewhere access to {member.mention} | {member}"
            await self.bot.channels['mod-logs'].send(msg)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def noelsewhere(self, ctx, member: SafeMember, *, reason=""):
        """Removes elsewhere access from a user. Staff only."""
        try:
            await self.add_restriction(member.id, self.bot.roles['no-elsewhere'])
            await member.add_roles(self.bot.roles['no-elsewhere'])
            await member.remove_roles(self.bot.roles['#elsewhere'])
            await ctx.send(f"{member.mention} can no longer access elsewhere.")
            msg = f"🚫 **Removed elsewhere**: {ctx.author.mention} removed elsewhere access from {member.mention} | {member}"
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            else:
                msg += "\nPlease add an explanation below. In the future, it is recommended to use `.noelsewhere <user> [reason]` as the reason is automatically sent to the user."
            await self.bot.channels['mod-logs'].send(msg)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def noembed(self, ctx, member: SafeMember, *, reason=""):
        """Removes embed permissions from a user. Staff only."""
        try:
            await self.add_restriction(member.id, self.bot.roles['No-Embed'])
            await member.add_roles(self.bot.roles['No-Embed'])
            msg_user = "You lost embed and upload permissions!"
            if reason != "":
                msg_user += " The given reason is: " + reason
            msg_user += "\n\nIf you feel this was unjustified, you may appeal in <#270890866820775946>."
            try:
                await member.send(msg_user)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await ctx.send(f"{member.mention} can no longer embed links or attach files.")
            msg = f"🚫 **Removed Embed**: {ctx.author.mention} removed embed from {member.mention} | {member}"
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            else:
                msg += "\nPlease add an explanation below. In the future, it is recommended to use `.noembed <user> [reason]` as the reason is automatically sent to the user."
            await self.bot.channels['mod-logs'].send(msg)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def embed(self, ctx, member: SafeMember):
        """Restore embed permissios for a user. Staff only."""
        try:
            await self.remove_restriction(member.id, self.bot.roles["No-Embed"])
            await member.remove_roles(self.bot.roles['No-Embed'])
            await ctx.send(f"{member.mention} can now embed links and attach files again.")
            msg = f"⭕️ **Restored Embed**: {ctx.author.mention} restored embed to {member.mention} | {member}"
            await self.bot.channels['mod-logs'].send(msg)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command(aliases=["nohelp"])
    async def takehelp(self, ctx, member: SafeMember, *, reason=""):
        """Remove access to help-and-questions. Staff and Helpers only."""
        await self.add_restriction(member.id, self.bot.roles['No-Help'])
        await member.add_roles(self.bot.roles['No-Help'])
        msg_user = "You lost access to help channels!"
        if reason != "":
            msg_user += " The given reason is: " + reason
        msg_user += "\n\nIf you feel this was unjustified, you may appeal in <#270890866820775946>."
        try:
            await member.send(msg_user)
        except discord.errors.Forbidden:
            pass
        await ctx.send(f"{member.mention} can no longer access the help channels.")
        msg = f"🚫 **Help access removed**: {ctx.author.mention} removed access to help channels from {member.mention} | {member}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        else:
            msg += "\nPlease add an explanation below. In the future, it is recommended to use `.takehelp <user> [reason]` as the reason is automatically sent to the user."
        await self.bot.channels['mod-logs'].send(msg)
        await self.bot.channels['helpers'].send(msg)
        await self.remove_timed_restriction(member.id, 'timenohelp')

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command()
    async def givehelp(self, ctx, member: SafeMember):
        """Restore access to help-and-questions. Staff and Helpers only."""
        try:
            await self.remove_restriction(member.id, self.bot.roles["No-Help"])
            await member.remove_roles(self.bot.roles['No-Help'])
            await ctx.send(f"{member.mention} can access the help channels again.")
            msg = f"⭕️ **Help access restored**: {ctx.author.mention} restored access to help channels to {member.mention} | {member}"
            await self.bot.channels['mod-logs'].send(msg)
            await self.bot.channels['helpers'].send(msg)
            await self.remove_timed_restriction(member.id, 'timenohelp')
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command(aliases=["timenohelp"])
    async def timetakehelp(self, ctx, member: SafeMember, length, *, reason=""):
        """Restricts a user from Assistance Channels for a limited period of time. Staff and Helpers only.\n\nLength format: #d#h#m#s"""

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
        await self.add_timed_restriction(member.id, unnohelp_time_string, 'timenohelp')
        await self.add_restriction(member.id, self.bot.roles['No-Help'])
        await member.add_roles(self.bot.roles['No-Help'])
        msg_user = "You lost access to help channels temporarily!"
        if reason != "":
            msg_user += " The given reason is: " + reason
        msg_user += "\n\nIf you feel this was unjustified, you may appeal in <#270890866820775946>."
        msg_user += f"\n\nThis restriction expires {unnohelp_time_string} {time.tzname[0]}."
        try:
            await member.send(msg_user)
        except discord.errors.Forbidden:
            pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
        await ctx.send(f"{member.mention} can no longer speak in Assistance Channels.")
        msg = f"🚫 **Timed No-Help**: {issuer.mention} restricted {member.mention} until {unnohelp_time_string} | {member}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        else:
            msg += "\nPlease add an explanation below. In the future, it is recommended to use `.timetakehelp <user> <length> [reason]` as the reason is automatically sent to the user."
        await self.bot.channels['mod-logs'].send(msg)
        await self.bot.channels['helpers'].send(msg)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command()
    async def takesmallhelp(self, ctx, members: commands.Greedy[SafeMember]):
        """Remove access to small help channel. Staff and Helpers only."""
        if len(members) < 1:
            await ctx.send("Mention at least one user")
            return
        for member in members:
            await member.remove_roles(self.bot.roles['Small Help'])
        await ctx.send(f"{', '.join([x.mention for x in members])} can no longer access the small help channel.")
        msg = f"⭕️ **Small help access revoked**: {ctx.author.mention} revoked access to small help channel from {', '.join([f'{x.mention} | {x}'for x in members])}"
        await self.bot.channels['mod-logs'].send(msg)
        await self.bot.channels['helpers'].send(msg)
       
    @is_staff("Helper")
    @commands.guild_only()
    @commands.command()
    async def givesmallhelp(self, ctx, members: commands.Greedy[SafeMember]):
        """Provide access to small help channel for 1-on-1 help. Staff and Helpers only."""
        if len(members) < 1:
            await ctx.send("Mention at least one user")
            return
        for member in members:
            await member.add_roles(self.bot.roles['Small Help'])
        await ctx.send(f"{', '.join([x.mention for x in members])} can access the small help channel.")
        msg = f"⭕️ **Small help access granted**: {ctx.author.mention} granted access to small help channel to {', '.join([f'{x.mention} | {x}'for x in members])}"
        await self.bot.channels['mod-logs'].send(msg)
        await self.bot.channels['helpers'].send(msg)
            
    @is_staff("Helper")
    @commands.guild_only()
    @commands.command(name="probate")
    async def probate(self, ctx, member: SafeMember, *, reason=""):
        """Probate a user. Staff and Helpers only."""
        await self.add_restriction(member.id, self.bot.roles['Probation'])
        await member.add_roles(self.bot.roles['Probation'])
        msg_user = "You are under probation!"
        if reason != "":
            msg_user += " The given reason is: " + reason
        try:
            await member.send(msg_user)
        except discord.errors.Forbidden:
            pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
        await ctx.send(f"{member.mention} is now in probation.")
        msg = f"🚫 **Probated**: {ctx.author.mention} probated {member.mention} | {member}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        else:
            msg += "\nPlease add an explanation below. In the future, it is recommended to use `.probate <user> [reason]` as the reason is automatically sent to the user."
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command()
    async def unprobate(self, ctx, member: SafeMember):
        """Unprobate a user. Staff and Helpers only."""
        await self.remove_restriction(member.id, self.bot.roles["Probation"])
        await member.remove_roles(self.bot.roles['Probation'])
        await ctx.send(f"{member.mention} is out of probation.")
        msg = f"⭕️ **Un-probated**: {ctx.author.mention} un-probated {member.mention} | {member}"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("OP")
    @commands.command()
    async def playing(self, ctx, *gamename):
        """Sets playing message. Staff only."""
        await self.bot.change_presence(activity=discord.Game(name=f'{" ".join(gamename)}'))

    @is_staff("OP")
    @commands.command()
    async def status(self, ctx, status):
        """Sets status. Staff only."""
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

    @is_staff("OP")
    @commands.command(hidden=True)
    async def username(self, ctx, *, username):
        """Sets bot name. Staff only."""
        await self.bot.user.edit(username=f'{username}')

    @is_staff("SuperOP")
    @commands.guild_only()
    @commands.command(hidden=True)
    async def nofilter(self, ctx, channel: discord.TextChannel):
        """Adds nofilter to the channel"""
        await self.add_nofilter(channel)
        await self.bot.channels['mod-logs'].send(f"⭕ **No filter**: {ctx.author.mention} added no filter to {channel.mention}")

    @is_staff("SuperOP")
    @commands.guild_only()
    @commands.command(hidden=True)
    async def filter(self, ctx, channel: discord.TextChannel):
        """Removes nofilter from the channel"""
        await self.remove_nofilter(channel)
        await self.bot.channels['mod-logs'].send(f"🚫 **Filter**: {ctx.author.mention} removed no filter from {channel.mention}")

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command(hidden=True)
    async def approve(self, ctx, invite: discord.Invite, times: int=1):
        """Approves a server invite for a number of times"""
        code = invite.code
        self.bot.temp_guilds[code] = times
        await ctx.send(f"Approved an invite to {invite.guild}({code}) for posting {times} times")
        await self.bot.channels['mod-logs'].send(f"🚫 **Approved**: {ctx.author.mention} approved server {invite.guild}({code}) to be posted {times} times")


def setup(bot):
    bot.add_cog(Mod(bot))
