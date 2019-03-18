import discord

from cogs.checks import is_staff
from discord.ext import commands


class Blah(commands.Cog, command_attrs=dict(hidden=True)):
    """
    Custom Cog to make announcements.
    """
    def __init__(self, bot):
        self.bot = bot
        print(f'Cog "{self.qualified_name}" loaded')

    @is_staff("OP")
    @commands.command()
    async def announce(self, ctx, *, inp):
        await self.bot.channels['announcements'].send(inp)

    @is_staff("OP")
    @commands.command()
    async def speak(self, ctx, channel: discord.TextChannel, *, inp):
        await channel.send(inp)

    @is_staff("OP")
    @commands.command()
    async def sendtyping(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        await channel.trigger_typing()

    @is_staff("Owner")
    @commands.command()
    async def dm(self, ctx, member: discord.Member, *, inp):
        await member.send(inp)


def setup(bot):
    bot.add_cog(Blah(bot))
