import discord
import json
import re
from discord.ext import commands
from subprocess import call
from sys import argv

class Mod:
    """
    Staff commands.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    async def add_restriction(self, member, rst):
        with open("restrictions.json", "r") as f:
            rsts = json.load(f)
        if member.id not in rsts:
            rsts[member.id] = []
        if rst not in rsts[member.id]:
            rsts[member.id].append(rst)
        with open("restrictions.json", "w") as f:
            json.dump(rsts, f)

    async def remove_restriction(self, member, rst):
        with open("restrictions.json", "r") as f:
            rsts = json.load(f)
        if member.id not in rsts:
            rsts[member.id] = []
        if rst in rsts[member.id]:
            rsts[member.id].remove(rst)
        with open("restrictions.json", "w") as f:
            json.dump(rsts, f)

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def quit(self, *gamename):
        """Stops the bot."""
        await self.bot.say("👋 Bye bye!")
        await self.bot.close()

    @commands.has_permissions(manage_server=True)
    @commands.command(hidden=True)
    async def pull(self, *gamename):
        """Pull new changes from GitHub and restart."""
        await self.bot.say("Pulling changes...")
        call(['git', 'pull'])
        await self.bot.say("👋 Restarting bot!")
        await self.bot.close()

    @commands.has_permissions(manage_server=True)
    @commands.command(pass_context=True, hidden=True)
    async def userinfo(self, ctx, user):
        """Gets user info. SuperOP+."""
        u = ctx.message.mentions[0]
        role = u.top_role.name
        if role == "@everyone":
            role = "@ everyone"
        await self.bot.say("name = {}\nid = {}\ndiscriminator = {}\navatar = {}\nbot = {}\navatar_url = {}\ndefault_avatar = {}\ndefault_avatar_url = <{}>\ncreated_at = {}\ndisplay_name = {}\njoined_at = {}\nstatus = {}\ngame = {}\ncolour = {}\ntop_role = {}\n".format(u.name, u.id, u.discriminator, u.avatar, u.bot, u.avatar_url, u.default_avatar, u.default_avatar_url, u.created_at, u.display_name, u.joined_at, u.status, u.game, u.colour, role))

    @commands.has_permissions(administrator=True)
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

    @commands.has_permissions(administrator=True)
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

    @commands.has_permissions(administrator=True)
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

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True, name="clear")
    async def purge(self, ctx, limit: int):
       """Clears a given number of messages. Staff only."""
       try:
           await self.bot.purge_from(ctx.message.channel, limit=limit)
           msg = "🗑 **Cleared**: {} cleared {} messages in {}".format(ctx.message.author.mention, limit, ctx.message.channel.mention)
           await self.bot.send_message(self.bot.modlogs_channel, msg)
       except discord.errors.Forbidden:
           await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True, name="mute")
    async def mute(self, ctx, user, *, reason=""):
        """Mutes a user so they can't speak. Staff only."""
        try:
            member = ctx.message.mentions[0]
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
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True, name="unmute")
    async def unmute(self, ctx, user):
        """Unmutes a user so they can speak. Staff only."""
        try:
            member = ctx.message.mentions[0]
            await self.remove_restriction(member, "Muted")
            await self.bot.remove_roles(member, self.bot.muted_role)
            await self.bot.say("{} can now speak again.".format(member.mention))
            msg = "🔈 **Unmuted**: {} unmuted {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True, name="noembed")
    async def noembed(self, ctx, user, *, reason=""):
        """Removes embed permissions from a user. Staff only."""
        try:
            member = ctx.message.mentions[0]
            await self.add_restriction(member, "No-Embed")
            await self.bot.add_roles(member, self.bot.noembed_role)
            msg_user = "You lost embed and upload permissions!"
            if reason != "":
                msg_user += " The given reason is: " + reason
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

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True, name="embed")
    async def embed(self, ctx, user):
        """Restore embed permissios for a user. Staff only."""
        try:
            member = ctx.message.mentions[0]
            await self.remove_restriction(member, "No-Embed")
            await self.bot.remove_roles(member, self.bot.noembed_role)
            await self.bot.say("{} can now embed links and attach files again.".format(member.mention))
            msg = "⭕️ **Restored Embed**: {} restored embed to {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.command(pass_context=True, name="takehelp")
    async def takehelp(self, ctx, user, *, reason=""):
        """Remove access to help-and-questions. Staff and Helpers only."""
        author = ctx.message.author
        if (self.bot.helpers_role not in author.roles) and (self.bot.staff_role not in author.roles):
            msg = "{} You cannot used this command.".format(author.mention)
            await self.bot.say(msg)
            return
        try:
            member = ctx.message.mentions[0]
            await self.add_restriction(member, "No-Help")
            await self.bot.add_roles(member, self.bot.nohelp_role)
            msg_user = "You lost access to help channels!"
            if reason != "":
                msg_user += " The given reason is: " + reason
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
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.command(pass_context=True, name="givehelp")
    async def givehelp(self, ctx, user):
        """Restore access to help-and-questions. Staff and Helpers only."""
        author = ctx.message.author
        if (self.bot.helpers_role not in author.roles) and (self.bot.staff_role not in author.roles):
            msg = "{} You cannot used this command.".format(author.mention)
            await self.bot.say(msg)
            return
        try:
            member = ctx.message.mentions[0]
            await self.remove_restriction(member, "No-Help")
            await self.bot.remove_roles(member, self.bot.nohelp_role)
            await self.bot.say("{} can access the help channels again.".format(member.mention))
            msg = "⭕️ **Help access restored**: {} restored access to help channels to {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            await self.bot.send_message(self.bot.modlogs_channel, msg)
            await self.bot.send_message(self.bot.helpers_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True, name="probate")
    async def probate(self, ctx, user, *, reason=""):
        """Probate a user. Staff only."""
        try:
            member = ctx.message.mentions[0]
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

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True, name="unprobate")
    async def unprobate(self, ctx, user):
        """Unprobate a user. Staff only."""
        try:
            member = ctx.message.mentions[0]
            await self.remove_restriction(member, "Probation")
            await self.bot.remove_roles(member, self.bot.probation_role)
            await self.bot.say("{} is out of probation.".format(member.mention))
            msg = "⭕️ **Un-probated**: {} un-probated {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(ban_members=True)
    @commands.command(pass_context=True)
    async def playing(self, ctx, *gamename):
        """Sets playing message. Staff only."""
        try:
            await self.bot.change_presence(game=discord.Game(name='{}'.format(" ".join(gamename))))
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(ban_members=True)
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

    @commands.has_permissions(ban_members=True)
    @commands.command(pass_context=True, hidden=True)
    async def username(self, ctx, *, username):
        """Sets bot name. Staff only."""
        try:
            await self.bot.edit_profile(username=('{}'.format(username)))
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

def setup(bot):
    bot.add_cog(Mod(bot))
