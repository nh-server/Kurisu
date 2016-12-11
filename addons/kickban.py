import discord
from discord.ext import commands
from sys import argv

class KickBan:
    """
    Kicking and banning users.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

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
            msg += "\n\nYou are able to rejoin the server, but please read the rules in #welcome-and-rules before participating again."
            try:
                await self.bot.send_message(member, msg)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            self.bot.actions.append("uk:"+member.id)
            await self.bot.kick(member)
            await self.bot.say("{0} is now gone. 👌".format(member))
            msg = "👢 **Kick**: {0} kicked {1} | {2}#{3}".format(ctx.message.author.mention, member.mention, member.name, member.discriminator)
            if reason != "":
                # much \n
                msg += "\n✏️ __Reason__: " + reason
            await self.bot.send_message(discord.utils.get(server.channels, name="server-logs"), msg)
            await self.bot.send_message(discord.utils.get(server.channels, name="mod-logs"), msg + ("\nPlease add an explanation below. In the future, it is recommended to use `.kick <user> [reason]` as the reason is automatically sent to the user." if reason == "" else ""))
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

def setup(bot):
    bot.add_cog(KickBan(bot))
