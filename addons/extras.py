import datetime
import discord
import os
import random
import re
import string
from discord.ext import commands
from sys import argv

class Extras:
    """
    Extra things.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    prune_key = "nokey"

    @commands.command()
    async def kurisu(self):
        """About Kurisu"""
        embed = discord.Embed(title="Kurisu", color=discord.Color.green())
        embed.set_author(name="916253 and ihaveahax")
        embed.set_thumbnail(url="http://i.imgur.com/hjVY4Et.jpg")
        embed.url = "https://github.com/916253/Kurisu"
        embed.description = "Kurisu, the Nintendo Homebrew Discord bot!"
        await self.bot.say("", embed=embed)

    @commands.command()
    async def membercount(self):
        """Prints the member count of the server."""
        await self.bot.say("{} has {:,} members!".format(self.bot.server.name, self.bot.server.member_count))

    @commands.has_permissions(ban_members=True)
    @commands.command(hidden=True)
    async def embedtext(self, *, text):
        """Embed content."""
        await self.bot.say(embed=discord.Embed(description=text))

    @commands.command(hidden=True)
    async def timedelta(self, length):
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
        curr = datetime.datetime.now()
        diff = datetime.timedelta(seconds=seconds)
        # http://stackoverflow.com/questions/2119472/convert-a-timedelta-to-days-hours-and-minutes
        days, hours, minutes = td.days, td.seconds//3600, (td.seconds//60)%60
        msg = "```\ncurr: {}\nnew:  {}\ndiff: {}\n```".format(
            curr,
            curr + diff,
            diff
        )
        await self.bot.say(msg)

    @commands.has_permissions(manage_nicknames=True)
    @commands.command()
    async def estprune(self, days=30):
        """Estimate count of members that would be pruned based on the amount of days. Staff only."""
        if days > 30:
            await self.bot.say("Maximum 30 days")
            return
        if days < 1:
            await self.bot.say("Minimum 1 day")
            return
        msg = await self.bot.say("I'm figuring this out!".format(self.bot.server.name))
        count = await self.bot.estimate_pruned_members(server=self.bot.server, days=days)
        await self.bot.edit_message(msg, "{:,} members inactive for {} day(s) would be kicked from {}!".format(count, days, self.bot.server.name))

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True)
    async def prune30(self, ctx, key=""):
        """Prune members that are inactive for 30 days. Staff only."""
        if self.bot.pruning > 0:
            await self.bot.say("Pruning is already in progress.")
            return
        if key != self.prune_key:
            if key != "":
                await self.bot.say("That's not the correct key.")
            self.prune_key = ''.join(random.sample(string.ascii_letters, 8))
            await self.bot.say("Are you sure you want to prune members inactive for 30 days?\nTo see how many members get kicked, use `.estprune`.\nTo confirm the prune, use the command `.prune30 {}`.".format(self.prune_key))
            return
        self.prune_key = ''.join(random.sample(string.ascii_letters, 8))
        await self.bot.say("Starting pruning!")
        count = await self.bot.prune_members(self.bot.server, days=30)
        self.bot.pruning = count
        await self.bot.send_message(self.bot.mods_channel, "{:,} are currently being kicked from {}!".format(count, self.bot.server.name))
        msg = "👢 **Prune**: {} pruned {:,} members".format(ctx.message.author.mention, count)
        await self.bot.send_message(self.bot.modlogs_channel, msg)

    @commands.has_permissions(manage_nicknames=True)
    @commands.command()
    async def disableleavelogs(self):
        """DEBUG COMMAND"""
        self.bot.pruning = True
        await self.bot.say("disable")

    @commands.has_permissions(manage_nicknames=True)
    @commands.command()
    async def enableleavelogs(self):
        """DEBUG COMMAND"""
        self.bot.pruning = False
        await self.bot.say("enable")

    @commands.command(name="32c3")
    async def _32c3(self):
        """Console Hacking 2015"""
        await self.bot.say("https://www.youtube.com/watch?v=bZczf57HSag")

    @commands.command(name="33c3")
    async def _33c3(self):
        """Nintendo Hacking 2016"""
        await self.bot.say("https://www.youtube.com/watch?v=8C5cn_Qj0G8")

    @commands.command()
    async def de(self):
        invalid()

    @commands.has_permissions(administrator=True)
    @commands.command(pass_context=True, hidden=True)
    async def dumpchannel(self, ctx, channel_name, limit=100):
        """Dump 100 messages from a channel to a file."""
        channel = ctx.message.channel_mentions[0]
        await self.bot.say("Dumping {} messages from {}".format(limit, channel.mention))
        os.makedirs("#{}-{}".format(channel.name, channel.id), exist_ok=True)
        async for message in self.bot.logs_from(channel, limit=limit):
            with open("#{}-{}/{}.txt".format(channel.name, channel.id, message.id), "w") as f:
                f.write(message.content)
        await self.bot.say("Done!")

    @commands.command(pass_context=True, hidden=True)
    async def togglechannel(self, ctx, channelname):
        """Enable or disable access to specific channels."""
        author = ctx.message.author
        await self.bot.delete_message(ctx.message)
        if channelname == "elsewhere":
            if self.bot.elsewhere_role in author.roles:
                await self.bot.remove_roles(author, self.bot.elsewhere_role)
                await self.bot.send_message(author, "Access to #elsewhere removed.")
            else:
                await self.bot.add_roles(author, self.bot.elsewhere_role)
                await self.bot.send_message(author, "Access to #elsewhere granted.")
        if channelname == "eventchat":
            if self.bot.eventchat_role in author.roles:
                await self.bot.remove_roles(author, self.bot.eventchat_role)
                await self.bot.send_message(author, "Access to #eventchat granted.")
            else:
                await self.bot.add_roles(author, self.bot.eventchat_role)
                await self.bot.send_message(author, "Access to #eventchat granted.")
        else:
            await self.bot.send_message(author, "{} is not a valid toggleable channel.".format(channelname))

    @commands.command(pass_context=True)
    async def norainbow(self, ctx):
        """Tired of it."""
        member = ctx.message.author
        if member.nick and member.nick[-1] == "🌈":
            await self.bot.say("Your nickname is now \"{}\"!".format(member.display_name[0:-1].strip()))
            await self.bot.change_nickname(member, member.display_name[0:-1])
        elif member.name[-1] == "🌈":
            await self.bot.say("Your username is the one with the rainbow!")
        else:
            await self.bot.say("You don't have a rainbow!")

def setup(bot):
    bot.add_cog(Extras(bot))
