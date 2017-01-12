import discord
from discord.ext import commands
from sys import argv

class AutoNoEmbed:
    """
    Logs join and leave messages.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    async def on_member_join(self, member):
        await self.bot.add_roles(member, self.bot.noembed_role)

def setup(bot):
    bot.add_cog(AutoNoEmbed(bot))
