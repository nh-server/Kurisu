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

    async def _meme(self, ctx: KurisuContext, msg, directed: bool = False, image_link: Optional[str] = None, allowed_mentions: Optional[discord.AllowedMentions] = None):

        if image_link is not None:
            title = f"{self.bot.escape_text(ctx.author.display_name) + ':' if not directed else ''} {msg}"
            embed = discord.Embed(title=title, color=discord.Color.default())
            embed.set_image(url=image_link)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{self.bot.escape_text(ctx.author.display_name) + ':' if not directed else ''} {msg}", allowed_mentions=allowed_mentions)

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
        await self._meme(ctx, f"{self.bot.escape_text(u.display_name)} has been gently patted.", True, "https://nintendohomebrew.com/assets/img/nhmemes/pat.jpg")

    @commands.command(hidden=True, aliases=["pat2"])
    async def headpat2(self, ctx: KurisuContext, u: discord.Member):
        """headpat 2"""
        await self._meme(ctx, f"{self.bot.escape_text(u.display_name)} has been gently patted.", True, "https://nintendohomebrew.com/assets/img/nhmemes/pat2.gif")

    @commands.command(hidden=True)
    async def headrub(self, ctx: KurisuContext, u: discord.Member):
        """headrub"""
        await self._meme(ctx, f"{self.bot.escape_text(u.display_name)} has received a head rub.", True, "https://nintendohomebrew.com/assets/img/nhmemes/headrub.jpg")

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
        await self._meme(ctx, "", image_link="https://album.eiphax.tech/uploads/big/2ec4764e884d956fb882f3479fa87ecf.gif")

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
        celsius = random.randint(38, 100)
        fahrenheit = self.c_to_f(celsius)
        kelvin = self.c_to_k(celsius)
        await self._meme(ctx, f"{u.mention} warmed. User is now {celsius}°C ({fahrenheit}°F, {kelvin}K).", True)

    # adding it here because It's pretty much the same code
    @commands.command(hidden=True, aliases=["cool"])
    async def chill(self, ctx: KurisuContext, u: discord.Member):
        """Cools a user :3"""
        celsius = random.randint(-273, 34)
        fahrenheit = self.c_to_f(celsius)
        kelvin = self.c_to_k(celsius)
        await self._meme(ctx, f"{u.mention} cooled. User is now {celsius}°C ({fahrenheit}°F, {kelvin}K).", True)
    # End code from https://github.com/reswitched/robocop-ng

    @commands.command(hidden=True)
    async def bean(self, ctx: KurisuContext, u: discord.Member):
        """swing the beanhammer"""
        await self._meme(ctx, f"{u.mention} is now beaned. <a:bean:462076812076384257>", True)

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
        await self._meme(ctx, f"{self.bot.escape_text(u.display_name)} has been eel slapped.", True, "https://nintendohomebrew.com/assets/img/nhmemes/eel.gif")

    @commands.command(hidden=True, aliases=["bruh", "yolo", "swag", "based"])
    async def dab(self, ctx: KurisuContext):
        """Memes."""
        await self._meme(ctx, "No. I might be controlled by you idiots, but I have *some* self respect, baka...")

    @commands.command(hidden=True, aliases=["hacc"])
    async def nobrain(self, ctx: KurisuContext, *, action="hacc"):
        """h a c c"""
        await self._meme(ctx, f'`I have no brain and I must {" ".join(action.replace("`",""))}`')

    @commands.command(hidden=True, aliases=["wheresource", "sauce", "github"])
    async def source(self, ctx: KurisuContext):
        """You *did* read the GPL, *right?*"""
        await self._meme(ctx, "", image_link="https://nintendohomebrew.com/assets/img/nhmemes/source.gif")

    @commands.command(hidden=True)
    async def pirate2(self, ctx: KurisuContext):
        """stop right there, criminal scum"""
        await self._meme(ctx, "", image_link="https://cdn.discordapp.com/attachments/508390946753216528/695752500179107910/giphy.gif")

    @commands.command(hidden=True)
    async def source2(self, ctx: KurisuContext):
        """citation needed"""
        await self._meme(ctx, "", image_link="https://album.eiphax.tech/uploads/big/b5c031e07ddbc3e48d0853f2d7064f66.jpg")

    @commands.command(hidden=True)
    async def disgraceful(self, ctx: KurisuContext):
        """YOU DIDN'T SEE IT BECAUSE IT WASN'T THERE"""
        await self._meme(ctx, "", image_link="https://album.eiphax.tech/uploads/big/b93b2a99bc28df4a192fc7eb8ccc01a9.png")

    @commands.command(hidden=True)
    async def greatness(self, ctx: KurisuContext):
        """We were this close."""
        await self._meme(ctx, "", image_link="https://album.eiphax.tech/uploads/big/f2b1e87af1fcdcd34f0dff65d7696deb.png")

    @commands.command(hidden=True)
    async def shovels(self, ctx: KurisuContext):
        """Do you need more?"""
        await self._meme(ctx, "", image_link="https://album.eiphax.tech/uploads/big/b798edd56662f1bde15ae4b6bc9c9fba.png")

    @commands.command(hidden=True)
    async def value(self, ctx: KurisuContext):
        """smug.png"""
        await self._meme(ctx, "", image_link="https://album.eiphax.tech/uploads/big/f882b32a3f051f474572b018d053bd7b.png")

    @commands.command(hidden=True)
    async def superiority(self, ctx: KurisuContext):
        """opinions"""
        await self._meme(ctx, "", image_link="https://album.eiphax.tech/uploads/big/e2cbbf7c808e21fb6c5ab603f6a89a3f.jpg")

    @commands.command(hidden=True)
    async def dolar(self, ctx: KurisuContext):
        """mcdondal"""
        await self._meme(ctx, "", image_link="https://album.eiphax.tech/uploads/big/3ecd851953906ecc2387cfd592ac97e7.png")

    @commands.command(hidden=True)
    async def serotonin(self, ctx: KurisuContext):
        """I really want to know"""
        await self._meme(ctx, "", image_link="https://album.eiphax.tech/uploads/big/2549ac8b197ae68080041d3966a887e8.png")

    @commands.command(hidden=True, aliases=['decisions'])
    async def decision(self, ctx: KurisuContext):
        """duly noted"""
        await self._meme(ctx, "", image_link="https://album.eiphax.tech/uploads/big/5186160fa1b8002fe8fa1867225e45a7.png")

    @commands.command(hidden=True, aliases=['tmyk'])
    async def themoreyouknow(self, ctx: KurisuContext):
        """now with ear rape"""
        await ctx.send("https://album.eiphax.tech/uploads/big/01432cfa6eb64091301037971f8225c4.webm")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=300.0, type=commands.BucketType.default)
    async def cadealert(self, ctx: KurisuContext):
        """stop! cade time."""
        await self._meme(ctx, "excuse me <@&575940388452433940>, it is time for cade", allowed_mentions=discord.AllowedMentions(roles=True))

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=300.0, type=commands.BucketType.channel)
    async def birbalert(self, ctx: KurisuContext):
        """stop! birb time."""
        await self._meme(ctx, "excuse me <@&805294876673572884>, it is time for birb", allowed_mentions=discord.AllowedMentions(roles=True))

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
        departure_gifs = ["https://nintendohomebrew.com/assets/img/nhmemes/departure1.gif", "https://nintendohomebrew.com/assets/img/nhmemes/departure2.gif"]
        await self._meme(ctx, "", image_link=random.choice(departure_gifs))

    @commands.command(hidden=True)
    async def arrival(self, ctx: KurisuContext):
        """Glazy can add departure but not arrival smh"""
        arrival_gifs = ["https://nintendohomebrew.com/assets/img/nhmemes/arrival1.gif", "https://nintendohomebrew.com/assets/img/nhmemes/arrival2.png"]
        await self._meme(ctx, "", image_link=random.choice(arrival_gifs))

    @commands.command(hidden=True)
    async def hug(self, ctx: KurisuContext, u: discord.Member):
        """hug"""
        await self._meme(ctx, f"{self.bot.escape_text(u.display_name)} has received a hug.", True, "https://nintendohomebrew.com/assets/img/nhmemes/hug.jpg")

    @commands.command(hidden=True)
    async def blahaj(self, ctx: KurisuContext, money: float):
        """Displays how much Blahajs you can buy with that money. ($ or €)"""
        # blahaj. takes usd or eur
        blahaj_link = "https://nintendohomebrew.com/assets/img/blahaj.png"
        if money < 18:
            text = "You can't even buy a Blahaj with that! Get more money, then buy a Blahaj."
        elif money // 18 == 1:
            text = "You could buy one Blahaj with that. Think about it."
        else:
            try:
                text = f"You could buy {int(money//18)} Blahajes with that. Think about it."
            except ValueError:
                text = "No."
        await self._meme(ctx, text, True, blahaj_link)

    @is_staff("Helper")
    @commands.command()
    async def xiwarn(self, ctx: KurisuContext, citizen: discord.Member):
        """Sometimes citizens need a reminder how to act"""
        await self.extras.add_social_credit(citizen.id, -100)
        await ctx.send(f"{ctx.author.mention} has assessed {citizen.mention}'s actions and removed 100 social credit from them!")

    @is_staff("Helper")
    @commands.command()
    async def xipraise(self, ctx: KurisuContext, citizen: discord.Member):
        """Model citizens will be praised"""
        await self.extras.add_social_credit(citizen.id, 100)
        await ctx.send(f"{ctx.author.mention} has assessed {citizen.mention}'s actions and added 100 social credit to them!")

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
        motd_list = [f"{str(self.flushedball)}", f"{str(self.flushedsquish)}", f"{str(self.flushedeyes)}",
                     "ur mom lol", "hot dogs are sandwiches dont @ me", "have you had a coffee today?",
                     "bird app bad", "imagine having opinions in current year", "based", "pog", "ratio",
                     "remember to moisturize today!", "drink some water u idiot", "take ur meds",
                     "do you like neapolitan ice cream?", "nentondon swonch", "xnoe at 11pm moment",
                     "has junko had a name change today?", "got milk?", "got pilk?",
                     "it has been 0 days since eip broke me", "ETA WEN PLS"]
        await ctx.send(random.choice(motd_list))

    @commands.command(hidden=True)
    async def wagu(self, ctx: KurisuContext):
        """got wagu?"""
        wagulist = [f"{str(self.wagu_emoji)}", f"{str(self.waguspooky)}", f"{str(self.waguxmas)}",
                    f"{str(self.waguspin)}", f"{str(self.waguspinaaa)}", f"{str(self.waguwat)}",
                    f"{str(self.waguwu)}", f"{str(self.waguw)}", f"{str(self.hyperwagu)}",
                    f"{str(self.wagupeek)}", f"{str(self.poggu)}", f"{str(self.waguburger)}",
                    f"{str(self.wagucar)}", f"{str(self.shutwagu)}", f"{str(self.waguboat)}",
                    f"{str(self.wagutv)}", f"{str(self.ghostwagu)}"]
        await ctx.send(random.choice(wagulist))

    @commands.command(hidden=True)
    async def flushed(self, ctx: KurisuContext):
        """got flushed?"""
        flushedlist = [f"{str(self.flushedsquish)}", f"{str(self.plusher_flusher)}", f"{str(self.isforme)}",
                       f"{str(self.flushedtriangle)}", f"{str(self.flushedstuffed)}", f"{str(self.flushedball)}",
                       f"{str(self.flushedeyes)}", f"{str(self.flushedsquare)}", f"{str(self.flushedskull)}",
                       f"{str(self.flushedmoon)}", f"{str(self.flushedhot)}", f"{str(self.flushedhand)}",
                       f"{str(self.flushedhalf)}", f"{str(self.flushedgoomba)}", f"{str(self.flushedflat)}",
                       f"{str(self.flushedcowboy)}", f"{str(self.flushedwater)}", f"{str(self.flushedw)}",
                       f"{str(self.flushedhalf2)}", f"{str(self.flushedroulette)}"]
        await ctx.send(random.choice(flushedlist))


async def setup(bot):
    await bot.add_cog(Memes(bot))
