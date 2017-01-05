import discord
import os
from discord.ext import commands
from sys import argv

class Extras:
    """
    Extra things.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    @commands.command()
    async def kurisu(self):
        """About Kurisu"""
        embed = discord.Embed(title="Kurisu", color=discord.Color.green())
        embed.set_author(name="916253 and ihaveahax")
        embed.set_thumbnail(url="http://static.zerochan.net/Makise.Kurisu.full.1998946.jpg")
        embed.url = "https://github.com/916253/Kurisu"
        embed.description = "Kurisu, the 3DS Hacking Discord bot!"
        await self.bot.say("", embed=embed)

    @commands.command()
    async def membercount(self):
        """Prints the member count of the server."""
        await self.bot.say("{} has {} members!".format(self.bot.server.name, self.bot.server.member_count))

    @commands.command(manage_nicknames=True)
    async def estprune(self, days=30):
        """Estimate count of members that would be pruned based on the amount of days. Staff only."""
        count = await self.bot.estimate_pruned_members(server=self.bot.server, days=days)
        await self.bot.say("{} members would be kicked from {}!".format(count, self.bot.server.name))

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

def setup(bot):
    bot.add_cog(Extras(bot))
