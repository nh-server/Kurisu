import discord
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

    @commands.has_permissions(administrator=True)
    @commands.command(pass_context=True, hidden=True)
    async def userinfo(self, ctx, user):
        """Gets user info. Owners only."""
        u = ctx.message.mentions[0]
        role = u.top_role.name
        if role == "@everyone":
            role = "@ everyone"
        await self.bot.say("name = {}\nid = {}\ndiscriminator = {}\navatar = {}\nbot = {}\navatar_url = {}\ndefault_avatar = {}\ndefault_avatar_url = <{}>\ncreated_at = {}\ndisplay_name = {}\njoined_at = {}\nstatus = {}\ngame = {}\ncolour = {}\ntop_role = {}\n".format(u.name, u.id, u.discriminator, u.avatar, u.bot, u.avatar_url, u.default_avatar, u.default_avatar_url, u.created_at, u.display_name, u.joined_at, u.status, u.game, u.colour, role))

    @commands.has_permissions(administrator=True)
    @commands.command(pass_context=True, hidden=True)
    async def matchuser(self, ctx, *, rgx: str):
        """Match users by regex."""
        server = ctx.message.server
        author = ctx.message.author
        msg = "```\nmembers:\n"
        for m in server.members:
            if bool(re.search(rgx, m.name, re.IGNORECASE)):
                msg += "{} - {}#{}\n".format(m.id, m.name, m.discriminator)
        msg += "```"
        await self.bot.send_message(author, msg)

    @commands.has_permissions(administrator=True)
    @commands.command(pass_context=True, hidden=True)
    async def multiban(self, ctx, *, members: str):
        """Multi-ban users."""
        server = ctx.message.server
        author = ctx.message.author
        msg = "```\nbanned:\n"
        for m in ctx.message.mentions:
            msg += "{} - {}#{}\n".format(m.id, m.name, m.discriminator)
            await self.bot.ban(m, 7)
        msg += "```"
        await self.bot.send_message(author, msg)

    @commands.has_permissions(administrator=True)
    @commands.command(pass_context=True, hidden=True)
    async def multibanre(self, ctx, *, rgx: str):
        """Multi-ban users by regex."""
        server = ctx.message.server
        author = ctx.message.author
        msg = "```\nbanned:\n"
        toban = []  # because "dictionary changed size during iteration"
        for m in server.members:
            if bool(re.search(rgx, m.name, re.IGNORECASE)):
                msg += "{} - {}#{}\n".format(m.id, m.name, m.discriminator)
                toban.append(m)
        for m in toban:
            await self.bot.ban(m)
        msg += "```"
        await print(self.bot.send_message(author, msg))

    @commands.has_permissions(manage_messages=True)
    @commands.command(pass_context=True, name="clear")
    async def purge(self, ctx, limit: int):
       """Clears a given number of messages. Staff only."""
       try:
           await self.bot.purge_from(ctx.message.channel, limit=limit)
           msg = "🗑 **Cleared**: {0} cleared {1} messages in {2}".format(ctx.message.author.mention, limit, ctx.message.channel.mention)
           await self.bot.send_message(discord.utils.get(ctx.message.server.channels, name="mod-logs"), msg)
       except discord.errors.Forbidden:
           await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True, name="kick")
    async def kick_member(self, ctx, user, *, reason=""):
        """Kicks a user from the server. Staff only."""
        try:
            member = ctx.message.mentions[0]
            server = ctx.message.author.server
            msg = "You were kicked from {0}.".format(server.name)
            if reason != "":
                # much \n
                msg += " The given reason is: " + reason
            msg += "\n\nYou are able to rejoin the server, but please read the rules in #welcome before participating again."
            await self.bot.send_message(member, msg)
            await self.bot.kick(member)
            await self.bot.say("{0} is now gone. 👌".format(member))
            msg = "👢 **Kick**: {0} kicked {1} | {2}#{3}".format(ctx.message.author.mention, member.mention, member.name, member.discriminator)
            if reason != "":
                # much \n
                msg += "\n✏️ __Reason__: " + reason
            await self.bot.send_message(discord.utils.get(server.channels, name="server-logs"), msg)
            await self.bot.send_message(discord.utils.get(server.channels, name="mod-logs"), msg + ("\nPlease add an explanation below. In the future, it is recommended to use `.kick <user> [reason]`." if reason == "" else ""))
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True, name="mute")
    async def mute(self, ctx, user):
        """Mutes a user so they can't speak. Staff only."""
        try:
            member = ctx.message.mentions[0]
            server = ctx.message.author.server
            await self.bot.add_roles(member, discord.utils.get(server.roles, name="Muted"))
            await self.bot.say("{0} can no longer speak.".format(member.mention))
            msg = "🔇 **Muted**: {0} muted {1} | {2}#{3}".format(ctx.message.author.mention, member.mention, member.name, member.discriminator)
            await self.bot.send_message(discord.utils.get(server.channels, name="mod-logs"), msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True, name="unmute")
    async def unmute(self, ctx, user):
        """Unmutes a user so they can speak. Staff only."""
        try:
            member = ctx.message.mentions[0]
            server = ctx.message.author.server
            await self.bot.remove_roles(member, discord.utils.get(server.roles, name="Muted"))
            await self.bot.say("{0} can now speak again.".format(member.mention))
            msg = "🔈 **Unmuted**: {0} unmuted {1} | {2}#{3}".format(ctx.message.author.mention, member.mention, member.name, member.discriminator)
            await self.bot.send_message(discord.utils.get(server.channels, name="mod-logs"), msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True, name="noembed")
    async def noembed(self, ctx, user):
        """Removes embed permissions from a user. Staff only."""
        try:
            member = ctx.message.mentions[0]
            server = ctx.message.author.server
            await self.bot.add_roles(member, discord.utils.get(server.roles, name="No-Embed"))
            await self.bot.say("{0} can no longer embed links or attach files.".format(member.mention))
            msg = "🚫 **Removed Embed**: {0} removed embed from {1} | {2}#{3}".format(ctx.message.author.mention, member.mention, member.name, member.discriminator)
            await self.bot.send_message(discord.utils.get(server.channels, name="mod-logs"), msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True, name="embed")
    async def embed(self, ctx, user):
        """Restore embed permissios for a user. Staff only."""
        try:
            member = ctx.message.mentions[0]
            server = ctx.message.author.server
            await self.bot.remove_roles(member, discord.utils.get(server.roles, name="No-Embed"))
            await self.bot.say("{0} can now embed links and attach files again.".format(member.mention))
            msg = "⭕️ **Restored Embed**: {0} restored embed to {1} | {2}#{3}".format(ctx.message.author.mention, member.mention, member.name, member.discriminator)
            await self.bot.send_message(discord.utils.get(server.channels, name="mod-logs"), msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.command(pass_context=True, name="takehelp")
    async def takehelp(self, ctx, user):
        """Remove access to help-and-questions. Staff and Helpers only."""
        helpers_role = discord.utils.get(ctx.message.server.roles, name="Helpers")
        staff_role = discord.utils.get(ctx.message.server.roles, name="Staff")
        author = ctx.message.author
        if (helpers_role not in author.roles) and (staff_role not in author.roles):
            msg = "{0} You cannot used this command.".format(author.mention)
            await self.bot.say(msg)
            return
        try:
            member = ctx.message.mentions[0]
            server = ctx.message.author.server
            await self.bot.add_roles(member, discord.utils.get(server.roles, name="No Help"))
            await self.bot.say("{0} can no longer give or get help.".format(member.mention))
            msg = "🚫 **Help access removed**: {0} removed access to h&q from {1} | {2}#{3}".format(ctx.message.author.mention, member.mention, member.name, member.discriminator)
            await self.bot.send_message(discord.utils.get(server.channels, name="mod-logs"), msg)
            await self.bot.send_message(discord.utils.get(server.channels, name="helpers"), msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.command(pass_context=True, name="givehelp")
    async def give(self, ctx, user):
        """Restore access to help-and-questions. Staff and Helpers only."""
        helpers_role = discord.utils.get(ctx.message.server.roles, name="Helpers")
        staff_role = discord.utils.get(ctx.message.server.roles, name="Staff")
        author = ctx.message.author
        if (helpers_role not in author.roles) and (staff_role not in author.roles):
            msg = "{0} You cannot used this command.".format(author.mention)
            await self.bot.say(msg)
            return
        try:
            member = ctx.message.mentions[0]
            server = ctx.message.author.server
            await self.bot.remove_roles(member, discord.utils.get(server.roles, name="No Help"))
            await self.bot.say("{0} can give or get help again.".format(member.mention))
            msg = "⭕️ **Help access restored**: {0} restored access to h&q from {1} | {2}#{3}".format(ctx.message.author.mention, member.mention, member.name, member.discriminator)
            await self.bot.send_message(discord.utils.get(server.channels, name="mod-logs"), msg)
            await self.bot.send_message(discord.utils.get(server.channels, name="helpers"), msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(ban_members=True)
    @commands.command(pass_context=True)
    async def playing(self, ctx, *gamename):
        """Sets playing message. Staff only."""
        try:
            await self.bot.change_presence(game=discord.Game(name='{0}'.format(" ".join(gamename))))
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
            await self.bot.edit_profile(username=('{0}'.format(username)))
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

def setup(bot):
    bot.add_cog(Mod(bot))
