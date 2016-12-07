import discord
from discord.ext import commands
from sys import argv

class Memes:
    """
    Meme commands
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    def _check_channel(self, ctx, msg):
        if ctx.message.channel.name[0:5] == "help-" or ctx.message.channel.name == "friend-codes":
            return ctx.message.author.mention + " Meme commands are disabled in this channel."
        else:
            return ctx.message.author.display_name + ": " + msg

    # list memes
    @commands.command(name="listmemes", pass_context=True)
    async def _listmemes(self, ctx):
        """List meme commands."""
        # this feels wrong...
        funcs = dir(self)
        msg = "```\n"
        for func in funcs:
            if func != "bot" and func[0] != "_":
                msg += func + "\n"
        msg += "```"
        await self.bot.say(self._check_channel(ctx, msg))

    # 3dshacks memes
    @commands.command(pass_context=True, hidden=True)
    async def s_99(self, ctx):
        """Memes."""
        await self.bot.say(self._check_channel(ctx, "**ALL HAIL BRITANNIA!**"))

    @commands.command(pass_context=True, hidden=True)
    async def xor(self, ctx):
        """Memes."""
        await self.bot.say(self._check_channel(ctx, "http://i.imgur.com/nLKATP6.png"))

    @commands.command(pass_context=True, hidden=True)
    async def megumi(self, ctx):
        """Memes."""
        await self.bot.say(self._check_channel(ctx, "http://i.imgur.com/GMRp1dj.jpg"))

    @commands.command(pass_context=True, hidden=True)
    async def inori(self, ctx):
        """Memes."""
        await self.bot.say(self._check_channel(ctx, "https://i.imgur.com/WLncIsi.gif"))

    @commands.command(pass_context=True, hidden=True)
    async def inori2(self, ctx):
        """Memes."""
        await self.bot.say(self._check_channel(ctx, "http://i.imgur.com/V0uu99A.jpg"))

    @commands.command(pass_context=True, hidden=True)
    async def kina(self, ctx):
        """Memes."""
        await self.bot.say(self._check_channel(ctx, "http://i.imgur.com/8Mm5ZvB.jpg"))

    @commands.command(pass_context=True, hidden=True)
    async def r34(self, ctx):
        """Memes."""
        await self.bot.say(self._check_channel(ctx, "http://i.imgur.com/sjQZKBF.gif"))

    @commands.command(pass_context=True, hidden=True)
    async def lenny(self, ctx):
        """Memes."""
        await self.bot.say(self._check_channel(ctx, "( ͡° ͜ʖ ͡°)"))

    @commands.command(pass_context=True, hidden=True)
    async def rip(self, ctx):
        """Memes."""
        await self.bot.say(self._check_channel(ctx, "Press F to pay respects."))

    @commands.command(pass_context=True, hidden=True)
    async def permabrocked(self, ctx):
        """Memes."""
        await self.bot.say(self._check_channel(ctx, "http://i.imgur.com/ARsOh3p.jpg"))

    @commands.command(pass_context=True, hidden=True)
    async def knp(self, ctx):
        """Memes."""
        await self.bot.say(self._check_channel(ctx, "http://i.imgur.com/EsJ191C.png"))

    @commands.command(pass_context=True)
    async def xarec(self, ctx):
        """Memes."""
        await self.bot.say(self._check_channel(ctx, "https://i.imgur.com/wRVuidH.gif"))
        
    @commands.command(pass_context=True)
    async def mitchy(self, ctx):
        """Memes."""
        await self.bot.say(self._check_channel(ctx, "https://i.imgur.com/nTVZTwt.gif"))    
    
    @commands.command(pass_context=True, hidden=True)
    async def clap(self, ctx):
        """Memes."""
        await self.bot.say(self._check_channel(ctx, "http://i.imgur.com/UYbIZYs.gifv"))

    @commands.command(pass_context=True, hidden=True)
    async def ayyy(self, ctx):
        """Memes."""
        await self.bot.say(self._check_channel(ctx, "http://i.imgur.com/NjMxnB5.gif"))

    @commands.command(pass_context=True, hidden=True)
    async def hazel(self, ctx):
        """Memes."""
        await self.bot.say(self._check_channel(ctx, "http://i.imgur.com/vpu8bX3.png"))

    @commands.command(pass_context=True, hidden=True)
    async def pbanj(self, ctx):
        """Memes."""
        await self.bot.say(self._check_channel(ctx, "http://i.imgur.com/c6P7KY5.png"))

    # Cute commands :3
    @commands.command(pass_context=True, hidden=True)
    async def headpat(self, ctx):
        """Cute"""
        await self.bot.say(self._check_channel(ctx, "http://i.imgur.com/7V6gIIW.jpg"))

# Load the extension
def setup(bot):
    bot.add_cog(Memes(bot))
