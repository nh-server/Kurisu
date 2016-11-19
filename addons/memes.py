import discord
from discord.ext import commands
from sys import argv

class Memes:
    """
    Meme commands
    """
    def __init__(self, bot):
        self.bot = bot
    print('Addon "Memes" has been loaded.')

    def check_channel(self, ctx, msg):
        if ctx.message.channel.name[0:5] == "help-" or ctx.message.channel.name == "friend-codes":
            return ctx.message.author.mention + " Please do not use meme commands in the help or friend-codes channels."
        else:
            return msg

    # 3dshacks memes
    @commands.command(pass_context=True)
    async def s_99(self, ctx):
        """Memes."""
        await self.bot.say(self.check_channel(ctx, "**ALL HAIL BRITANNIA!**"))

    @commands.command(pass_context=True)
    async def xor(self, ctx):
        """Memes."""
        await self.bot.say(self.check_channel(ctx, "http://i.imgur.com/nLKATP6.png"))

    @commands.command(pass_context=True)
    async def megumi(self, ctx):
        """Memes."""
        await self.bot.say(self.check_channel(ctx, "http://i.imgur.com/GMRp1dj.jpg"))

    @commands.command(pass_context=True)
    async def inori(self, ctx):
        """Memes."""
        await self.bot.say(self.check_channel(ctx, "https://i.imgur.com/WLncIsi.gif"))

    @commands.command(pass_context=True)
    async def kina(self, ctx):
        """Memes."""
        await self.bot.say(self.check_channel(ctx, "http://i.imgur.com/8Mm5ZvB.jpg"))

    @commands.command(pass_context=True)
    async def r34(self, ctx):
        """Memes."""
        await self.bot.say(self.check_channel(ctx, "http://i.imgur.com/sjQZKBF.gif"))

    @commands.command(pass_context=True)
    async def lenny(self, ctx):
        """Memes."""
        await self.bot.say(self.check_channel(ctx, "( ͡° ͜ʖ ͡°)"))

    @commands.command(pass_context=True)
    async def rip(self, ctx):
        """Memes."""
        await self.bot.say(self.check_channel(ctx, "Press F to pay respects."))

    @commands.command(pass_context=True)
    async def permabrocked(self, ctx):
        """Memes."""
        await self.bot.say(self.check_channel(ctx, "http://i.imgur.com/ARsOh3p.jpg"))

    @commands.command(pass_context=True)
    async def clap(self, ctx):
        """Memes."""
        await self.bot.say(self.check_channel(ctx, "http://i.imgur.com/UYbIZYs.gifv"))

    # Cute commands :3
    @commands.command(pass_context=True)
    async def headpat(self, ctx):
        """Cute"""
        await self.bot.say(self.check_channel(ctx, "http://i.imgur.com/7V6gIIW.jpg"))

# Load the extension
def setup(bot):
    bot.add_cog(Memes(bot))
