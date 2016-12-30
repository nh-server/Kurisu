import discord
import json
import time
from discord.ext import commands
from sys import argv

class ModWarn:
    """
    Warn commands.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True)
    async def warn(self, ctx, user, *, reason=""):
        """Warn a user. Staff only."""
        member = ctx.message.mentions[0]
        issuer = ctx.message.author
        server = ctx.message.author.server
        if self.bot.staff_role in member.roles:
            await self.bot.say("You can't warn another staffer with this command!")
            return
        with open("warns.json", "r") as f:
            warns = json.load(f)
        if member.id not in warns:
            warns[member.id] = {"warns": {}}
        warns[member.id]["name"] = member.name + "#" + member.discriminator
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        warns[member.id]["warns"][len(warns[member.id]["warns"]) + 1] = {"issuer_id": issuer.id, "issuer_name": issuer.name, "reason": reason, "timestamp": timestamp}
        with open("warns.json", "w") as f:
            json.dump(warns, f)
        msg = "You were warned on {}.".format(server.name)
        if reason != "":
            # much \n
            msg += " The given reason is: " + reason
        msg += "\n\nPlease read the rules in #welcome-and-rules. This is warn #{}.".format(len(warns[member.id]["warns"]))
        warn_count = len(warns[member.id]["warns"])
        if warn_count == 2:
            msg += " __The next warn will automatically kick.__"
        if warn_count == 3:
            msg += "\n\nYou were kicked because of this warning. You can join again, but one more warn will result in a ban."
        try:
            await self.bot.send_message(member, msg)
        except discord.errors.Forbidden:
            pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
        if warn_count == 3:
            self.bot.actions.append("wk:"+member.id)
            await self.bot.kick(member)
        if warn_count == 4:
            self.bot.actions.append("wb:"+member.id)
            await self.bot.ban(member)
        await self.bot.say("{} warned.".format(member.mention))
        msg = "⚠️ **Warned**: {} warned {} (warn #{}) | {}#{}".format(issuer.mention, member.mention, len(warns[member.id]["warns"]), member.name, member.discriminator)
        if reason != "":
            # much \n
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.send_message(self.bot.modlogs_channel, msg + ("\nPlease add an explanation below. In the future, it is recommended to use `.warn <user> [reason]` as the reason is automatically sent to the user." if reason == "" else ""))

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True)
    async def listwarns(self, ctx, user):
        """List warns for a user. Staff only."""
        member = ctx.message.mentions[0]
        embed = discord.Embed(color=discord.Color.dark_red())
        embed.set_author(name="Warns for {}#{}".format(member.display_name, member.discriminator), icon_url=member.avatar_url)
        with open("warns.json", "r") as f:
            warns = json.load(f)
        # crappy workaround given how dicts are not ordered
        try:
            warn_count = len(warns[member.id]["warns"])
            if warn_count == 0:
                embed.description = "There are none!"
                embed.color = discord.Color.green()
            else:
                for key in range(warn_count):
                    warn = warns[member.id]["warns"][str(key + 1)]
                    embed.add_field(name="{}: {}".format(key + 1, warn["timestamp"]), value="Issuer: {}\nReason: {}".format(warn["issuer_name"], warn["reason"]))
        except KeyError:  # if the user is not in the file
            embed.description = "There are none!"
            embed.color = discord.Color.green()
        await self.bot.say("", embed=embed)

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True)
    async def clearwarns(self, ctx, user):
        """Clear all warns for a user. Staff only."""
        member = ctx.message.mentions[0]
        with open("warns.json", "r") as f:
            warns = json.load(f)
        if member.id not in warns:
            await self.bot.say("{} has no warns!".format(member.mention))
            return
        warn_count = len(warns[member.id]["warns"])
        if warn_count == 0:
            await self.bot.say("{} has no warns!".format(member.mention))
            return
        warns[member.id] = {"warns": {}}
        with open("warns.json", "w") as f:
            json.dump(warns, f)
        await self.bot.say("{} no longer has any warns!".format(member.mention))
        msg = "🗑 **Cleared warns**: {} cleared {} warns from {} | {}#{}".format(ctx.message.author.mention, warn_count, member.mention, member.name, member.discriminator)
        await self.bot.send_message(self.bot.modlogs_channel, msg)

def setup(bot):
    bot.add_cog(ModWarn(bot))
