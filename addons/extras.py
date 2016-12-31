import discord
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

def setup(bot):
    bot.add_cog(Extras(bot))
