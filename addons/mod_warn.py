import discord
from discord.ext import commands
from sys import argv

# this thing doesn't work yet

class ModWarn:
    """
    Warn commands.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True, name="kick")
    async def kick_member(self, ctx, user, *, reason=""):
        """Warn a user. Staff only."""
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

def setup(bot):
    bot.add_cog(ModWarn(bot))
