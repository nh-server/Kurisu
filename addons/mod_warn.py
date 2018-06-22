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

    @commands.command(pass_context=True)
    async def warn(self, ctx, user, *, reason=""):
        """Warn a user. Staff and Helpers only."""
        issuer = ctx.message.author
        if (self.bot.helpers_role not in issuer.roles) and (self.bot.staff_role not in issuer.roles):
            msg = "{0} This command is limited to Staff and Helpers.".format(issuer.mention)
            await self.bot.say(msg)
            return
        try:
            member = ctx.message.mentions[0]
        except IndexError:
            await self.bot.say("Please mention a user.")
            return
        if self.bot.staff_role in member.roles:
            await self.bot.say("You can't warn another staffer with this command!")
            return
        with open("data/warnsv2.json", "r") as f:
            warns = json.load(f)
        if member.id not in warns:
            warns[member.id] = {"warns": []}
        warns[member.id]["name"] = member.name + "#" + member.discriminator
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        warns[member.id]["warns"].append({"issuer_id": issuer.id, "issuer_name": issuer.name, "reason": reason, "timestamp": timestamp})
        with open("data/warnsv2.json", "w") as f:
            json.dump(warns, f)
        msg = "You were warned on {}.".format(self.bot.server.name)
        if reason != "":
            # much \n
            msg += " The given reason is: " + reason
        msg += "\n\nPlease read the rules in #welcome-and-rules. This is warn #{}.".format(len(warns[member.id]["warns"]))
        warn_count = len(warns[member.id]["warns"])
        if warn_count == 2:
            msg += " __The next warn will automatically kick.__"
        if warn_count == 3:
            msg += "\n\nYou were kicked because of this warning. You can join again right away. Two more warnings will result in an automatic ban."
        if warn_count == 4:
            msg += "\n\nYou were kicked because of this warning. This is your final warning. You can join again, but **one more warn will result in a ban**."
        if warn_count == 5:
            msg += "\n\nYou were automatically banned due to five warnings."
        try:
            await self.bot.send_message(member, msg)
        except discord.errors.Forbidden:
            pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
        if warn_count == 3 or warn_count == 4:
            self.bot.actions.append("wk:"+member.id)
            await self.bot.kick(member)
        if warn_count >= 5:  # just in case
            self.bot.actions.append("wb:"+member.id)
            await self.bot.ban(member, 0)
        await self.bot.say("{} warned. User has {} warning(s)".format(member.mention, len(warns[member.id]["warns"])))
        msg = "⚠️ **Warned**: {} warned {} (warn #{}) | {}#{}".format(issuer.mention, member.mention, len(warns[member.id]["warns"]), member.name, member.discriminator)
        if reason != "":
            # much \n
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.send_message(self.bot.modlogs_channel, msg + ("\nPlease add an explanation below. In the future, it is recommended to use `.warn <user> [reason]` as the reason is automatically sent to the user." if reason == "" else ""))

    @commands.command(pass_context=True)
    async def listwarns(self, ctx, user: discord.Member = None):
        """List warns for a user. Staff and Helpers only."""
        if not user: # If user is set to None, its a selfcheck
            user = ctx.message.author
        issuer = ctx.message.author
        if (self.bot.helpers_role not in issuer.roles) and (self.bot.staff_role not in issuer.roles):
            msg = "{0} This command is limited to Staff and Helpers.".format(issuer.mention)
            await self.bot.say(msg)
            return
        member = user # A bit sloppy but its to reduce the amount of work needed to change below.
        embed = discord.Embed(color=discord.Color.dark_red())
        embed.set_author(name="Warns for {}#{}".format(member.display_name, member.discriminator), icon_url=member.avatar_url)
        with open("data/warnsv2.json", "r") as f:
            warns = json.load(f)
        # crappy workaround given how dicts are not ordered
        try:
            if len(warns[member.id]["warns"]) == 0:
                embed.description = "There are none!"
                embed.color = discord.Color.green()
            else:
                for idx, warn in enumerate(warns[member.id]["warns"]):
                    value = ""
                    if ctx.message.channel == self.bot.helpers_channel or ctx.message.channel == self.bot.mods_channel:
                        value += "Issuer: " + warn["issuer_name"] + "\n"
                    value += "Reason: " + warn["reason"] + " "
                    # embed.add_field(name="{}: {}".format(key + 1, warn["timestamp"]), value="Issuer: {}\nReason: {}".format(warn["issuer_name"], warn["reason"]))
                    embed.add_field(name="{}: {}".format(idx + 1, warn["timestamp"]), value=value)
        except KeyError:  # if the user is not in the file
            embed.description = "There are none!"
            embed.color = discord.Color.green()
        await self.bot.say("", embed=embed)

    @commands.command(pass_context=True)
    async def listwarnsid(self, ctx, user_id):
        """List warns for a user based on ID. Staff and Helpers only."""
        issuer = ctx.message.author
        if (self.bot.helpers_role not in issuer.roles) and (self.bot.staff_role not in issuer.roles):
            msg = "{0} This command is limited to Staff and Helpers.".format(issuer.mention)
            await self.bot.say(msg)
            return
        embed = discord.Embed(color=discord.Color.dark_red())
        with open("data/warnsv2.json", "r") as f:
            warns = json.load(f)
        # crappy workaround given how dicts are not ordered
        try:
            embed.set_author(name="Warns for {}".format(warns[user_id]["name"]))
            if len(warns[user_id]["warns"]) == 0:
                embed.description = "There are none!"
                embed.color = discord.Color.green()
            else:
                for idx, warn in enumerate(warns[user_id]["warns"]):
                    value = ""
                    if ctx.message.channel == self.bot.helpers_channel or ctx.message.channel == self.bot.mods_channel:
                        value += "Issuer: " + warn["issuer_name"] + "\n"
                    value += "Reason: " + warn["reason"] + " "
                    # embed.add_field(name="{}: {}".format(key + 1, warn["timestamp"]), value="Issuer: {}\nReason: {}".format(warn["issuer_name"], warn["reason"]))
                    embed.add_field(name="{}: {}".format(idx + 1, warn["timestamp"]), value=value)
        except KeyError:  # if the user is not in the file
            embed.set_author(name="Warns for {}".format(user_id))
            embed.description = "ID doesn't exist in saved warnings."
            embed.color = discord.Color.green()
        await self.bot.say("", embed=embed)

    @commands.has_permissions(manage_server=True)
    @commands.command(pass_context=True)
    async def copywarns_id2id(self, ctx, user_id1, user_id2):
        """Copy warns from one user ID to another. Overwrites all warns of the target user ID. Staff only."""
        with open("data/warnsv2.json", "r") as f:
            warns = json.load(f)
        if user_id1 not in warns:
            await self.bot.say("{} doesn't exist in saved warnings.".format(user_id1))
            return
        warn_count = len(warns[user_id1]["warns"])
        if warn_count == 0:
            await self.bot.say("{} has no warns!".format(warns[user_id1]["name"]))
            return
        warns1 = warns[user_id1]
        if user_id2 not in warns:
            warns[user_id2] = []
        warns2 = warns[user_id2]
        if "name" not in warns2:
            orig_name = ""
            warns2["name"] = "(copied from {})".format(warns1["name"])
        else:
            orig_name = warns2["name"]
            warns2["name"] = "{} (copied from {})".format(warns2["name"], warns1["name"])
        warns2["warns"] = warns1["warns"]
        with open("data/warnsv2.json", "w") as f:
            json.dump(warns, f)
        await self.bot.say("{} warns were copied from {} to {}!".format(warn_count, user_id1, user_id2))
        msg = "📎 **Copied warns**: {} copied {} warns from {} ({}) to ".format(ctx.message.author.mention, warn_count, warns1["name"], user_id1)
        if orig_name:
            msg += "{} ({})".format(warns2["name"], user_id2)
        else:
            msg += user_id2
        await self.bot.send_message(self.bot.modlogs_channel, msg)

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True)
    async def delwarn(self, ctx, user, idx: int):
        """Remove a specific warn from a user. Staff only."""
        try:
            member = ctx.message.mentions[0]
        except IndexError:
            await self.bot.say("Please mention a user.")
            return
        with open("data/warnsv2.json", "r") as f:
            warns = json.load(f)
        if member.id not in warns:
            await self.bot.say("{} has no warns!".format(member.mention))
            return
        warn_count = len(warns[member.id]["warns"])
        if warn_count == 0:
            await self.bot.say("{} has no warns!".format(member.mention))
            return
        if idx > warn_count:
            await self.bot.say("Warn index is higher than warn count ({})!".format(warn_count))
            return
        if idx < 1:
            await self.bot.say("Warn index is below 1!")
            return
        warn = warns[member.id]["warns"][idx - 1]
        embed = discord.Embed(color=discord.Color.dark_red(), title="Warn {} on {}".format(idx, warn["timestamp"]),
                              description="Issuer: {0[issuer_name]}\nReason: {0[reason]}".format(warn))
        del warns[member.id]["warns"][idx - 1]
        with open("data/warnsv2.json", "w") as f:
            json.dump(warns, f)
        await self.bot.say("{} has a warning removed!".format(member.mention))
        msg = "🗑 **Deleted warn**: {} removed warn {} from {} | {}#{}".format(ctx.message.author.mention, idx, member.mention, member.name, member.discriminator)
        await self.bot.send_message(self.bot.modlogs_channel, msg, embed=embed)

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True)
    async def delwarnid(self, ctx, user_id, idx: int):
        """Remove a specific warn from a user based on ID. Staff only."""
        with open("data/warnsv2.json", "r") as f:
            warns = json.load(f)
        if user_id not in warns:
            await self.bot.say("{} doesn't exist in saved warnings.".format(user_id))
            return
        warn_count = len(warns[user_id]["warns"])
        if warn_count == 0:
            await self.bot.say("{} has no warns!".format(warns[user_id]["name"]))
            return
        if idx > warn_count:
            await self.bot.say("Warn index is higher than warn count ({})!".format(warn_count))
            return
        if idx < 1:
            await self.bot.say("Warn index is below 1!")
            return
        warn = warns[user_id]["warns"][idx - 1]
        embed = discord.Embed(color=discord.Color.dark_red(), title="Warn {} on {}".format(idx, warn["timestamp"]),
                              description="Issuer: {0[issuer_name]}\nReason: {0[reason]}".format(warn))
        del warns[user_id]["warns"][idx - 1]
        with open("data/warnsv2.json", "w") as f:
            json.dump(warns, f)
        await self.bot.say("{} has a warning removed!".format(warns[user_id]["name"]))
        msg = "🗑 **Deleted warn**: {} removed warn {} from {} ({})".format(ctx.message.author.mention, idx, warns[user_id]["name"], user_id)
        await self.bot.send_message(self.bot.modlogs_channel, msg, embed=embed)

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True)
    async def clearwarns(self, ctx, user):
        """Clear all warns for a user. Staff only."""
        try:
            member = ctx.message.mentions[0]
        except IndexError:
            await self.bot.say("Please mention a user.")
            return
        with open("data/warnsv2.json", "r") as f:
            warns = json.load(f)
        if member.id not in warns:
            await self.bot.say("{} has no warns!".format(member.mention))
            return
        warn_count = len(warns[member.id]["warns"])
        if warn_count == 0:
            await self.bot.say("{} has no warns!".format(member.mention))
            return
        warns[member.id]["warns"] = []
        with open("data/warnsv2.json", "w") as f:
            json.dump(warns, f)
        await self.bot.say("{} no longer has any warns!".format(member.mention))
        msg = "🗑 **Cleared warns**: {} cleared {} warns from {} | {}#{}".format(ctx.message.author.mention, warn_count, member.mention, member.name, member.discriminator)
        await self.bot.send_message(self.bot.modlogs_channel, msg)

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True)
    async def clearwarnsid(self, ctx, user_id):
        """Clear all warns for a user based on ID. Staff only."""
        with open("data/warnsv2.json", "r") as f:
            warns = json.load(f)
        if user_id not in warns:
            await self.bot.say("{} doesn't exist in saved warnings.".format(user_id))
            return
        warn_count = len(warns[user_id]["warns"])
        if warn_count == 0:
            await self.bot.say("{} has no warns!".format(warns[user_id]["name"]))
            return
        warns[user_id]["warns"] = []
        with open("data/warnsv2.json", "w") as f:
            json.dump(warns, f)
        await self.bot.say("{} no longer has any warns!".format(warns[user_id]["name"]))
        msg = "🗑 **Cleared warns**: {} cleared {} warns from {} ({})".format(ctx.message.author.mention, warn_count, warns[user_id]["name"], user_id)
        await self.bot.send_message(self.bot.modlogs_channel, msg)

def setup(bot):
    bot.add_cog(ModWarn(bot))
