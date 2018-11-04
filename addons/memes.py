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
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/j0Dkv2Z.png")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def eeh(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/2SBC1Qo.jpg")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def dubyadud(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/Sohsi8s.png")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def megumi(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/GMRp1dj.jpg")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def inori(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="https://i.imgur.com/WLncIsi.gif")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def inori3(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/so8thgu.gifv")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def inori4(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/267IXh1.gif")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def inori5(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/lKcsiBP.png")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def inori6(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/SIJzpau.gifv")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def kina(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="https://i.imgur.com/C2Is4xt.png")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def kina2(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="https://i.imgur.com/WCiNd0x.png")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def shotsfired(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/zf2XrNk.gifv")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def rusure(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/dqh3fNi.png")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def r34(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/sjQZKBF.gif")
        await self._meme(embed=embed)

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
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/ARsOh3p.jpg")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def knp(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/EsJ191C.png")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def lucina(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/tnWSXf7.png")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def lucina2(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/ZPMveve.jpg")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def xarec(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/A59RbRT.png")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def clap(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/UYbIZYs.gifv")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def ayyy(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/bgvuHAd.png")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def hazel(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/vpu8bX3.png")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def thumbsup(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/hki1IIs.gifv")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def pbanjo(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/sBJKzuK.png")
        await self._meme(embed=embed)

    # Cute commands :3
    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def headpat(self, ctx):
        """Cute"""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/7V6gIIW.jpg")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def headpat2(self, ctx):
        """Cute"""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/djhHX0n.gifv")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def sudoku(self, ctx):
        """Cute"""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/VHlIZRC.png")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def baka(self, ctx):
        """Cute"""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/OyjCHNe.png")
        await self._meme(embed=embed)
        
    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def whale(self, ctx):
        """Cute"""
        embed=discord.Embed(title=ctx, color=0x2ca1dd)
        embed.set_image(url="https://i.imgur.com/yOfDWyY.gif")
        embed.set_footer(text="Whale Tales")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def mugi(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/lw80tT0.gif")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def lisp(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/RQeZErU.png")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def dev(self, ctx):
        """Reminds user where they are."""
        await self.bot.say("You {}seem to be in <#196635781798952960>.".format("do not " if ctx.message.channel.name != "dev" else ""))

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def headrub(self, ctx):
        """Cute"""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/j6xSoKv.jpg")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def blackalabi(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/JzFem4y.png")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def nom(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/p1r53ni.jpg")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def soghax(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/oQJy2eN.png")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def weebs(self, ctx):
        """Memes."""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/sPjRKUB.png")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def whatisr(self, ctx):
        """MEMES?"""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/Z8HhfzJ.jpg")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def helpers(self, ctx):
        """MEMES?"""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="http://i.imgur.com/0v1EgMX.png")
        await self._meme(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def concern(self, ctx):
        """MEMES?"""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="https://i.imgur.com/cWXBb5g.png")
        await self._meme(embed=embed)
        
    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def fuck(self, ctx):
        """MEMES?"""
        embed=discord.Embed(title=ctx, color=0x6b0fcc)
        embed.set_image(url="https://i.imgur.com/4lNA5Ud.gif")
        await self._meme(embed=embed)

# Load the extension
def setup(bot):
    bot.add_cog(Memes(bot))
