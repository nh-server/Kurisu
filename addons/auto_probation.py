import logging
import discord
from discord.ext import commands
from sys import argv

log = logging.getLogger('discord')

class AutoProbation:
    """
    Logs join and leave messages.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    async def on_member_join(self, member):
        server = member.server
        role = discord.utils.get(server.roles, name="Probation")
        await self.bot.add_roles(member, role)

def setup(bot):
    bot.add_cog(AutoProbation(bot))
