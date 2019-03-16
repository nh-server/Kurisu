import datetime
import discord
import json
import re
import time
from discord.ext import commands
from addons import converters
from addons.checks import is_staff, check_staff


@commands.guild_only()
class KickBan(commands.Cog):
    """
    Kicking and banning users.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    async def meme(self, beaner, beaned, action, channel, reason):
        await channel.send("Seriously? What makes you think it's okay to try and {} another staff or helper like that?".format(action))
        msg = "{} attempted to {} {}|{}#{} in {} ".format(beaner.mention, action, beaned.mention,
                                                                  self.bot.escape_name(beaned.name),
                                                                  beaned.discriminator, channel.mention)
        if reason != "":
            msg += "for the reason " + reason
        await self.bot.meta_channel.send(msg + (" without a reason" if reason == "" else ""))


    @is_staff("HalfOP")
    @commands.command(name="kick")
    async def kick_member(self, ctx, member: converters.SafeMember, *, reason=""):
        """Kicks a user from the server. Staff only."""
        if check_staff(member.id, 'Helper'):
            await self.meme(ctx.author, member, "kick", ctx.channel, reason)
            return
        msg = "You were kicked from {}.".format(ctx.guild.name)
        if reason != "":
            msg += " The given reason is: " + reason
        msg += "\n\nYou are able to rejoin the server, but please read the rules in #welcome-and-rules before participating again."
        try:
            await member.send(msg)
        except discord.errors.Forbidden:
            pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
        self.bot.actions.append("uk:"+str(member.id))
        try:
            await member.kick()
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
        await ctx.send("{} is now gone. 👌".format(self.bot.help_command.remove_mentions(member.name)))
        msg = "👢 **Kick**: {} kicked {} | {}#{}\n🏷 __User ID__: {}".format(ctx.author.mention, member.mention, self.bot.escape_name(member.name), member.discriminator, member.id)
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.serverlogs_channel.send(msg)
        await self.bot.modlogs_channel.send(msg + ("\nPlease add an explanation below. In the future, it is recommended to use `.kick <user> [reason]` as the reason is automatically sent to the user." if reason == "" else ""))


    @is_staff("OP")
    @commands.command(name="ban")
    async def ban_member(self, ctx, member: converters.SafeMember, *, reason=""):
        """Bans a user from the server. OP+ only."""
        if check_staff(member.id, 'Helper'):
            await self.meme(ctx.author, member, "ban", ctx.channel, reason)
            return
        msg = "You were banned from {}.".format(ctx.guild.name)
        if reason != "":
            msg += " The given reason is: " + reason
        msg += "\n\nThis ban does not expire."
        try:
            await member.send(msg)
        except discord.errors.Forbidden:
            pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
        self.bot.actions.append("ub:"+str(member.id))
        try:
            await member.ban()
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
        await ctx.send("{} is now b&. 👍".format(self.bot.help_command.remove_mentions(member)))
        msg = "⛔ **Ban**: {} banned {} | {}#{}\n🏷 __User ID__: {}".format(ctx.author.mention, member.mention, self.bot.escape_name(member.name), member.discriminator, member.id)
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.serverlogs_channel.send(msg)
        await self.bot.modlogs_channel.send(msg + ("\nPlease add an explanation below. In the future, it is recommended to use `.ban <user> [reason]` as the reason is automatically sent to the user." if reason == "" else ""))

    @is_staff("OP")
    @commands.command(name="banid")
    async def banid_member(self, ctx, userid: str, *, reason=""):
        """Bans a user id from the server. OP+ only."""
        try:
            user = await self.bot.get_user_info(userid)
        except discord.errors.NotFound:
            await ctx.send("No user associated with ID {}.".format(user.id))
        if check_staff(user.id, 'Helper'):
            await ctx.send("You can't ban another staffer with this command!")
            return
        self.bot.actions.append("ub:" + user.id)
        try:
            await user.ban()
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
        await ctx.send("ID {} is now b&. 👍".format(user.id))
        msg = "⛔ **Ban**: {} banned ID {}".format(ctx.author.mention, user.id)
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.serverlogs_channel.send(msg)
        await self.bot.modlogs_channel.send(msg + (
            "\nPlease add an explanation below. In the future, it is recommended to use `.banid <userid> [reason]` as the reason is automatically sent to the user." if reason == "" else ""))


    @is_staff("OP")
    @commands.command(name="silentban", hidden=True)
    async def silentban_member(self, ctx, member: converters.SafeMember, *, reason=""):
        """Bans a user from the server, without a notification. OP+ only."""
        if check_staff(member.id, 'Helper'):
            await self.meme(ctx.author, member, "ban", ctx.channel, reason)
            return
        self.bot.actions.append("ub:"+str(member.id))
        try:
            await member.ban()
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
        await ctx.send("{} is now b&. 👍".format(self.bot.escape_name(member)))
        msg = "⛔ **Silent ban**: {} banned {} | {}#{}\n🏷 __User ID__: {}".format(ctx.author.mention, member.mention, self.bot.escape_name(member.name), member.discriminator, member.id)
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.serverlogs_channel.send(msg)
        await self.bot.modlogs_channel.send(msg + ("\nPlease add an explanation below. In the future, it is recommended to use `.silentban <user> [reason]`." if reason == "" else ""))

    @is_staff("OP")
    @commands.command(name="timeban")
    async def timeban_member(self, ctx, member: converters.SafeMember, length, *, reason=""):
        """Bans a user for a limited period of time. OP+ only.\n\nLength format: #d#h#m#s"""
        if check_staff(member.id, 'Helper'):
            await self.meme(ctx.author, member, "timeban", ctx.channel, reason)
            return
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
        unban_time = timestamp + delta
        unban_time_string = unban_time.strftime("%Y-%m-%d %H:%M:%S")
        with open("data/timebans.json", "r") as f:
            timebans = json.load(f)
        timebans[member.id] = unban_time_string
        self.bot.timebans[member.id] = [member, unban_time, False]  # last variable is "notified", for <=30 minute notifications
        with open("data/timebans.json", "w") as f:
            json.dump(timebans, f)
        msg = "You were banned from {}.".format(ctx.guild.name)
        if reason != "":
            msg += " The given reason is: " + reason
        msg += "\n\nThis ban expires {} {}.".format(unban_time_string, time.tzname[0])
        try:
            await member.send(msg)
        except discord.errors.Forbidden:
            pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
        self.bot.actions.append("ub:"+str(member.id))
        try:
            await member.ban()
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
        await ctx.send("{} is now b& until {} {}. 👍".format(self.bot.escape_name(member), unban_time_string, time.tzname[0]))
        msg = "⛔ **Time ban**: {} banned {} until {} | {}#{}\n🏷 __User ID__: {}".format(ctx.author.mention, member.mention, unban_time_string, self.bot.escape_name(member.name), member.discriminator, member.id)
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.serverlogs_channel.send(msg)
        await self.bot.modlogs_channel.send(msg + ("\nPlease add an explanation below. In the future, it is recommended to use `.timeban <user> <length> [reason]` as the reason is automatically sent to the user." if reason == "" else ""))

    @is_staff("OP")
    @commands.command(name="softban")
    async def softban_member(self, ctx, member: converters.SafeMember, *, reason):
        """Soft-ban a user. OP+ only.\n\nThis "bans" the user without actually doing a ban on Discord. The bot will instead kick the user every time they join. Discord bans are account- and IP-based."""
        if check_staff(member.id, 'Helper'):
            await self.meme(ctx.author, member, "softban", ctx.channel, reason)
            return
        issuer = ctx.author
        with open("data/softbans.json", "r") as f:
            softbans = json.load(f)
        if member.id not in softbans:
            softbans[member.id] = {}
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        softbans[member.id] = {"name": "{}#{}".format(member.name, member.discriminator), "issuer_id": issuer.id, "issuer_name": issuer.name, "reason": reason, "timestamp": timestamp}
        with open("data/softbans.json", "w") as f:
            json.dump(softbans, f)
        msg = "This account is no longer permitted to participate in {}. The reason is: {}".format(ctx.guild.name, softbans[member.id]["reason"])
        await member.send(msg)
        try:
            await member.kick
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
        await ctx.send("{} is now b&. 👍".format(self.bot.escape_name(member)))
        msg = "⛔ **Soft-ban**: {} soft-banned {} | {}#{}\n🏷 __User ID__: {}\n✏️ __Reason__: {}".format(ctx.author.mention, member.mention, self.bot.escape_name(member.name), member.discriminator, member.id, reason)
        await self.bot.modlogs_channel.send(msg)
        await self.bot.serverlogs_channel.send(msg)


    @is_staff("OP")
    @commands.command(name="softbanid")
    async def softbanid_member(self, ctx, user_id, *, reason):
        """Soft-ban a user based on ID. OP+ only.\n\nThis "bans" the user without actually doing a ban on Discord. The bot will instead kick the user every time they join. Discord bans are account- and IP-based."""
        issuer = ctx.author
        if check_staff(user_id, 'Helper'):
            await ctx.send("You can't softban another staffer with this command!")
            return
        with open("data/softbans.json", "r") as f:
            softbans = json.load(f)
        name = "???"
        if user_id not in softbans:
            softbans[user_id] = {}
        elif softbans[user_id]["name"] != "???":
            name = softbans[user_id]["name"]
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        softbans[user_id] = {"name": name, "issuer_id": issuer.id, "issuer_name": issuer.name, "reason": reason, "timestamp": timestamp}
        with open("data/softbans.json", "w") as f:
            json.dump(softbans, f)
        await ctx.send("ID {} is now b&. 👍".format(user_id))
        msg = "⛔ **Soft-ban**: {} soft-banned ID {}\n✏️ __Reason__: {}".format(ctx.author.mention, user_id, reason)
        await self.bot.modlogs_channel.send(msg)
        await self.bot.serverlogs_channel.send(msg)

    @is_staff("OP")
    @commands.command(name="unsoftban")
    async def unsoftban_member(self, ctx, user_id):
        issuer = ctx.author
        """Un-soft-ban a user based on ID. OP+ only."""
        with open("data/softbans.json", "r") as f:
            softbans = json.load(f)
        if user_id not in softbans:
            await ctx.send("{} is not soft-banned!".format(user_id))
            return
        name = softbans[user_id]["name"]
        softbans.pop(user_id)
        with open("data/softbans.json", "w") as f:
            json.dump(softbans, f)
        await ctx.send("{} has been unbanned!".format(self.bot.escape_name(name) if name != "???" else user_id))
        msg = "⚠️ **Un-soft-ban**: {} un-soft-banned {}".format(issuer.mention, self.bot.escape_name(name) if name != "???" else "ID {}".format(user_id))
        await self.bot.modlogs_channel.send(msg)

    @is_staff("HalfOP")
    @commands.command()
    async def listsoftbans(self, ctx, user_id=""):
        """List soft bans. Shows all if an ID is not specified."""
        with open("data/softbans.json", "r") as f:
            softbans = json.load(f)
        embed = discord.Embed(color=discord.Color.dark_red())
        if user_id == "":
            embed.title = "All soft bans"
            for softban in softbans:
                # sorry this is garbage
                embed.add_field(
                    name=self.bot.escape_name(softbans[softban]["name"]) if softbans[softban]["name"] != "???" else softban,
                    value="{}Issuer: {}\nTime: {}\nReason: {}".format(
                        "" if softbans[softban]["name"] == "???" else "ID: {}\n".format(softban),
                        self.bot.escape_name(softbans[softban]["issuer_name"]),
                        softbans[softban]["timestamp"],
                        softbans[softban]["reason"]
                    )
                )
        else:
            if user_id in softbans:
                embed.title = self.bot.escape_name(softbans[user_id]["name"]) if softbans[user_id]["name"] != "???" else user_id
                embed.description = "{}Issuer: {}\nTime: {}\nReason: {}".format(
                    "" if softbans[user_id]["name"] == "???" else "ID: {}\n".format(user_id),
                    self.bot.escape_name(softbans[user_id]["issuer_name"]),
                    softbans[user_id]["timestamp"],
                    softbans[user_id]["reason"]
                )
            else:
                embed.color = discord.Color.green()
                embed.title = user_id
                embed.description = "ID is not banned!"
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(KickBan(bot))
