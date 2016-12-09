import discord
import json
import time
from discord.ext import commands
from sys import argv

# TODO: list warnings
# TODO: clear warnings

class ModWarn:
    """
    Warn commands.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    @commands.command(hidden=True, pass_context=True)
    async def wtest(self, ctx, usr):
        print(ctx.message.mentions)
        mention = ctx.message.mentions[0]
        await self.bot.say(mention.id + " " + mention.name)

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True)
    async def warn(self, ctx, user, *, reason=""):
        """Warn a user. Staff only."""
        member = ctx.message.mentions[0]
        issuer = ctx.message.author
        server = ctx.message.author.server
        with open("warns.json", "r") as f:
            warns = json.load(f)
        if member.id not in warns:
            warns[member.id] = {"warns": {}}
        warns[member.id]["name"] = member.name + "#" + member.discriminator
        # 2015-12-28 05:37:55.743000
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S.%f", time.localtime())
        warns[member.id]["warns"][len(warns[member.id]["warns"])] = {"issuer_id": issuer.id, "reason": reason, "timestamp": timestamp}
        with open("warns.json", "w") as f:
            json.dump(warns, f)
        #await self.bot.say(json.dumps(warns))
        msg = "You were warned on {}.".format(server.name)
        if reason != "":
            # much \n
            msg += " The given reason is: " + reason
        msg += "\n\nPlease read the rules in #welcome-and-rules. This is warn #{}.".format(len(warns[member.id]["warns"]))
        await self.bot.send_message(member, msg)
        await self.bot.say("{} warned.".format(member))
        msg = "⚠️ **Warned**: {} warned {} (warn #{}) | {}#{}".format(issuer.mention, member.mention, len(warns[member.id]["warns"]), member.name, member.discriminator)
        if reason != "":
            # much \n
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.send_message(discord.utils.get(server.channels, name="mod-logs"), msg + ("\nPlease add an explanation below. In the future, it is recommended to use `.warn <user> [reason]` as the reason is automatically sent to the user." if reason == "" else ""))

def setup(bot):
    bot.add_cog(ModWarn(bot))
