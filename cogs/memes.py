from __future__ import annotations

import datetime
import discord
import math
import random

from discord.ext import commands
from typing import TYPE_CHECKING
from utils.checks import is_staff
from utils.utils import KurisuCooldown

if TYPE_CHECKING:
    from kurisu import Kurisu
    from typing import Optional
    from utils.context import KurisuContext


class Memes(commands.Cog):
    """
    Meme commands
    """

    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.bot.loop.create_task(self.init_memes())
        self.extras = bot.extras

        self.excluded = [self._listmemes, self.xiwarn, self.xipraise, self.gulag]

        for command in self.walk_commands():
            if command not in self.excluded and not command.cooldown:
                command._buckets = commands.DynamicCooldownMapping(KurisuCooldown(1, 15.0), commands.BucketType.channel)

    async def cog_check(self, ctx: KurisuContext) -> bool:
        if ctx.guild is None or ctx.command in self.excluded or isinstance(ctx.author, discord.User):
            return True
        return not (ctx.channel in self.bot.assistance_channels or self.bot.roles['No-Memes'] in ctx.author.roles)

    async def cog_command_error(self, ctx: KurisuContext, error: commands.CommandError):
        if isinstance(error, commands.CheckFailure) and ctx.channel.guild is not None:
            await ctx.message.delete()
            try:
                await ctx.author.send(
                    "Meme commands are disabled in this channel, or your privileges have been revoked.")
            except discord.Forbidden:
                await ctx.send(
                    f"{ctx.author.mention} Meme commands are disabled in this channel, or your privileges have been revoked.")

    async def init_memes(self):
        await self.bot.wait_until_all_ready()
        self.emoji = discord.utils.get(self.bot.guild.emojis, name='fug') or discord.PartialEmoji.from_str("⁉")
        self.wagu_emoji = discord.utils.get(self.bot.guild.emojis, name="wagu") or "⁉"
        self.waguspooky = discord.utils.get(self.bot.guild.emojis, name="waguspooky") or "⁉"
        self.waguxmas = discord.utils.get(self.bot.guild.emojis, name="waguxmas") or "⁉"
        self.waguspin = discord.utils.get(self.bot.guild.emojis, name="waguspin") or "⁉"
        self.waguspinaaa = discord.utils.get(self.bot.guild.emojis, name="waguspinaaa") or "⁉"
        self.waguwat = discord.utils.get(self.bot.guild.emojis, name="waguwat") or "⁉"
        self.waguwu = discord.utils.get(self.bot.guild.emojis, name="waguwu") or "⁉"
        self.waguw = discord.utils.get(self.bot.guild.emojis, name="waguw") or "⁉"
        self.hyperwagu = discord.utils.get(self.bot.guild.emojis, name="hyperwagu") or "⁉"
        self.wagupeek = discord.utils.get(self.bot.guild.emojis, name="wagupeek") or "⁉"
        self.poggu = discord.utils.get(self.bot.guild.emojis, name="poggu") or "⁉"
        self.waguburger = discord.utils.get(self.bot.guild.emojis, name="waguburger") or "⁉"
        self.wagucar = discord.utils.get(self.bot.guild.emojis, name="wagucar") or "⁉"
        self.shutwagu = discord.utils.get(self.bot.guild.emojis, name="shutwagu") or "⁉"
        self.waguboat = discord.utils.get(self.bot.guild.emojis, name="waguboat") or "⁉"
        self.wagutv = discord.utils.get(self.bot.guild.emojis, name="wagutv") or "⁉"
        self.ghostwagu = discord.utils.get(self.bot.guild.emojis, name="ghostwagu") or "⁉"
        self.flushedsquish = discord.utils.get(self.bot.guild.emojis, name="flushedsquish") or "⁉"
        self.flushedball = discord.utils.get(self.bot.guild.emojis, name="flushedball") or "⁉"
        self.flushedeyes = discord.utils.get(self.bot.guild.emojis, name="flushedeyes") or "⁉"
        self.plusher_flusher = discord.utils.get(self.bot.guild.emojis, name="plusher_flusher") or "⁉"
        self.isforme = discord.utils.get(self.bot.guild.emojis, name="isforme") or "⁉"
        self.flushedtriangle = discord.utils.get(self.bot.guild.emojis, name="flushedtriangle") or "⁉"
        self.flushedstuffed = discord.utils.get(self.bot.guild.emojis, name="flushedstuffed") or "⁉"
        self.flushedsquare = discord.utils.get(self.bot.guild.emojis, name="flushedsquare") or "⁉"
        self.flushedskull = discord.utils.get(self.bot.guild.emojis, name="flushedskull") or "⁉"
        self.flushedmoon = discord.utils.get(self.bot.guild.emojis, name="flushedmoon") or "⁉"
        self.flushedhot = discord.utils.get(self.bot.guild.emojis, name="flushedhot") or "⁉"
        self.flushedhand = discord.utils.get(self.bot.guild.emojis, name="flushedhand") or "⁉"
        self.flushedhalf = discord.utils.get(self.bot.guild.emojis, name="flushedhalf") or "⁉"
        self.flushedgoomba = discord.utils.get(self.bot.guild.emojis, name="flushedgoomba") or "⁉"
        self.flushedflat = discord.utils.get(self.bot.guild.emojis, name="flushedflat") or "⁉"
        self.flushedcowboy = discord.utils.get(self.bot.guild.emojis, name="flushedcowboy") or "⁉"
        self.flushedwater = discord.utils.get(self.bot.guild.emojis, name="flushedwater") or "⁉"
        self.flushedw = discord.utils.get(self.bot.guild.emojis, name="FlushedW") or "⁉"
        self.flushedhalf2 = discord.utils.get(self.bot.guild.emojis, name="flushedhalf2") or "⁉"
        self.flushedroulette = discord.utils.get(self.bot.guild.emojis, name="flushedroulette") or "⁉"
        self.flushedcushion = discord.utils.get(self.bot.guild.emojis, name="flushedcushion") or "⁉"
        self.flushedcrush = discord.utils.get(self.bot.guild.emojis, name="flushedcrush") or "⁉"
        self.isforme2 = discord.utils.get(self.bot.guild.emojis, name="isforme2") or "⁉"
        self.isforme3 = discord.utils.get(self.bot.guild.emojis, name="isforme3") or "⁉"
        self.flushed5 = discord.utils.get(self.bot.guild.emojis, name="flushed5") or "⁉"
        self.flushedbold = discord.utils.get(self.bot.guild.emojis, name="flushedbold") or "⁉"
        self.joyclap = discord.utils.get(self.bot.guild.emojis, name="joyclap") or "⁉"

    async def _meme(self, ctx: KurisuContext, msg, directed: bool = False, image_link: Optional[str] = None,
                    allowed_mentions: Optional[discord.AllowedMentions] = None):

        if image_link is not None:
            title = f"{self.bot.escape_text(ctx.author.display_name) + ':' if not directed else ''} {msg}"
            embed = discord.Embed(title=title, color=discord.Color.default())
            embed.set_image(url=image_link)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{self.bot.escape_text(ctx.author.display_name) + ':' if not directed else ''} {msg}",
                           allowed_mentions=allowed_mentions)

    # list memes
    @commands.command(name="listmemes")
    async def _listmemes(self, ctx: KurisuContext):
        """List meme commands."""
        cmds = ", ".join([x.name for x in self.get_commands()][1:])
        await self._meme(ctx, f"```{cmds}```")

    # 3dshacks memes
    @commands.command(hidden=True)
    async def s_99(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "**ALL HAIL BRITANNIA!**")

    @commands.command(hidden=True)
    async def honk(self, ctx: KurisuContext):
        """honk"""
        await self._meme(ctx, "`R A K E  I N  T H E  L A K E`")

    @commands.command(hidden=True)
    async def screams(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/screamsinternally.png")

    @commands.command(hidden=True)
    async def eeh(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/eeh.jpg")

    @commands.command(hidden=True)
    async def dubyadud(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/dubyadud.png")

    @commands.command(hidden=True)
    async def megumi(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/megumi.jpg")

    @commands.command(hidden=True)
    async def inori(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/inori.gif")

    @commands.command(hidden=True)
    async def inori2(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/inori2.jpg")

    @commands.command(hidden=True)
    async def inori3(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/inori3.gif")

    @commands.command(hidden=True)
    async def inori4(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/inori4.gif")

    @commands.command(hidden=True)
    async def inori5(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/inori5.png")

    @commands.command(hidden=True)
    async def inori6(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/inori6.gif")

    @commands.command(hidden=True)
    async def shotsfired(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/shotsfired.gif")

    @commands.command(hidden=True)
    async def rusure(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/rusure.gif")

    @commands.command(hidden=True)
    async def r34(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/r34.gif")

    @commands.command(hidden=True)
    async def lenny(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "( ͡° ͜ʖ ͡°)")

    @commands.command(hidden=True)
    async def rip(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "Press F to pay respects.")

    @commands.command(hidden=True)
    async def permabrocked(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/permabrocked.jpg")

    @commands.command(hidden=True)
    async def knp(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/knp.png")

    @commands.command(hidden=True)
    async def lucina(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/lucina.png")

    @commands.command(hidden=True)
    async def lucina2(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/lucina2.jpg")

    @commands.command(hidden=True)
    async def xarec(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/xarec.png")

    @commands.command(hidden=True)
    async def clap(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/clap.gif")

    @commands.command(hidden=True)
    async def ayyy(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/ayyy.png")

    @commands.command(hidden=True)
    async def hazel(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/hazel.png")

    @commands.command(hidden=True)
    async def thumbsup(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "https://nintendohomebrew.com/assets/img/nhmemes/thumbsup.gifv")

    @commands.command(hidden=True)
    async def pbanjo(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/pbanjo.png")

    # Cute commands :3
    @commands.command(hidden=True, aliases=["pat"])
    async def headpat(self, ctx: KurisuContext, u: discord.Member):
        """headpat"""
        await self._meme(ctx, f"{self.bot.escape_text(u.display_name)} has been gently patted.", True,
                         "https://nintendohomebrew.com/assets/img/nhmemes/pat.jpg")

    @commands.command(hidden=True, aliases=["pat2"])
    async def headpat2(self, ctx: KurisuContext, u: discord.Member):
        """headpat 2"""
        await self._meme(ctx, f"{self.bot.escape_text(u.display_name)} has been gently patted.", True,
                         "https://nintendohomebrew.com/assets/img/nhmemes/pat2.gif")

    @commands.command(hidden=True)
    async def headrub(self, ctx: KurisuContext, u: discord.Member):
        """headrub"""
        await self._meme(ctx, f"{self.bot.escape_text(u.display_name)} has received a head rub.", True,
                         "https://nintendohomebrew.com/assets/img/nhmemes/headrub.jpg")

    @commands.command(hidden=True)
    async def sudoku(self, ctx: KurisuContext):
        """Cute"""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/sudoku.png")

    @commands.command(hidden=True)
    async def baka(self, ctx: KurisuContext):
        """Cute"""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/baka.png")

    @commands.command(hidden=True)
    async def mugi(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/mugi.png")

    @commands.command(hidden=True)
    async def lisp(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/lisp.png")

    @commands.command(hidden=True)
    async def blackalabi(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/blackalabi.png")

    @commands.command(hidden=True)
    async def eip(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/eip.png")

    @commands.command(hidden=True)
    async def whoops(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "",
                         image_link="https://album.eiphax.tech/uploads/big/2ec4764e884d956fb882f3479fa87ecf.gif")

    @commands.command(hidden=True)
    async def nom(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/nom.png")

    @commands.command(hidden=True)
    async def soghax(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/soghax.png")

    @commands.command(hidden=True)
    async def weebs(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/weebs.png")

    @commands.command(hidden=True)
    async def helpers(self, ctx: KurisuContext):
        """MEMES?"""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/helpers.png")

    @commands.command(hidden=True)
    async def concern(self, ctx: KurisuContext):
        """MEMES?"""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/concern.png")

    @commands.command(hidden=True)
    async def fuck(self, ctx: KurisuContext):
        """MEMES?"""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/fuck.gif")

    @commands.command(hidden=True)
    async def goose(self, ctx: KurisuContext):
        """MEMES?"""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/goose.jpg")

    @commands.command(hidden=True)
    async def planet(self, ctx: KurisuContext):
        """haha yes!"""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/planet.png")

    @commands.command(hidden=True)
    async def pbanj(self, ctx: KurisuContext):
        """he has the power"""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/pbanj.png")

    @commands.command(hidden=True)
    async def pbanj2(self, ctx: KurisuContext):
        """pbanos"""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/pbanj2.gif")

    @commands.command(hidden=True)
    async def notreading(self, ctx: KurisuContext):
        """why read?"""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/notreading.gif")

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
    async def warm(self, ctx: KurisuContext, u: discord.Member):
        """Warms a user :3"""
        celsius = random.randint(38, 50)
        fahrenheit = self.c_to_f(celsius)
        kelvin = self.c_to_k(celsius)
        await self._meme(ctx, f"{u.mention} warmed. User is now {celsius}°C ({fahrenheit}°F, {kelvin}K).", True)

    @commands.command(hidden=True, aliases=["roast"])
    async def burn(self, ctx: KurisuContext, u: discord.Member):
        """Burns a user :fire:"""
        celsius = random.randint(51, 500)
        fahrenheit = self.c_to_f(celsius)
        kelvin = self.c_to_k(celsius)
        await self._meme(ctx, f"{u.mention} burned. User is now a crispy {celsius}°C ({fahrenheit}°F, {kelvin}K).", True)

    # adding it here because It's pretty much the same code
    @commands.command(hidden=True, aliases=["cool"])
    async def chill(self, ctx: KurisuContext, u: discord.Member):
        """Cools a user :3"""
        celsius = random.randint(-3, 21)
        fahrenheit = self.c_to_f(celsius)
        kelvin = self.c_to_k(celsius)
        await self._meme(ctx, f"{u.mention} cooled. User is now {celsius}°C ({fahrenheit}°F, {kelvin}K).", True)

    @commands.command(hidden=True, aliases=["cryofreeze"])
    async def freeze(self, ctx: KurisuContext, u: discord.Member):
        """Freezes a user :3"""
        celsius = random.randint(-300, -4)
        fahrenheit = self.c_to_f(celsius)
        kelvin = self.c_to_k(celsius)
        await self._meme(ctx, f"{u.mention} frozen. User is now {celsius}°C ({fahrenheit}°F, {kelvin}K). Wait how is that possible?", True)

    # End code from https://github.com/reswitched/robocop-ng

    @commands.command(hidden=True)
    async def bean(self, ctx: KurisuContext, u: discord.Member):
        """swing the beanhammer"""
        await self._meme(ctx, f"{u.mention} is now beaned. <a:bean:462076812076384257>", True)

    @commands.command(hidden=True)
    async def shower(self, ctx: KurisuContext, u: discord.Member):
        """unsoap"""
        await self._meme(ctx, f"{u.mention} has had their soap removed. 🧼 🚿", True)

    @commands.command(hidden=True)
    async def nogas(self, ctx: KurisuContext):
        """shhhh no one gives a shit!"""
        await self._meme(ctx, "https://nintendohomebrew.com/assets/img/nhmemes/nogas.mp4")

    @commands.command(hidden=True)
    async def cosmic(self, ctx: KurisuContext):
        """Cosmic ban"""
        await self._meme(ctx, "https://nintendohomebrew.com/assets/img/nhmemes/cosmicban.mp4")

    @commands.command(hidden=True)
    async def menuhax(self, ctx: KurisuContext):
        """menuhax 11.4 wen"""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/menuhax.png")

    @commands.command(hidden=True)
    async def magic(self, ctx: KurisuContext):
        """shrug.avi"""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/magic.jpg")

    @commands.command(hidden=True)
    async def mouse(self, ctx: KurisuContext):
        """Whaaaa"""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/mouse.png")

    @commands.command(hidden=True)
    async def bananoose(self, ctx: KurisuContext):
        """:)"""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/bananoose.jpg")

    @commands.command(hidden=True)
    async def goosenana(self, ctx: KurisuContext):
        """:)"""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/goosenana.jpg")

    @commands.command(hidden=True)
    async def eel(self, ctx: KurisuContext, u: discord.Member):
        """eel"""
        await self._meme(ctx, f"{self.bot.escape_text(u.display_name)} has been eel slapped.", True,
                         "https://nintendohomebrew.com/assets/img/nhmemes/eel.gif")

    @commands.command(hidden=True)
    async def blast(self, ctx: KurisuContext, u: discord.Member):
        """it's joever"""
        await self._meme(ctx, f"It's over, {u.mention}... バイデンブラスト[BIDEN BLAST] https://nintendohomebrew.com/assets/img/nhmemes/biden.png", True)

    @commands.command(hidden=True, aliases=["bruh", "yolo", "swag", "based"])
    async def dab(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "No. I might be controlled by you idiots, but I have *some* self respect, baka...")

    @commands.command(hidden=True, aliases=["hacc"])
    async def nobrain(self, ctx: KurisuContext, *, action="hacc"):
        """h a c c"""
        await self._meme(ctx, f'`I have no brain and I must {" ".join(action.replace("`", ""))}`')

    @commands.command(hidden=True, aliases=["wheresource", "sauce", "github"])
    async def source(self, ctx: KurisuContext):
        """You *did* read the GPL, *right?*"""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/source.gif")

    @commands.command(hidden=True)
    async def pirate2(self, ctx: KurisuContext):
        """stop right there, criminal scum"""
        await self._meme(ctx, "",
                         image_link="https://cdn.discordapp.com/attachments/508390946753216528/695752500179107910/giphy.gif")

    @commands.command(hidden=True)
    async def source2(self, ctx: KurisuContext):
        """citation needed"""
        await self._meme(ctx, "",
                         image_link="https://album.eiphax.tech/uploads/big/b5c031e07ddbc3e48d0853f2d7064f66.jpg")

    @commands.command(hidden=True)
    async def source3(self, ctx: KurisuContext):
        """citation needed (2)"""
        await self._meme(ctx, "",
                         image_link="https://nintendohomebrew.com/assets/img/nhmemes/source3.gif")

    @commands.command(hidden=True)
    async def disgraceful(self, ctx: KurisuContext):
        """YOU DIDN'T SEE IT BECAUSE IT WASN'T THERE"""
        await self._meme(ctx, "",
                         image_link="https://album.eiphax.tech/uploads/big/b93b2a99bc28df4a192fc7eb8ccc01a9.png")

    @commands.command(hidden=True)
    async def greatness(self, ctx: KurisuContext):
        """We were this close."""
        await self._meme(ctx, "",
                         image_link="https://album.eiphax.tech/uploads/big/f2b1e87af1fcdcd34f0dff65d7696deb.png")

    @commands.command(hidden=True)
    async def shovels(self, ctx: KurisuContext):
        """Do you need more?"""
        await self._meme(ctx, "",
                         image_link="https://album.eiphax.tech/uploads/big/b798edd56662f1bde15ae4b6bc9c9fba.png")

    @commands.command(hidden=True)
    async def value(self, ctx: KurisuContext):
        """smug.png"""
        await self._meme(ctx, "",
                         image_link="https://album.eiphax.tech/uploads/big/f882b32a3f051f474572b018d053bd7b.png")

    @commands.command(hidden=True)
    async def superiority(self, ctx: KurisuContext):
        """opinions"""
        await self._meme(ctx, "",
                         image_link="https://album.eiphax.tech/uploads/big/e2cbbf7c808e21fb6c5ab603f6a89a3f.jpg")

    @commands.command(hidden=True)
    async def dolar(self, ctx: KurisuContext):
        """mcdondal"""
        await self._meme(ctx, "",
                         image_link="https://album.eiphax.tech/uploads/big/3ecd851953906ecc2387cfd592ac97e7.png")

    @commands.command(hidden=True)
    async def serotonin(self, ctx: KurisuContext):
        """I really want to know"""
        await self._meme(ctx, "",
                         image_link="https://album.eiphax.tech/uploads/big/2549ac8b197ae68080041d3966a887e8.png")

    @commands.command(hidden=True, aliases=['decisions'])
    async def decision(self, ctx: KurisuContext):
        """duly noted"""
        await self._meme(ctx, "",
                         image_link="https://album.eiphax.tech/uploads/big/5186160fa1b8002fe8fa1867225e45a7.png")

    @commands.command(hidden=True)
    async def shitposting(self, ctx: KurisuContext):
        """i don't say this very often..."""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/shitposting.jpg")

    @commands.command(hidden=True, aliases=['tmyk'])
    async def themoreyouknow(self, ctx: KurisuContext):
        """now with ear rape"""
        await ctx.send("https://album.eiphax.tech/uploads/big/01432cfa6eb64091301037971f8225c4.webm")

    @commands.command(hidden=True)
    async def cope(self, ctx: KurisuContext):
        """and seethe"""
        await ctx.send("https://album.eiphax.tech/uploads/big/c43dd20db7ff59dec7bc15dd26d2b65f.mp4")

    @commands.command(hidden=True)
    async def didntask(self, ctx: KurisuContext):
        """damn that's crazy but"""
        await ctx.send("https://album.eiphax.tech/uploads/big/4f8e77e08460e2234cdaebc6308f1fd1.mp4")

    @is_staff("OP")
    @commands.guild_only()
    @commands.command(hidden=True, aliases=['🍰', 'cake'])
    async def birthday(self, ctx: KurisuContext, member: discord.Member):
        """Wishes a happy birthday. Do not abuse pls."""

        await ctx.message.delete()
        try:
            await member.add_roles(self.bot.roles['🍰'])
        except discord.Forbidden:
            return

        timestamp = datetime.datetime.now(self.bot.tz)
        delta = datetime.timedelta(seconds=86400)
        expiring_time = timestamp + delta

        await self.extras.add_timed_role(member, self.bot.roles['🍰'], expiring_time)
        await ctx.send(f"Happy birthday {member.mention}!")

    @commands.command(hidden=True, aliases=["departure"])
    async def depart(self, ctx: KurisuContext):
        """From the amazing Mr. Burguers"""
        departure_gifs = ["https://nintendohomebrew.com/assets/img/nhmemes/departure1.gif",
                          "https://nintendohomebrew.com/assets/img/nhmemes/departure2.gif"]
        await self._meme(ctx, "", image_link=random.choice(departure_gifs))

    @commands.command(hidden=True)
    async def arrival(self, ctx: KurisuContext):
        """Glazy can add departure but not arrival smh"""
        arrival_gifs = ["https://nintendohomebrew.com/assets/img/nhmemes/arrival1.gif",
                        "https://nintendohomebrew.com/assets/img/nhmemes/arrival2.gif",
                        "https://nintendohomebrew.com/assets/img/nhmemes/arrival3.gif"]
        await self._meme(ctx, "", image_link=random.choice(arrival_gifs))

    @commands.command(hidden=True)
    async def hug(self, ctx: KurisuContext, u: discord.Member):
        """hug"""
        await self._meme(ctx, f"{self.bot.escape_text(u.display_name)} has received a hug.", True,
                         "https://nintendohomebrew.com/assets/img/nhmemes/hug.jpg")

    @commands.command(hidden=True)
    async def blahaj(self, ctx: KurisuContext, money: float):
        """Displays how many Blåhajs you could buy with a given amount of money. ($ or €)"""
        # blahaj. takes usd or eur
        blahaj_link = "https://nintendohomebrew.com/assets/img/blahaj.png"
        blahaj_price = 30  # should we handle eur and usd price difference properly?
        if money < blahaj_price:
            text = "You can't even buy a Blåhaj! Get more money, then buy a Blåhaj."
        elif money // blahaj_price == 1:
            text = "You could buy one Blåhaj with that. Think about it."
        elif money > blahaj_price * 100:
            text = "You could buy the entire stock. Think about it."
        else:
            text = f"You could buy {int(money // blahaj_price)} Blåhajs with that. Think about it."
        await self._meme(ctx, text, True, blahaj_link)

    @is_staff("Helper")
    @commands.command()
    async def xiwarn(self, ctx: KurisuContext, citizen: discord.Member):
        """Sometimes citizens need a reminder how to act"""
        await self.extras.add_social_credit(citizen.id, -100)
        await ctx.send(
            f"{ctx.author.mention} has assessed {citizen.mention}'s actions and removed 100 social credit from them!")

    @is_staff("Helper")
    @commands.command()
    async def xipraise(self, ctx: KurisuContext, citizen: discord.Member):
        """Model citizens will be praised"""
        await self.extras.add_social_credit(citizen.id, 100)
        await ctx.send(
            f"{ctx.author.mention} has assessed {citizen.mention}'s actions and added 100 social credit to them!")

    @is_staff("Helper")
    @commands.command(aliases=["sc"])
    async def socialcredit(self, ctx: KurisuContext, citizen: discord.Member):
        """You better keep this high"""
        db_citizen = await self.extras.get_citizen(citizen.id)
        if not db_citizen:
            await self.extras.add_citizen(citizen.id)
            await self.extras.get_citizen(citizen.id)
            return await ctx.send(f"{citizen.mention} is now a citizen and has 100 social credit!")
        await ctx.send(f"{citizen.mention} currently has {db_citizen.social_credit} social credit!")
        if db_citizen.social_credit < -200:
            await ctx.send("The citizen is due a visit to the reeducation camp!")
        elif db_citizen.social_credit > 500:
            await ctx.send("The citizen is an example for others to follow!")

    @is_staff("Helper")
    @commands.command()
    async def gulag(self, ctx: KurisuContext, citizen: discord.Member):
        """When the citizen was not meant to be"""
        db_citizen = await self.extras.get_citizen(citizen.id)
        if not db_citizen:
            return await ctx.send(f"There is no citizen named {citizen.mention}!")
        await self.extras.delete_citizen(citizen.id)
        await ctx.send(f"{citizen.mention} was sent away for reeducation purposes!")

    @commands.command(hidden=True)
    async def motd(self, ctx: KurisuContext):
        """got milk?"""
        motd_list = [str(self.flushedball), str(self.flushedsquish), str(self.flushedeyes),
                     "ur mom lol", "hot dogs are sandwiches dont @ me", "have you had a coffee today?",
                     "bird app bad", "imagine having opinions in current year", "based", "pog", "ratio",
                     "remember to moisturize today!", "drink some water u idiot", "take ur meds",
                     "do you like neapolitan ice cream?", "nentondon swonch", "xnoe at 11pm moment",
                     "has junko had a name change today?", "got milk?", "got pilk?",
                     "it has been 0 days since eip broke me", "ETA WEN PLS",
                     "The beatings will continue until morale improves.",
                     "Zǎoshang hǎo zhōngguó xiànzài wǒ yǒu BING CHILLING", "HELP QUIJA?",
                     str(self.joyclap), "Hell is empty, and the demons are here.", "Man alone measures time. Man alone chimes the hour.\r\nAnd, because of this, man alone suffers a paralyzing fear that no other creature endures.\r\nA fear of time running out."]
        await ctx.send(random.choice(motd_list))

    @commands.command(hidden=True)
    async def doom(self, ctx: KurisuContext):
        """got demons?"""
        doom_list = ["RIP AND TEAR", "I *could* run Doom, but I choose not to.", "The Ion Catapult is designed to use only approved UAC ammunition.",
                     "...we will send unto them... only you.", "May your thirst for retribution never quench, may the blood on your sword never dry, and may we never need you again.",
                     "That is a weapon, NOT a teleporter.", "You can't just shoot a hole into the surface of **Mars**...", "They are rage, brutal, without mercy. But you. You will be worse. Rip and tear, until it is done."]
        await ctx.send(random.choice(doom_list))

    @commands.command(hidden=True)
    async def hru(self, ctx: KurisuContext):
        """Finally asking how Kurisu is."""
        feeling_list = ["AWFUL", "stfu", "alright", "I am a bot what the fuck do you think?", "Look at the assistance channels for two minutes and tell me how **you** think I am."]
        await ctx.send(random.choice(feeling_list))

    @commands.command(hidden=True)
    async def wagu(self, ctx: KurisuContext, sample: commands.Range[int, 1, 10] = 1):
        """got wagu?"""
        wagulist = [self.wagu_emoji, self.waguspooky, self.waguxmas,
                    self.waguspin, self.waguspinaaa, self.waguwat,
                    self.waguwu, self.waguw, self.hyperwagu,
                    self.wagupeek, self.poggu, self.waguburger,
                    self.wagucar, self.shutwagu, self.waguboat,
                    self.wagutv, self.ghostwagu]
        await ctx.send(' '.join(map(str, random.choices(wagulist, k=sample))))

    @commands.command(hidden=True)
    async def flushed(self, ctx: KurisuContext, sample: commands.Range[int, 1, 10] = 1):
        """got flushed?"""
        flushed_list = [self.flushedsquish, self.plusher_flusher, self.isforme,
                        self.flushedtriangle, self.flushedstuffed, self.flushedball,
                        self.flushedeyes, self.flushedsquare, self.flushedskull,
                        self.flushedmoon, self.flushedhot, self.flushedhand,
                        self.flushedhalf, self.flushedgoomba, self.flushedflat,
                        self.flushedcowboy, self.flushedwater, self.flushedw,
                        self.flushedhalf2, self.flushedroulette, self.flushedcushion,
                        self.flushedcrush, self.isforme2, self.isforme3,
                        self.flushed5]
        await ctx.send(' '.join(map(str, random.choices(flushed_list, k=sample))))

    @commands.command(hidden=True, aliases=["freeshop", "3hs"])
    async def hshop(self, ctx: KurisuContext):
        """hmmmm nah"""
        await self._meme(ctx, "",
                         image_link="https://nintendohomebrew.com/assets/img/nhmemes/howboutno.gif")

    @commands.command(hidden=True, aliases=["stfu"])
    async def atkrieg(self, ctx: KurisuContext):
        """i'm not... strong enough"""
        await self._meme(ctx, "",
                         image_link="https://album.eiphax.tech/uploads/big/e86dd27f708078c919959f64b25fc0c0.png")

    @commands.command(hidden=True)
    async def eustace(self, ctx: KurisuContext):
        """eustace: regular edition"""
        await self._meme(ctx, "",
                         image_link="https://album.eiphax.tech/uploads/big/8bf790ad730890c1968006289543f3aa.png")

    @commands.command(hidden=True)
    async def eustace2(self, ctx: KurisuContext):
        """eustace: laser edition"""
        await self._meme(ctx, "",
                         image_link="https://album.eiphax.tech/uploads/big/3d36de23c42913610a074a5a36d687e6.jpeg")

    @commands.command(hidden=True)
    async def eustace3(self, ctx: KurisuContext):
        """eustace: bizarro edition"""
        await self._meme(ctx, "",
                         image_link="https://album.eiphax.tech/uploads/big/cf85135091814a6136aaf5acd395d860.jpeg")

    @commands.command(hidden=True)
    async def booba(self, ctx: KurisuContext):
        """:booba:"""
        await self._meme(ctx, "",
                         image_link="https://album.eiphax.tech/uploads/big/76781a4f317af75f2cd24fc0a78cbe2c.jpeg")

    @commands.command(hidden=True)
    async def nogas2(self, ctx: KurisuContext):
        """see?"""
        await self._meme(ctx, "",
                         image_link="https://nintendohomebrew.com/assets/img/nhmemes/nobodycares.png")

    @commands.command(hidden=True)
    async def poggere(self, ctx: KurisuContext):
        """poggers!"""
        await self._meme(ctx, "",
                         image_link="https://upload.wikimedia.org/wikipedia/commons/d/dd/Le_poggere.jpg?20201109224437")

    @commands.command(hidden=True)
    async def dumbass(self, ctx: KurisuContext):
        """use sparingly"""
        await self._meme(ctx, "",
                         image_link="https://nintendohomebrew.com/assets/img/nhmemes/dumbass.png")

    @commands.command(hidden=True)
    async def consider(self, ctx: KurisuContext):
        """well?"""
        await self._meme(ctx, "",
                         image_link="https://album.eiphax.tech/uploads/original/0e/1f/fbbfb561d1ea55706341014c765c.png")

    @commands.command(hidden=True)
    async def rotate(self, ctx: KurisuContext, u: discord.Member, degrees: int = None):
        bot: 'Kurisu' = ctx.bot
        """Rotate a user 🌪️"""
        MAX_DEGREES = 10000

        base_degrees = random.randint(-1080, 1080)

        if degrees is not None:
            if abs(degrees) > MAX_DEGREES:
                await ctx.send(f"That's too much rotation. Please keep it within ±{MAX_DEGREES} degrees.")
                return
            total_degrees = base_degrees + degrees
        else:
            total_degrees = base_degrees

        total_rotations = total_degrees / 360
        msg = f"{u.mention} has been rotated {base_degrees} degrees."

        if degrees is not None:
            if u.id == bot.user.id: # are we Kurisu?
                msg += f" This means I am now at {total_degrees} degrees, which is {total_rotations:.2f} rotations." # respond with useless level of detail if so
            else:
                msg += f" This means the user is now at {total_degrees} degrees, which is {total_rotations:.2f} rotations." # otherwise normal detail
        else:
            msg += f" That is {total_rotations:.2f} rotations."

        await self._meme(ctx, msg, True)

    @commands.command(hidden=True, aliases=["🅱"])
    async def b(self, ctx: KurisuContext):
        """haha, b emoji funny"""
        b_list = ["https://nintendohomebrew.com/assets/img/nhmemes/b1.png",
                  "https://nintendohomebrew.com/assets/img/nhmemes/b2.png",
                  "https://nintendohomebrew.com/assets/img/nhmemes/b3.png",
                  "https://nintendohomebrew.com/assets/img/nhmemes/b4.png",
                  "https://nintendohomebrew.com/assets/img/nhmemes/b5.png",
                  "https://nintendohomebrew.com/assets/img/nhmemes/b6.png",
                  "https://nintendohomebrew.com/assets/img/nhmemes/b7.png",
                  "https://nintendohomebrew.com/assets/img/nhmemes/b8.png",
                  "https://nintendohomebrew.com/assets/img/nhmemes/b9.png",
                  "https://nintendohomebrew.com/assets/img/nhmemes/b10.png",
                  "https://nintendohomebrew.com/assets/img/nhmemes/b11.png",
                  "https://nintendohomebrew.com/assets/img/nhmemes/b12.png",
                  "https://nintendohomebrew.com/assets/img/nhmemes/b13.png",
                  "https://nintendohomebrew.com/assets/img/nhmemes/b14.png",
                  "https://nintendohomebrew.com/assets/img/nhmemes/b15.png"]
        await self._meme(ctx, "", image_link=random.choice(b_list))

    @commands.command(hidden=True, aliases=['america'])
    @commands.cooldown(rate=1, per=300.0, type=commands.BucketType.channel)
    async def shootings(self, ctx: KurisuContext):
        """so we don't have to find it every time"""
        shooting_list = ["https://nintendohomebrew.com/assets/img/nhmemes/shooting1.png",
                         "https://nintendohomebrew.com/assets/img/nhmemes/shooting2.jpg"]
        await self._meme(ctx, "", image_link=random.choice(shooting_list))


async def setup(bot):
    await bot.add_cog(Memes(bot))
