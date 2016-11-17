#Importing libraries
import discord
from discord.ext import commands
from sys import argv

class Mod:
    """
    Staff commands.
    """
    def __init__(self, bot):
        self.bot = bot
    print('Addon "Mod" has been loaded.')

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def quit(self, *gamename):
        """Stops the bot."""
        await self.bot.say("👋 Bye bye!")
        await self.bot.close()

    @commands.has_permissions(manage_messages=True)
    @commands.command(pass_context=True, name="clear")
    async def purge(self, ctx, limit: int):
       """Clears a given number of messages. Staff only."""
       try:
           await self.bot.purge_from(ctx.message.channel, limit=limit)
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

    @commands.has_permissions(ban_members=True)
    @commands.command(pass_context=True)
    async def playing(self, ctx, *gamename):
        """Sets playing message. Staff only."""
        try:
            await self.bot.change_status(game=discord.Game(name='{0}'.format(" ".join(gamename))))
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
