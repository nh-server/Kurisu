from discord.ext import commands
from addons.checks import is_staff
class Blah:
    """
    Custom addon to make announcements.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    @is_staff("OP")
    @commands.command(hidden=True, pass_context=True)
    async def announce(self, ctx, *, inp):
        await self.bot.send_message(self.bot.announcements_channel, inp)

    @is_staff("OP")
    @commands.command(hidden=True, pass_context=True)
    async def speak(self, ctx, channel_destination: str, *, inp):
        channel = ctx.message.channel_mentions[0]
        await self.bot.send_message(channel, inp)

    @is_staff("OP")
    @commands.command(hidden=True, pass_context=True)
    async def sendtyping(self, ctx, channel_destination: str):
        channel = ctx.message.channel_mentions[0]
        await self.bot.send_typing(channel)

    @is_staff("Owner")
    @commands.command(hidden=True, pass_context=True)
    async def dm(self, ctx, channel_destination: str, *, inp):
        dest = ctx.message.mentions[0]
        await self.bot.send_message(dest, inp)

def setup(bot):
    bot.add_cog(Blah(bot))
