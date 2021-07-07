import datetime
import discord
import math
import random

from discord.ext import commands
from utils import crud
from utils.checks import is_staff


class Memes(commands.Cog):
    """
    Meme commands
    """
    def __init__(self, bot):
        self.bot = bot

    async def _meme(self, ctx, msg, directed: bool = False, imagelink=None, allowed_mentions=None):
        author = ctx.author
        if isinstance(ctx.channel, discord.abc.GuildChannel) and (ctx.channel in self.bot.assistance_channels or (self.bot.roles['No-Memes'] in author.roles)):
            await ctx.message.delete()
            try:
                await ctx.author.send("Meme commands are disabled in this channel, or your privileges have been revoked.")
            except discord.errors.Forbidden:
                await ctx.send(f"{ctx.author.mention} Meme commands are disabled in this channel, or your privileges have been revoked.")
        elif imagelink is not None:
            title = f"{self.bot.escape_text(ctx.author.display_name) + ':' if not directed else ''} {msg}"
            embed = discord.Embed(title=title, color=discord.Color.default())
            embed.set_image(url=imagelink)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{self.bot.escape_text(ctx.author.display_name) + ':' if not directed else ''} {msg}", allowed_mentions=allowed_mentions)

    async def _meme2(self, ctx, msg, directed: bool = False, imagelink=None, allowed_mentions=None):
        author = ctx.author
        if isinstance(ctx.channel, discord.abc.GuildChannel) and (ctx.channel in self.bot.assistance_channels or (self.bot.roles['No-Memes'] in author.roles) or ctx.channel is self.bot.channels['bot-cmds']):
            await ctx.message.delete()
            try:
                await ctx.author.send("Meme commands are disabled in this channel, or your privileges have been revoked.")
            except discord.errors.Forbidden:
                await ctx.send(f"{ctx.author.mention} Meme commands are disabled in this channel, or your privileges have been revoked.")
        elif imagelink is not None:
            title = f"{self.bot.escape_text(ctx.author.display_name) + ':' if not directed else ''} {msg}"
            embed = discord.Embed(title=title, color=discord.Color.default())
            embed.set_image(url=imagelink)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{self.bot.escape_text(ctx.author.display_name) + ':' if not directed else ''} {msg}", allowed_mentions=allowed_mentions)

    # list memes
    @commands.command(name="listmemes")
    async def _listmemes(self, ctx):
        """List meme commands."""
        cmds = ", ".join([x.name for x in self.get_commands()][1:])
        await self._meme(ctx, f"```{cmds}```")

    # 3dshacks memes
    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def s_99(self, ctx):
        """Memes."""
        await self._meme(ctx, "**ALL HAIL BRITANNIA!**")

    @commands.command(hidden=True)
    @commands.cooldown(rate=5, per=30.0, type=commands.BucketType.channel)
    async def honk(self, ctx):
        """honk"""
        await self._meme(ctx, "`R A K E  I N  T H E  L A K E`")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def screams(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/j0Dkv2Z.png")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def eeh(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/2SBC1Qo.jpg")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def dubyadud(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/Sohsi8s.png")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def megumi(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/GMRp1dj.jpg")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def inori(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="https://i.imgur.com/WLncIsi.gif")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def inori2(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/V0uu99A.jpg")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def inori3(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/so8thgu.gif")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def inori4(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/267IXh1.gif")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def inori5(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/lKcsiBP.png")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def inori6(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/SIJzpau.gif")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def shotsfired(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/zf2XrNk.gif")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def rusure(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="https://imgur.com/sXnVRLw.gif")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r34(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/sjQZKBF.gif")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def lenny(self, ctx):
        """Memes."""
        await self._meme(ctx, "( ͡° ͜ʖ ͡°)")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def rip(self, ctx):
        """Memes."""
        await self._meme(ctx, "Press F to pay respects.")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def permabrocked(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/ARsOh3p.jpg")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def knp(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/EsJ191C.png")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def lucina(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/tnWSXf7.png")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def lucina2(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/ZPMveve.jpg")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def xarec(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/A59RbRT.png")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def clap(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/UYbIZYs.gif")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def ayyy(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/bgvuHAd.png")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def hazel(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/vpu8bX3.png")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def thumbsup(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/hki1IIs.gifv")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def pbanjo(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/sBJKzuK.png")

    # Cute commands :3
    @commands.command(hidden=True, aliases=["pat"])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def headpat(self, ctx, u: discord.Member):
        """headpat"""
        await self._meme(ctx, f"{self.bot.escape_text(u.display_name)} has been gently patted.", True, "http://i.imgur.com/7V6gIIW.jpg")

    @commands.command(hidden=True, aliases=["pat2"])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def headpat2(self, ctx, u: discord.Member):
        """headpat 2"""
        await self._meme(ctx, f"{self.bot.escape_text(u.display_name)} has been gently patted.", True, "http://i.imgur.com/djhHX0n.gif")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def headrub(self, ctx, u: discord.Member):
        """headrub"""
        await self._meme(ctx, f"{self.bot.escape_text(u.display_name)} has received a head rub.", True, "http://i.imgur.com/j6xSoKv.jpg")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def sudoku(self, ctx):
        """Cute"""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/VHlIZRC.png")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def baka(self, ctx):
        """Cute"""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/OyjCHNe.png")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def mugi(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/lw80tT0.gif")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def lisp(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/RQeZErU.png")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def dev(self, ctx):
        """Reminds user where they are."""
        await self._meme(ctx, f"You {'do not ' if ctx.channel != self.bot.channels['dev'] else ''}seem to be in {self.bot.channels['dev'].mention}.", True)

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def meta(self, ctx):
        """Reminds user where they are. (2)"""
        await self._meme(ctx, f"You {'do not ' if ctx.channel != self.bot.channels['meta'] else ''}seem to be in {self.bot.channels['meta'].mention}. Please take this subject {'there' if ctx.channel != self.bot.channels['meta'] else 'somewhere else'}.", True)

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def blackalabi(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/JzFem4y.png")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def whoops(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="https://i.imgur.com/caF9KHk.gif")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def nom(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/p1r53ni.jpg")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def soghax(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/oQJy2eN.png")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def weebs(self, ctx):
        """Memes."""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/sPjRKUB.png")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def whatisr(self, ctx):
        """MEMES?"""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/Z8HhfzJ.jpg")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def helpers(self, ctx):
        """MEMES?"""
        await self._meme(ctx, "", imagelink="http://i.imgur.com/0v1EgMX.png")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def concern(self, ctx):
        """MEMES?"""
        await self._meme(ctx, "", imagelink="https://i.imgur.com/cWXBb5g.png")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def fuck(self, ctx):
        """MEMES?"""
        await self._meme(ctx, "", imagelink="https://i.imgur.com/4lNA5Ud.gif")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def goose(self, ctx):
        """MEMES?"""
        await self._meme(ctx, "", imagelink="https://i.imgur.com/pZUeBql.jpg")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def planet(self, ctx):
        """haha yes!"""
        await self._meme(ctx, "", imagelink="https://i.imgur.com/YIBADGT.png")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def pbanj(self, ctx):
        """he has the power"""
        await self._meme(ctx, "", imagelink="https://i.imgur.com/EQy9pl3.png")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def pbanj2(self, ctx):
        """pbanos"""
        await self._meme(ctx, "", imagelink="https://i.imgur.com/oZx7Qid.gif")

    # Begin code from https://github.com/reswitched/robocop-ng
    @staticmethod
    def c_to_f(c):
        """this is where we take memes too far"""
        return math.floor(1.8 * c + 32)

    @staticmethod
    def c_to_k(c):
        """this is where we take memes REALLY far"""
        return math.floor(c + 273.15)

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def warm(self, ctx, u: discord.Member):
        """Warms a user :3"""
        celsius = random.randint(38, 100)
        fahrenheit = self.c_to_f(celsius)
        kelvin = self.c_to_k(celsius)
        await self._meme(ctx, f"{u.mention} warmed. User is now {celsius}°C ({fahrenheit}°F, {kelvin}K).", True)

    # adding it here cause its pretty much the same code
    @commands.command(hidden=True, aliases=["cool"])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def chill(self, ctx, u: discord.Member):
        """Cools a user :3"""
        celsius = random.randint(-273, 34)
        fahrenheit = self.c_to_f(celsius)
        kelvin = self.c_to_k(celsius)
        await self._meme(ctx, f"{u.mention} cooled. User is now {celsius}°C ({fahrenheit}°F, {kelvin}K).", True)
    # End code from https://github.com/reswitched/robocop-ng

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def bean(self, ctx, u: discord.Member):
        """swing the beanhammer"""
        await self._meme(ctx, f"{u.mention} is now beaned. <a:bean:462076812076384257>", True)

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def nogas(self, ctx):
        """shhhh no one gives a shit!"""
        await self._meme(ctx, "https://imgur.com/a/5IcfK6N")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def cosmic(self, ctx):
        """Cosmic ban"""
        await self._meme(ctx, "https://i.imgur.com/V4TVpbC.gifv")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def menuhax(self, ctx):
        """menuhax 11.4 wen"""
        await self._meme(ctx, "", imagelink="https://i.imgur.com/fUiZ2c3.png")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def magic(self, ctx):
        """shrug.avi"""
        await self._meme(ctx, "", imagelink="https://i.imgur.com/k9111dq.jpg")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def mouse(self, ctx):
        """Whaaaa"""
        await self._meme(ctx, "", imagelink="https://i.imgur.com/0YHBP7l.png")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def bananoose(self, ctx):
        """:)"""
        await self._meme(ctx, "", imagelink="https://i.imgur.com/VUmkXDd.jpg")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def goosenana(self, ctx):
        """:)"""
        await self._meme(ctx, "", imagelink="https://i.imgur.com/dLZOK5c.jpg")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def eel(self, ctx, u: discord.Member):
        """eel"""
        await self._meme(ctx, f"{self.bot.escape_text(u.display_name)} has been eel slapped.", True, "https://i.imgur.com/QXF2Pcn.gif")

    @commands.command(hidden=True, aliases=["bruh", "yolo", "swag"])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def dab(self, ctx):
        """Memes."""
        await self._meme(ctx, "No. I might be controlled by you idiots, but I have *some* self respect, baka...")

    @commands.command(hidden=True, aliases=["hacc"])
    @commands.cooldown(rate=5, per=60.0, type=commands.BucketType.channel)
    async def nobrain(self, ctx, *, action="hacc"):
        """h a c c"""
        await self._meme(ctx, f'`I have no brain and I must {" ".join(action.replace("`",""))}`')

    @commands.command(hidden=True, aliases=["wheresource", "sauce", "github"])
    @commands.cooldown(rate=5, per=30.0, type=commands.BucketType.channel)
    async def source(self, ctx):
        """You *did* read the GPL, *right?*"""
        await self._meme(ctx, "", imagelink="https://i.imgur.com/ceLGvc4.gif")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def pirate2(self, ctx):
        """stop right there, criminal scum"""
        await self._meme(ctx, "", imagelink="https://cdn.discordapp.com/attachments/508390946753216528/695752500179107910/giphy.gif")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def source2(self, ctx):
        """citation needed"""
        await self._meme(ctx, "", imagelink="https://album.eiphax.tech/uploads/big/b5c031e07ddbc3e48d0853f2d7064f66.jpg")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def disgraceful(self, ctx):
        """YOU DIDN'T SEE IT BECAUSE IT WASN'T THERE"""
        await self._meme(ctx, "", imagelink="https://album.eiphax.tech/uploads/big/b93b2a99bc28df4a192fc7eb8ccc01a9.png")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def greatness(self, ctx):
        """We were this close."""
        await self._meme(ctx, "", imagelink="https://album.eiphax.tech/uploads/big/f2b1e87af1fcdcd34f0dff65d7696deb.png")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def shovels(self, ctx):
        """Do you need more?"""
        await self._meme(ctx, "", imagelink="https://album.eiphax.tech/uploads/big/b798edd56662f1bde15ae4b6bc9c9fba.png")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def value(self, ctx):
        """smug.png"""
        await self._meme(ctx, "", imagelink="https://album.eiphax.tech/uploads/big/f882b32a3f051f474572b018d053bd7b.png")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def superiority(self, ctx):
        """opinions"""
        await self._meme(ctx, "", imagelink="https://album.eiphax.tech/uploads/big/e2cbbf7c808e21fb6c5ab603f6a89a3f.jpg")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=300.0, type=commands.BucketType.channel)
    async def cadealert(self, ctx):
        """stop! cade time."""
        await self._meme2(ctx, "excuse me <@&575940388452433940>, it is time for cade", allowed_mentions=discord.AllowedMentions(roles=True))

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=300.0, type=commands.BucketType.channel)
    async def birbalert(self, ctx):
        """stop! birb time."""
        await self._meme2(ctx, "excuse me <@&805294876673572884>, it is time for birb", allowed_mentions=discord.AllowedMentions(roles=True))

    @is_staff("OP")
    @commands.command(hidden=True, aliases=['🍰'])
    async def birthday(self, ctx, member: discord.Member):
        """Wishes a happy birthday. Do not abuse pls."""

        await ctx.message.delete()
        await member.add_roles(self.bot.roles['🍰'])

        timestamp = datetime.datetime.now()
        delta = datetime.timedelta(seconds=86400)
        expiring_time = timestamp + delta

        await crud.add_timed_role(member.id, self.bot.roles['🍰'].id, expiring_time)
        await ctx.send(f"Happy birthday {member.mention}!")

    @commands.command(hidden=True, aliases=["departure"])
    @commands.cooldown(rate=5, per=30.0, type=commands.BucketType.channel)
    async def depart(self, ctx):
        """From the amazing Mr. Burguers"""
        departure_gifs = ["https://i.imgur.com/Kbyp7i4.gif", "https://i.imgur.com/Wv8DoGC.gif"]
        await self._meme(ctx, "", imagelink=random.choice(departure_gifs))


def setup(bot):
    bot.add_cog(Memes(bot))
