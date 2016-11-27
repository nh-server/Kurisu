import logging
import discord
from discord.ext import commands
from sys import argv

log = logging.getLogger('discord')

class Announce:
    """
    Custom addon to make announcements.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    @commands.has_permissions(ban_members=True)
    @commands.command(hidden=True, pass_context=True)
    async def announce(self, ctx, *, inp):
        channel = discord.utils.get(ctx.message.server.channels, name="announcements")
        await self.bot.send_message(channel, inp)

    @commands.has_permissions(ban_members=True)
    @commands.command(hidden=True, pass_context=True)
    async def speak(self, ctx, channel_destination: str, *, inp):
        channel = ctx.message.channel_mentions[0]
        await self.bot.send_message(channel, inp)

    @commands.has_permissions(administrator=True)
    @commands.command(hidden=True, pass_context=True)
    async def dm(self, ctx, channel_destination: str, *, inp):
        dest = ctx.message.mentions[0]
        await self.bot.send_message(dest, inp)

def setup(bot):
    bot.add_cog(Announce(bot))
