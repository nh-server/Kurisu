import discord
from discord.ext import commands

class Memes:
    """
    Meme commands
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    async def _meme(self, ctx, msg):
        author = ctx.message.author
        if ctx.message.channel.name[0:5] == "help-" or "assistance" in ctx.message.channel.name or (self.bot.nomemes_role in author.roles):
            await self.bot.delete_message(ctx.message)
            try:
                await self.bot.send_message(author, "Meme commands are disabled in this channel, or your privileges have been revoked.")
            except discord.errors.Forbidden:
                await self.bot.say(author.mention + " Meme commands are disabled in this channel, or your privileges have been revoked.")
        else:
            await self.bot.say(self.bot.escape_name(ctx.message.author.display_name) + ": " + msg)

    # list memes
    @commands.command(name="listmemes", pass_context=True)
    async def _listmemes(self, ctx):
        """List meme commands."""
        # this feels wrong...
        funcs = dir(self)
        msg = "```\n"
        msg += ", ".join(func for func in funcs if func != "bot" and func[0] != "_")
        msg += "```"
        await self._meme(ctx, msg)

    # 3dshacks memes
    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def s_99(self, ctx):
        """Memes."""
        await self._meme(ctx, "**ALL HAIL BRITANNIA!**")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def screams(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/j0Dkv2Z.png")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def eeh(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/2SBC1Qo.jpg")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def dubyadud(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/Sohsi8s.png")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def megumi(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/GMRp1dj.jpg")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def inori(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://i.imgur.com/WLncIsi.gif")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def inori3(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/so8thgu.gifv")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def inori4(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/267IXh1.gif")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def inori5(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/lKcsiBP.png")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def inori6(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/SIJzpau.gifv")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def shotsfired(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/zf2XrNk.gifv")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def rusure(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/dqh3fNi.png")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def r34(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/sjQZKBF.gif")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def lenny(self, ctx):
        """Memes."""
        await self._meme(ctx, "( ͡° ͜ʖ ͡°)")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def rip(self, ctx):
        """Memes."""
        await self._meme(ctx, "Press F to pay respects.")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def permabrocked(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/ARsOh3p.jpg")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def knp(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/EsJ191C.png")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def lucina(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/tnWSXf7.png")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def lucina2(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/ZPMveve.jpg")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def xarec(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/A59RbRT.png")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def clap(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/UYbIZYs.gifv")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def ayyy(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/bgvuHAd.png")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def hazel(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/vpu8bX3.png")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def thumbsup(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/hki1IIs.gifv")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def pbanjo(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/sBJKzuK.png")

    # Cute commands :3
    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def headpat(self, ctx):
        """Cute"""
        await self._meme(ctx, "http://i.imgur.com/7V6gIIW.jpg")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def headpat2(self, ctx):
        """Cute"""
        await self._meme(ctx, "http://i.imgur.com/djhHX0n.gifv")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def sudoku(self, ctx):
        """Cute"""
        await self._meme(ctx, "http://i.imgur.com/VHlIZRC.png")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def baka(self, ctx):
        """Cute"""
        await self._meme(ctx, "http://i.imgur.com/OyjCHNe.png")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def mugi(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/lw80tT0.gif")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def lisp(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/RQeZErU.png")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def dev(self, ctx):
        """Reminds user where they are."""
        await self.bot.say("You {}seem to be in <#196635781798952960>.".format("do not " if ctx.message.channel.name != "dev" else ""))

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def headrub(self, ctx):
        """Cute"""
        await self._meme(ctx, "http://i.imgur.com/j6xSoKv.jpg")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def blackalabi(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/JzFem4y.png")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def nom(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/p1r53ni.jpg")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def soghax(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/oQJy2eN.png")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def weebs(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/sPjRKUB.png")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def whatisr(self, ctx):
        """MEMES?"""
        await self._meme(ctx, "http://i.imgur.com/Z8HhfzJ.jpg")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def helpers(self, ctx):
        """MEMES?"""
        await self._meme(ctx, "http://i.imgur.com/0v1EgMX.png")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def concern(self, ctx):
        """MEMES?"""
        await self._meme(ctx, "https://i.imgur.com/cWXBb5g.png")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def fuck(self, ctx):
        """MEMES?"""
        await self._meme(ctx, "https://i.imgur.com/4lNA5Ud.gif")
    
    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def planet(self, ctx):
        """haha yes!"""
        await self._meme(ctx, "https://i.imgur.com/YIBADGT.png")
       
    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def pbanj(self, ctx):
        """he has the power"""
        await self._meme(ctx, "https://i.imgur.com/EQy9pl3.png")
    
    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def nogas(self, ctx):
        """shhhh no one gives a shit!"""
        await self._meme(ctx, "https://imgur.com/a/5IcfK6N")
    
    

# Load the extension
def setup(bot):
    bot.add_cog(Memes(bot))
