import discord
import qrcode
import logging

from discord.ext import commands, tasks
from io import BytesIO
from inspect import cleandoc
from os.path import dirname, join
from Levenshtein import distance
from utils.utils import ConsoleColor
from utils.checks import check_if_user_can_sr
from utils.mdcmd import add_md_files_as_commands, check_console, systems

logger = logging.getLogger(__name__)


class Assistance(commands.Cog, command_attrs=dict(cooldown=commands.Cooldown(1, 30.0, commands.BucketType.channel))):
    """
    Commands that will mostly be used in the help channels.
    """

    format_map = {
        'nx_firmware': '12.1.0',
        'ams_ver': '0.20.1',
        'hekate_ver': '5.6.0',
        'last_revision': 'August 30th, 2021',
    }

    # compatibility until the use of these variables is removed
    nx_firmware = format_map['nx_firmware']
    ams_ver = format_map['ams_ver']
    hekate_ver = format_map['hekate_ver']
    last_revision = format_map['last_revision']

    data_dir = join(dirname(__file__), 'assistance-cmds')

    def __init__(self, bot):
        self.bot = bot
        self.unidb = {}
        self.apps_update.start()

    @tasks.loop(hours=2)
    async def apps_update(self):
        async with self.bot.session.get("https://raw.githubusercontent.com/Universal-Team/db/master/docs/data/full.json", timeout=45) as r:
            if r.status == 200:
                # Content type is text/plain instead of application/json
                self.unidb = await r.json(content_type=None)
                logger.info("Downloaded Universal Team Database")
            else:
                self.unidb = {}
                logger.warning("Failed to fetch Universal Team Database.")

    def unisearch(self, query: str) -> dict:
        query = query.lower()
        max_rat = 0
        res = {}
        for app in self.unidb:
            title = app['title'].lower()
            len_tot = len(query) + len(title)
            ratio = int(((len_tot - distance(query, title)) / len_tot) * 100)
            if ratio > 50 and ratio > max_rat:
                res = app
                max_rat = ratio
        return res

    async def simple_embed(self, ctx, text, *, title="", color=discord.Color.default()):
        embed = discord.Embed(title=title, color=color)
        embed.description = cleandoc(text)
        await ctx.send(embed=embed)

    @check_if_user_can_sr()
    @commands.guild_only()
    @commands.command(aliases=["sr"], cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def staffreq(self, ctx, *, msg_request: str = ""):
        """Request staff, with optional additional text. Trusted, Helpers, Staff, Retired Staff, Verified only."""
        author = ctx.author
        await ctx.message.delete()
        msg = f"❗️ **Assistance requested**: {ctx.channel.mention} by {author.mention} | {self.bot.escape_text(author)} @here"
        if msg_request != "":
            embed = discord.Embed(color=discord.Color.gold())
            embed.description = msg_request
        await self.bot.channels['mods'].send(msg, embed=(embed if msg_request != "" else None), allowed_mentions=discord.AllowedMentions(everyone=True))
        try:
            await author.send(f"✅ Online staff have been notified of your request in {ctx.channel.mention}.", embed=(embed if msg_request != "" else None))
        except discord.errors.Forbidden:
            pass

    @commands.command()
    async def guide(self, ctx, *, consoles=""):
        """Links to the recommended guides."""
        consoles = consoles.casefold()
        consoleslist = {x for x in consoles.split() if x in systems}
        channel_name = ctx.channel.name if not isinstance(ctx.channel, discord.DMChannel) else ""

        if not consoleslist:
            if channel_name.startswith(systems):
                consoleslist = ['auto']
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")

                ctx.command.reset_cooldown(ctx)
                return
        for x in consoleslist:
            if check_console(x, channel_name, '3ds'):
                embed = discord.Embed(title="Guide", color=ConsoleColor.n3ds())
                embed.set_author(name="NH & Friends", url="https://3ds.hacks.guide/")
                embed.set_thumbnail(url="https://nintendohomebrew.com/assets/img/nhplai.png")
                embed.url = "https://3ds.hacks.guide/"
                embed.description = "A complete guide to 3DS custom firmware, from stock to boot9strap."
                await ctx.send(embed=embed)
                continue
            if check_console(x, channel_name, ('wiiu',)):
                embed = discord.Embed(title="Guide", color=ConsoleColor.wiiu())
                embed.set_author(name="NH Discord Server", url="https://wiiu.hacks.guide/")
                embed.set_thumbnail(url="https://i.imgur.com/CVSu1zc.png")
                embed.url = "https://wiiu.hacks.guide/"
                embed.description = "A complete Wii U custom firmware + coldboothax guide"
                await ctx.send(embed=embed)
                continue
            if check_console(x, channel_name, ('vwii',)):
                embed = discord.Embed(title="Guide", color=ConsoleColor.wiiu())
                embed.set_author(name="NH Discord Server", url="https://wiiu.hacks.guide/#/vwii-modding")
                embed.set_thumbnail(url="https://i.imgur.com/FclGzNz.png")
                embed.url = "https://wiiu.hacks.guide/#/vwii-modding"
                embed.description = "A complete vWii modding guide"
                await ctx.send(embed=embed)
                continue
            if check_console(x, channel_name, ('switch', 'nx', 'ns')):
                embed = discord.Embed(title="Guide", color=ConsoleColor.switch())
                embed.set_author(name="NH Discord Server", url="https://nh-server.github.io/switch-guide/")
                embed.set_thumbnail(url="https://i.imgur.com/CVSu1zc.png")
                embed.url = "https://nh-server.github.io/switch-guide/"
                embed.description = "A Switch guide from stock to Atmosphere"
                await ctx.send(embed=embed)
                continue
            if check_console(x, channel_name, ('legacy', 'wii')):
                embed = discord.Embed(title="Guide", color=ConsoleColor.wii())
                embed.set_author(name="RiiConnect24", url="https://wii.guide/")
                embed.set_thumbnail(url="https://i.imgur.com/KI6IXmm.png")
                embed.url = "https://wii.guide/"
                embed.description = "A complete original Wii softmod guide"
                await ctx.send(embed=embed)
            if check_console(x, channel_name, ('legacy', 'dsi')):
                embed = discord.Embed(title="Guide", color=ConsoleColor.legacy())
                embed.set_author(name="emiyl & DS⁽ⁱ⁾ Mode Hacking", url="https://dsi.cfw.guide/credits")
                embed.set_thumbnail(url="https://i.imgur.com/OGelKVt.png")
                embed.url = "https://dsi.cfw.guide/"
                embed.description = "The complete guide to modding your Nintendo DSi"
                await ctx.send(embed=embed)

    @commands.command(aliases=['finalizing', 'finalising', 'finalise'])
    async def finalize(self, ctx):
        """Finalizing Setup"""
        await self.simple_embed(ctx, """
                    3DS Hacks Guide's [Finalizing Setup](https://3ds.hacks.guide/finalizing-setup)
                    """, title="Finalizing Setup")

    @commands.command()
    async def soundhax(self, ctx):
        """Links to Soundhax Website"""
        embed = discord.Embed(title="Soundhax", color=discord.Color.blue())
        embed.set_author(name="Ned Williamson", url="http://soundhax.com/")
        embed.set_thumbnail(url="http://i.imgur.com/lYf0jan.png")
        embed.url = "http://soundhax.com"
        embed.description = "Free 3DS Primary Entrypoint <= 11.3"
        await ctx.send(embed=embed)

    @commands.command(aliases=['3dslanding'])
    async def getstarted(self, ctx):
        """Links the 3DS get-started page"""
        embed = discord.Embed(title="3DS CFW guide", color=ConsoleColor.n3ds())
        embed.set_author(name="NH & Friends", url="https://3ds.hacks.guide/get-started")
        embed.set_thumbnail(url="https://nintendohomebrew.com/assets/img/nhplai.png")
        embed.url = "https://3ds.hacks.guide/get-started"
        embed.description = "How to hack your 3DS console on any firmware from 1.0.0 to 11.14"
        await ctx.send(embed=embed)

    @commands.command()
    async def catalyst(self, ctx, console=None):
        """Link to problem solvers"""
        systems = ("3ds", "nx", "ns", "switch")
        channel_name = ctx.channel.name if not isinstance(ctx.channel, discord.DMChannel) else ""
        if not console:
            if channel_name.startswith(systems):
                console = "auto"
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")

                ctx.command.reset_cooldown(ctx)
                return
        if check_console(console, channel_name, '3ds'):
            embed = discord.Embed(title="eip's problem solver packs", color=ConsoleColor.n3ds())
            embed.description = cleandoc("""
            Please visit the following page and read the information provided.
            https://3ds.eiphax.tech/catalyst.html
            """)
            await ctx.send(embed=embed)
        elif check_console(console, channel_name, ('nx', 'switch', 'ns')):
            embed = discord.Embed(title="eip's problem solver pack", color=ConsoleColor.switch())
            embed.description = cleandoc("""
            Please visit the following page and read the information provided.
            https://nx.eiphax.tech/catalyst.html
            """)
            await ctx.send(embed=embed)

    @commands.command()
    async def nxcfw(self, ctx, cfw=""):
        """Information on why we don't support or recommend various other Switch CFWs"""

        if cfw == "sx":  # Alias for sxos
            cfw = "sxos"

        cfwinfo = {
            'kosmos': {
                'info': """
                        * Kosmos bundles several extras, including system modules which can cause issues with booting if they are not compatible
                        with the currently running firmware. As a result, troubleshooting is often required to figure out which one is causing the issue.""",
                'title': "Kosmos"
            },
            'reinx': {
                'info': """
                        * Older versions have caused bans due to the incorrectly implemented user agent string.
                        * The author has expressed no interest in adding emuMMC/emuNAND.
                        * The author has expressed that they feel it doesn't matter if consoles get banned.
                        * It often takes weeks to several months for it to get support for the latest firmware.""",
                'title': "ReiNX"
            },
            'sxos': {
                'info': """
                        * SX OS is illegal to purchase and own. It bundles various keys and copyrighted data that cannot be legally shared.
                        * It has known compatibility issues with homebrew, due to its non-standard and proprietary nature.
                        * It does not support loading custom system modules.
                        * Several versions of the CFW have caused users to be banned without their knowledge.""",
                'title': "SX OS"
            }
        }

        if not (info := cfwinfo.get(cfw)):
            await ctx.send(f"Please specify a cfw. Valid options are: {', '.join([x for x in cfwinfo])}.")

            ctx.command.reset_cooldown(ctx)
            return
        await self.simple_embed(ctx, info['info'], title=f"Why {info['title']} isn't recommended")

    @commands.command(aliases=["sderror", "sderrors", "sd"])
    async def sdguide(self, ctx):
        """SD Troubleshooter"""
        await self.simple_embed(ctx, """
                    Need to do something with your SD card? Find advice in [this guide](https://3ds.eiphax.tech/sd.html)
                    """, title="SD Troubleshooter")

    @commands.command()
    async def notbricked(self, ctx):
        """Missing boot.firm"""
        embed = discord.Embed(title="No, you are not bricked")
        embed.description = cleandoc("""
                            If your power LED turns on and off after you installed b9s, you are not bricked and are \
just missing a file called boot.firm in the root of your SD card.
                            """)
        embed.add_field(name="How to fix the issue", value="1. Check you inserted the SD card in your console\n 2. Place/replace the file, downloading it from https://github.com/LumaTeam/Luma3DS/releases", inline=False)
        embed.add_field(name="Checking your SD for errors or corruption", value="https://3ds.eiphax.tech/sderrors.html \n Please read the instructions carefully.", inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=["troubleshooting"])
    async def troubleshoot(self, ctx):
        """Troubleshooting guides for common issues"""
        embed = discord.Embed(title="Troubleshooting guide for most current 3DS hacking methods", color=discord.Color(0xA2BAE0))
        embed.url = "https://3ds.eiphax.tech/issues.html"
        embed.description = "A simple troubleshooting guide for common CFW and homebrew installation issues \n when using popular recent 3DS hacking methods."
        await ctx.send(embed=embed)

    @commands.command()
    async def emureco(self, ctx, console=None):
        """Quick advice for emunands"""
        systems = ("3ds", "nx", "ns", "switch")
        channel_name = ctx.channel.name if not isinstance(ctx.channel, discord.DMChannel) else ""
        if console not in systems:
            if channel_name.startswith(systems):
                console = "auto"
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")

                ctx.command.reset_cooldown(ctx)
                return
        if check_console(console, channel_name, '3ds'):
            embed = discord.Embed(title="EmuNAND for 3DS", color=ConsoleColor.n3ds())
            embed.description = cleandoc("""
            With the recent advances in hacking methods and safety, it is no longer recommended to use an emuNAND on a 3DS/2DS system.
            Generally, for most users, there is no reason or benefit to using an emuNAND on a 3DS/2DS system.
            If you do not know what an emuNAND is, or is used for, you do not need one.
            """)
            await ctx.send(embed=embed)
        elif check_console(console, channel_name, ('nx', 'switch', 'ns')):
            embed = discord.Embed(title="EmuMMC/EmuNAND for Switch", color=ConsoleColor.switch())
            embed.description = cleandoc(f"""
            On the Switch system, it is recommended to use an emuMMC/emuNAND.
            An emuMMC/emuNAND will take up approximately 30GB on your SD card, so the SD card must be 64GB or above.
            The purpose of an emuMMC/emuNAND is to give you a safe place to use custom firmware functions.
            This will allow you to keep your sysMMC/sysNAND clean, so you can use it online.
            Following the default NH server guide (type `.guide nx` in {self.bot.channels['bot-cmds'].mention} for a link) will set you up with an emuMMC/emuNAND.
            """)
            await ctx.send(embed=embed)

    @commands.command()
    async def failedupdate(self, ctx):
        """Notice about failed update on Wii U"""
        await self.simple_embed(ctx, """
                                 A failed update in Download Management does not mean there is an update and the system \
is trying to download it. This means your blocking method (DNS etc.) is working and \
the system can't check for an update.
                                 """, color=ConsoleColor.wiiu())

    @commands.command(aliases=["updateluma", "lumaupdate"])
    async def emptysd(self, ctx):
        """What to do if you delete all your SD card contents"""
        await self.simple_embed(ctx, """
                                If you need to update your 3DS CFW installation, **or** you have lost the contents of your SD card, \
                                please follow the directions on the 3DS Hacks Guide [Restoring / Updating CFW](https://3ds.hacks.guide/restoring-updating-cfw) page.
                                """, color=ConsoleColor.n3ds())

    @commands.command()
    async def luma(self, ctx, lumaversion=""):
        """Download links for Luma versions"""
        if len(lumaversion) >= 3 and lumaversion[0].isdigit() and lumaversion[1] == "." and lumaversion[2].isdigit():
            await self.simple_embed(ctx, f"Luma v{lumaversion}\nhttps://github.com/LumaTeam/Luma3DS/releases/tag/v{lumaversion}", color=discord.Color.blue())
        elif lumaversion == "latest":
            await self.simple_embed(ctx, "Latest Luma Version:\nhttps://github.com/LumaTeam/Luma3DS/releases/latest", color=discord.Color.blue())
        else:
            await self.simple_embed(ctx, """
                                    Download links for the most common Luma3DS releases:
                                    [Latest Luma](https://github.com/LumaTeam/Luma3DS/releases/latest)
                                    [Luma v7.0.5](https://github.com/LumaTeam/Luma3DS/releases/tag/v7.0.5)
                                    [Luma v7.1](https://github.com/LumaTeam/Luma3DS/releases/tag/v7.1)
                                    """, color=discord.Color.blue())

    @commands.command(aliases=["twlfix"])
    async def twl(self, ctx):
        """Information on how to fix a broken TWL Partition"""
        await self.simple_embed(ctx, """
                                Follow [TWLFix-CFW](https://github.com/MechanicalDragon0687/TWLFix-CFW/releases/).
                                These instructions require that you **perform a system update** after running the app.
                                """, title="Fix broken TWL", color=ConsoleColor.legacy())

    @commands.command(aliases=["hbl"])
    async def boot3dsx(self, ctx):
        """Download link for 3DS Homebrew Launcher, boot.3dsx"""
        await self.simple_embed(ctx, "The 3DS Homebrew Launcher, [boot.3dsx](https://github.com/fincs/new-hbmenu/releases/latest/download/boot.3dsx)")

    @commands.command(aliases=["faketiks"])
    async def faketik(self, ctx):
        """Download link for faketik"""
        await self.simple_embed(ctx, "3DS ticket spoofing utility, faketik: [faketik.3dsx](https://github.com/ihaveamac/faketik/releases)")

    @commands.command(aliases=["greenscr", "bootnds"])
    async def b9stool(self, ctx):
        """Download link for B9STool, boot.nds"""
        await self.simple_embed(ctx, "The B9S installation tool for DSiWare exploits.\nB9STool, [boot.nds](https://github.com/zoogie/b9sTool/releases)")

    @commands.command()
    async def homext(self, ctx):
        """Deleting home menu extdata"""
        await self.simple_embed(ctx, """
                                1. Navigate to the following folder on your SD card: \
`/Nintendo 3DS/(32 Character ID)/(32 Character ID)/extdata/00000000/`
                                2. Delete the corresponding folder for your region:
                                  USA: `0000008f`
                                  EUR: `00000098`
                                  JPN: `00000082`
                                  KOR: `000000A9`
                                  """, title="How to clear Home Menu extdata")

    @commands.command()
    async def deltheme(self, ctx, console=None):
        """Deleting home menu theme data"""
        systems = ("3ds", "nx", "ns", "switch")
        channel_name = ctx.channel.name if not isinstance(ctx.channel, discord.DMChannel) else ""
        if console not in systems:
            if channel_name.startswith(systems):
                console = "auto"
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")

                ctx.command.reset_cooldown(ctx)
                return
        if check_console(console, channel_name, '3ds'):
            await self.simple_embed(ctx, """
                            1. Navigate to the following folder on your SD card: \
`/Nintendo 3DS/(32 Character ID)/(32 Character ID)/extdata/00000000/`
                            2. Delete the corresponding folder for your region:
                              USA: `000002cd`
                              EUR: `000002ce`
                              JPN: `000002cc`
                              """, title="How to delete Home Menu Theme Data", color=ConsoleColor.n3ds())
        elif check_console(console, channel_name, ('nx', 'switch', 'ns')):
            await self.simple_embed(ctx, """
                            1. Navigate to the following folder on your SD card: `/atmosphere/contents`
                            2. Delete the folder with the name `0100000000001000`
                            **Note: On Atmosphere 0.9.4 or below, `contents` is called `titles`.**
                              """, title="How to delete Home Menu Theme Data", color=ConsoleColor.wiiu())

    @commands.command(aliases=['godmode9'])
    async def gm9(self, ctx):
        """Links to the guide on GodMode9"""
        embed = discord.Embed(title="GodMode9 Usage", color=discord.Color(0x66FFFF))
        embed.set_author(name="NH & Friends", url="https://3ds.hacks.guide/godmode9-usage")
        embed.set_thumbnail(url="https://nintendohomebrew.com/assets/img/nhplai.png")
        embed.url = "https://3ds.hacks.guide/godmode9-usage"
        embed.description = "GodMode9 usage guide"
        await ctx.send(embed=embed)

    @commands.command()
    async def flashcart(self, ctx):
        """Launcher for old flashcarts"""
        embed = discord.Embed(title="Launcher for old flashcards (r4,m3,dstt,dsx,etc)", color=discord.Color(0x42f462))
        embed.set_author(name="Apache Thunder", url="https://gbatemp.net/threads/r4-stage2-twl-flashcart-launcher-and-perhaps-other-cards-soon%E2%84%A2.416434/")
        embed.set_thumbnail(url="https://gbatemp.net/data/avatars/m/105/105648.jpg")
        embed.url = "https://gbatemp.net/threads/r4-stage2-twl-flashcart-launcher-and-perhaps-other-cards-soon%E2%84%A2.416434/"
        embed.description = "Launcher for old flashcards"
        await ctx.send(embed=embed)

    @commands.command()
    async def vc(self, ctx, *, consoles=""):
        """Link to Virtual Console Injects for 3DS/Wiiu."""
        injects = ("3ds", "wiiu")
        consoleslist = {x for x in consoles.split() if x in injects}
        channel_name = ctx.channel.name if not isinstance(ctx.channel, discord.DMChannel) else ""
        if not consoleslist:
            if channel_name.startswith(injects):
                consoleslist = ['auto']
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in injects])}.")

                ctx.command.reset_cooldown(ctx)
                return
        for x in consoleslist:
            if check_console(x, channel_name, ('3ds',)):
                embed = discord.Embed(title="Virtual Console Injects for 3DS", color=ConsoleColor.n3ds())
                embed.set_author(name="Asdolo", url="https://gbatemp.net/members/asdolo.389539/")
                embed.set_thumbnail(url="https://i.imgur.com/rHa76XM.png")
                embed.url = "https://mega.nz/#!qnAE1YjC!q3FRHgIAVEo4nRI2IfANHJr-r7Sil3YpPYE4w8ZbUPY"
                embed.description = ("The recommended way to play old classics on your 3DS.\n"
                                     "Usage guide [here](http://3ds.eiphax.tech/nsui.html).")
                await ctx.send(embed=embed)
                continue

            if check_console(x, channel_name, ('wiiu', 'wii u')):
                embed = discord.Embed(title="Virtual Console Injects for Wii U", color=ConsoleColor.wiiu())
                embed.set_author(name="NicoAICP", url="https://gbatemp.net/members/nicoaicp.404553/")
                embed.set_thumbnail(url="https://gbatemp.net/data/avatars/l/404/404553.jpg")
                embed.url = "https://gbatemp.net/threads/release-uwuvci-injectiine.486781/"
                embed.description = ("The recommended way to play old classics on your Wii U.\n"
                                    "Usage guide [here](https://flumpster.github.io/instructions/index).")
                await ctx.send(embed=embed)

    @commands.command()
    async def dump(self, ctx, console=None):
        """How to dump games and data for CFW consoles"""
        systems = ("3ds", "nx", "ns", "switch", "wiiu", "vwii", "dsi")
        channel_name = ctx.channel.name if not isinstance(ctx.channel, discord.DMChannel) else ""
        if console not in systems:
            if channel_name.startswith(systems):
                console = "auto"
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")

                ctx.command.reset_cooldown(ctx)
                return
        if check_console(console, channel_name, '3ds'):
            embed = discord.Embed(title="GodMode9 dump/build Guide", color=ConsoleColor.n3ds())
            embed.set_author(name="NH & Friends", url="https://3ds.hacks.guide/dumping-titles-and-game-cartridges")
            embed.set_thumbnail(url="https://nintendohomebrew.com/assets/img/nhplai.png")
            embed.url = "https://3ds.hacks.guide/dumping-titles-and-game-cartridges"
            embed.description = "How to dump/build CIAs and Files using GodMode9"
            await ctx.send(embed=embed)
        elif check_console(console, channel_name, ('switch', 'nx', 'ns')):
            embed = discord.Embed(title="Switch dump/build Guide", color=ConsoleColor.switch())
            embed.set_author(name="SuchMeme", url="https://suchmememanyskill.github.io/guides/switchdumpguide/")
            embed.set_thumbnail(url="https://i.imgur.com/FkKB0er.png")
            embed.url = "https://suchmememanyskill.github.io/guides/switchdumpguide/"
            embed.description = ("How to dump/build NSPs using NXDumpTool\n"
                                 "BAN Warning: only for use using offline emummc")
            await ctx.send(embed=embed)
        elif check_console(console, channel_name, ('wiiu',)):
            embed = discord.Embed(title="Wii U dump/install Guide", color=ConsoleColor.wiiu())
            embed.set_author(name="NH Discord Server", url="https://wiiu.hacks.guide/#/dump-games")
            embed.set_thumbnail(url="https://i.imgur.com/CVSu1zc.png")
            embed.url = "https://wiiu.hacks.guide/#/dump-games"
            embed.description = "How to dump/install Wii U game discs using disc2app and WUP Installer GX2"
            await ctx.send(embed=embed)
        elif check_console(console, channel_name, 'vwii'):
            embed = discord.Embed(title="vWii dump Guide", color=ConsoleColor.wii())
            embed.set_author(name="NH Discord Server", url="https://wiiu.hacks.guide/#/dump-wii-games")
            embed.set_thumbnail(url="https://i.imgur.com/CVSu1zc.png")
            embed.url = "https://wiiu.hacks.guide/#/dump-wii-games"
            embed.description = "How to dump Wii game discs on vWii using CleanRip"
            await ctx.send(embed=embed)
        elif check_console(console, channel_name, 'dsi'):
            embed = discord.Embed(title="GodMode9i dump Guide", color=ConsoleColor.legacy())
            embed.set_author(name="NightScript", url="https://dsi.cfw.guide/dumping-game-cards")
            embed.url = "https://dsi.cfw.guide/dumping-game-cards"
            embed.description = "How to dump cartridges on a Nintendo DSi using GodMode9i"
            await ctx.send(embed=embed)

    @commands.command()
    async def cartinstall(self, ctx):
        """How to install 3DS cartridges to the SD card"""
        embed = discord.Embed(title="3DS Cart Install Guide", color=ConsoleColor.n3ds())
        embed.set_author(name="NH & Friends")
        embed.set_thumbnail(url="https://nintendohomebrew.com/assets/img/nhplai.png")
        embed.url = "https://3ds.hacks.guide/dumping-titles-and-game-cartridges#installing-a-game-cartridge-directly-to-the-system"
        embed.description = "How to install 3DS cartridges to the SD card"
        await ctx.send(embed=embed)

    @commands.command()
    async def sighax(self, ctx):
        """Information about sighax"""
        embed = discord.Embed(title="Sighax Information", color=discord.Color(0x0000ff))
        embed.set_author(name="SciresM", url="https://www.reddit.com/r/3dshacks/comments/67f6as/psa_clearing_up_some_misconceptions_about_sighax/")
        embed.set_thumbnail(url="https://i.imgur.com/11ajkdJ.jpg")
        embed.url = "https://www.reddit.com/r/3dshacks/comments/67f6as/psa_clearing_up_some_misconceptions_about_sighax/"
        embed.description = "PSA About Sighax"
        await ctx.send(embed=embed)

    @commands.command(name="7zip")
    async def p7zip(self, ctx):
        """Download a .7z file extractor"""
        embed = discord.Embed(title="Download 7-Zip", color=discord.Color(0x0000ff))
        embed.description = ("To be able to extract .7z files, you will need an extractor that supports this format.\n"
                             "• Windows: [7-Zip](https://www.7-zip.org)\n"
                             "• Mac (Before 10.15 Catalina): [Keka](https://www.keka.io/en/)")
        await ctx.send(embed=embed)

    @commands.command()
    async def wiiuhdd(self, ctx):
        """Message on HDDs on the Wii U"""
        await self.simple_embed(ctx, """
                                If you're having trouble getting your HDD to work with your WiiU, it might be due to the HDD not getting enough power. \
One way to fix this is by using an y-cable to connect the HDD to two USB ports.
                                """)

    @commands.command(aliases=["pendingupdate"])
    async def delupdate(self, ctx):
        """Erase pending updates on Nintendo Switch"""
        await self.simple_embed(ctx, """
                                When an update is downloaded, but not installed, the console will not display the \
firmware version in System Settings.

                                • To reset on a stock system,  *power the console off* (hold the power button, follow on-screen prompts).\
 __Hold__ Volume - and Volume +, then Power. When you see Maintenance Mode, you \
can reboot, and check System Settings.
                                • If you're using CFW, launch Hekate, select your boot option, then immediately\
 __Hold__ Volume - and Volume +. When you see Maintenance Mode, you \
can reboot, and check System Settings.

                                To block automatic update downloads, type '.90dns' in <#261581918653513729> for further information.
                                 """, title="How to delete pending Switch Updates", color=ConsoleColor.switch())

    @commands.command()
    async def sdlock(self, ctx):
        """Disable write protection on an SD Card"""
        embed = discord.Embed(title="Disable write protection on an SD Card")
        embed.description = cleandoc("""
                                     This switch on the SD Card should be facing upwards, as in this photo. Otherwise, \
your device will refuse to write to it.
                                     *If it is write locked, your console and other applications may behave unexpectedly.*
                                     """)
        embed.set_image(url="https://i.imgur.com/RvKjWcz.png")
        await ctx.send(embed=embed)

    @commands.group(cooldown=commands.Cooldown(0, 0, commands.BucketType.channel), invoke_without_command=True, case_insensitive=True)
    async def tutorial(self, ctx):
        """Links to one of multiple guides"""
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send_help(ctx.command)
        else:
            await ctx.send(f'{ctx.author.mention}, if you wish to view the \
complete list of tutorials, send `.tutorial` to me in a DM.', delete_after=10)

    @tutorial.command(cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def pokemon(self, ctx):
        """Displays different guides for Pokemon"""
        embed = discord.Embed(title="Possible guides for **Pokemon**:", color=discord.Color.red())
        embed.description = "**pkhex**|**pkhax**|**pkgen** Links to PKHeX tutorial\n**randomize** Links to layeredfs randomizing tutorial\n**pksm** Links to the PKSM documentation"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["pkhax", "pkgen"], cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def pkhex(self, ctx):
        """Links to PKHeX tutorial"""
        embed = discord.Embed(title="PKHeX tutorial", color=discord.Color.red())
        embed.set_thumbnail(url="https://i.imgur.com/rr7Xf3E.jpg")
        embed.url = "https://3ds.eiphax.tech/pkhex.html"
        embed.description = "Basic tutorial for PKHeX"
        await ctx.send(embed=embed)

    @tutorial.command(cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def pksm(self, ctx):
        """Links to PKSM Documentation"""
        embed = discord.Embed(title="PKSM Documentation", color=discord.Color.red())
        embed.set_thumbnail(url="https://raw.githubusercontent.com/FlagBrew/PKSM/master/assets/banner.png")
        embed.url = "https://github.com/FlagBrew/PKSM/wiki"
        embed.description = "Documentation for PKSM"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["randomise"], cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def randomize(self, ctx):
        """Links to layeredfs randomizing tutorial"""
        embed = discord.Embed(title="Randomizing with LayeredFS", color=discord.Color.red())
        embed.set_thumbnail(url="https://i.imgur.com/rr7Xf3E.jpg")
        embed.url = "https://zetadesigns.github.io/randomizing-layeredfs.html"
        embed.description = "Basic tutorial for randomizing with LayeredFS"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["Animal_crossing"], cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def acnl(self, ctx):
        """Links to AC:NL editing tutorial"""
        embed = discord.Embed(title="AC:NL editing tutorial", color=discord.Color.green())
        embed.set_thumbnail(url="https://i.imgur.com/3rVToMF.png")
        embed.url = "https://3ds.eiphax.tech/acnl.html"
        embed.description = "Basic tutorial for AC:NL editing"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["twilightmenu", "dsimenu++", "srloader"], cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def twlmenu(self, ctx):
        """Links to twlmenu tutorial"""
        embed = discord.Embed(title="TWiLightMenu++ tutorial", color=discord.Color.purple())
        embed.set_thumbnail(url="https://avatars1.githubusercontent.com/u/46971470?s=200&v=4")
        embed.url = "https://wiki.ds-homebrew.com/twilightmenu/installing-3ds.html"
        embed.description = "Basic tutorial for installing TWiLightMenu++"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["forwarders", "forwarder", "twlforwarders"], cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def ndsforwarders(self, ctx):
        """Links to nds forwarders"""
        embed = discord.Embed(title="NDS Forwarder Guide", color=discord.Color.purple())
        embed.set_thumbnail(url="https://avatars.githubusercontent.com/u/46971470?s=400&v=4")
        embed.url = "https://wiki.ds-homebrew.com/ds-index/forwarders"
        embed.description = "Tutorial for NDS Forwarders"
        await ctx.send(embed=embed)

    @tutorial.command(cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def vcextract(self, ctx, console=""):
        """Links to Virtual Console Extraction tutorials"""
        systems = ("3ds", "wiiu")
        channel_name = ctx.channel.name if not isinstance(ctx.channel, discord.DMChannel) else ""
        if console not in systems:
            if channel_name.startswith(systems):
                console = "auto"
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")
                ctx.command.reset_cooldown(ctx)
                return

        embed = discord.Embed()
        if check_console(console, channel_name, "3ds"):
            embed.title = "3DS VC Extraction Tutorial"
            embed.set_author(name="GlaZed_Belmont")
            embed.set_thumbnail(url="https://i.imgur.com/TgdOPkG.png")
            embed.url = "https://glazedbelmont.github.io/vcextract/"
        elif check_console(console, channel_name, ('wiiu',)):
            embed.title = "Wii U VC Extraction Tutorial"
            embed.set_author(name="lendun, Lazr")
            embed.set_thumbnail(url="https://i.imgur.com/qXc4TY5.png")
            embed.url = "https://lendunistus.github.io/wiiuvcextract-guide/"
        embed.description = "Tutorial to extract a ROM out of your VC titles"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["ftpd"], cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def ftp(self, ctx, console=None):
        """FTPD/WinSCP ftp guide"""
        systems = ("3ds", "nx", "ns", "switch")
        channel_name = ctx.channel.name if not isinstance(ctx.channel, discord.DMChannel) else ""
        if console not in systems:
            if channel_name.startswith(systems):
                console = "auto"
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")
                ctx.command.reset_cooldown(ctx)
                return

        embed = discord.Embed()
        if check_console(console, channel_name, "3ds"):
            embed.title = "3DS FTP Guide"
            embed.url = "https://3ds.eiphax.tech/ftp.html"
        elif check_console(console, channel_name, ("nx", "ns", "switch")):
            embed.title = "Switch FTP Guide"
            embed.url = "https://nx.eiphax.tech/ftp.html"
        embed.colour = discord.Color.purple()
        embed.set_author(name="Krieg")
        embed.set_thumbnail(url="https://nintendohomebrew.com/assets/img/krieg.png")
        embed.description = "A guide to using ftp with FTPD and WinSCP"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["theme"])
    async def themes(self, ctx, console=None):
        """Links to tutorials for installing themes"""
        systems = ("3ds", "nx", "ns", "switch")
        channel_name = ctx.channel.name if not isinstance(ctx.channel, discord.DMChannel) else ""
        if console not in systems:
            if channel_name.startswith(systems):
                console = "auto"
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")

                ctx.command.reset_cooldown(ctx)
                return
        if check_console(console, channel_name, '3ds'):
            embed = discord.Embed(title="3DS Themes Tutorial", color=discord.Color.dark_orange())
            embed.url = "https://itspizzatime1501.github.io/guides/themes/"
            embed.description = "Tutorial for installing themes on the 3DS"
            await ctx.send(embed=embed)
        elif check_console(console, channel_name, ('nx', 'switch', 'ns')):
            embed = discord.Embed(title="Switch Themes Tutorial", color=discord.Color.dark_orange())
            embed.url = "https://nh-server.github.io/switch-guide/extras/theming/"
            embed.description = "Tutorial for installing themes on the Switch"
            await ctx.send(embed=embed)

    @commands.command(aliases=["uu"])
    async def universalupdater(self, ctx):
        """Community-maintained 3DS homebrew app store"""
        embed = discord.Embed(title="Universal Updater", color=discord.Color.blue())
        embed.set_author(name="Universal Team")
        embed.url = "https://github.com/Universal-Team/Universal-Updater/releases/latest"
        embed.description = "A Community-maintained 3DS homebrew app store"
        await ctx.send(embed=embed)

    @commands.command()
    async def cios(self, ctx):
        """cIOS installation guide"""
        embed = discord.Embed(title="cIOS Guide", color=ConsoleColor.wii())
        embed.set_author(name="tj_cool")
        embed.set_thumbnail(url="https://i.imgur.com/sXSNYyV.jpg")
        embed.url = "https://sites.google.com/site/completesg/backup-launchers/installation"
        embed.description = "A cIOS installation guide"
        await ctx.send(embed=embed)

    @commands.command()
    async def sdroot(self, ctx):
        """Picture to say what the heck is the root"""
        embed = discord.Embed()
        embed.set_image(url="https://i.imgur.com/QXHIvOz.jpg")
        await ctx.send(embed=embed)

    @commands.command()
    async def autorcm(self, ctx):
        """Guide and Warnings about AutoRCM"""
        embed = discord.Embed(title="Guide", color=ConsoleColor.switch())
        embed.set_author(name="NH Discord Server")
        embed.set_thumbnail(url="https://i.imgur.com/CVSu1zc.png")
        embed.url = "https://nh-server.github.io/switch-guide/extras/autorcm/"
        embed.description = "Guide and Warnings about AutoRCM"
        await ctx.send(embed=embed)

    @commands.command(aliases=['whatsid0', 'id0'])
    async def whatisid0(self, ctx):
        """Picture to say what the heck is the id0"""
        embed = discord.Embed()
        embed.set_image(url="https://media.discordapp.net/attachments/196635695958196224/677996125034250280/unknown-76.png")
        await ctx.send(embed=embed)

    @commands.command(aliases=['switchserial'])
    async def serial(self, ctx):
        """Picture to show what the hell a serial is"""
        embed = discord.Embed(title="Don't know where your Switch's serial is?", color=ConsoleColor.switch())
        embed.description = "This is where the serial is located. Use this number to check if you are patched."
        embed.set_image(url="https://i.imgur.com/03NfeFN.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def nxban(self, ctx):
        """Switch ban risk snippet"""
        await self.simple_embed(ctx, """
                                The Switch is a much more secure system than the 3DS, and Nintendo has upped their game when it comes to bans.
                                One of the main reasons for this is that there are significantly more monitoring systems, \
some of which cannot be turned off.

                                Remember that you can only reduce your chances of getting banned; nothing is guaranteed and you could be banned \
at any time if you decide to hack your device. It will always be a cat and mouse game, until or unless there are big changes \
in the scene.

                                Refer to <#465640445913858048> for a list of things to avoid doing to reduce your risks.
                                You cannot ask about unbanning your console here.
                                """, title="Switch Bans")

    @commands.command(name="90dns")
    async def ninetydns(self, ctx):
        """90DNS IP addresses"""
        await self.simple_embed(ctx, """
                                The public 90DNS IP addresses are:
                                - `207.246.121.77` (USA)
                                - `163.172.141.219`(France)

                                [Follow these steps](https://nh-server.github.io/switch-guide/extras/blocking_updates/) to set up 90dns and ensure it isn't being blocked

                                You will have to manually set these for each WiFi connection you have set up.""",
                                title="90DNS IP addresses", color=ConsoleColor.switch())

    @commands.command(aliases=['missingco'])
    async def missingconfig(self, ctx):
        """No main boot entries found solution"""
        await self.simple_embed(ctx, """
                                You forgot to copy the "hekate_ipl.ini" file to the bootloader folder on your sd card, or forgot to insert your sd card before booting hekate.

                                Note that if hekate can't find a config, it'll create one. So likely you now have a hekate_ipl.ini in your bootloader folder, replace it with the one from [the guide](https://nh-server.github.io/switch-guide/user_guide/emummc/sd_preparation/)
                                """, title="Getting the \"No main boot entries found\" error in hekate?", color=ConsoleColor.switch())

    @commands.command(aliases=['injector'])
    async def injectors(self, ctx):
        embed = discord.Embed(title="List of switch payload injectors", color=ConsoleColor.switch())
        embed.set_author(name="NH Discord Server", url="https://nh-server.github.io/switch-guide/extras/rcm_injectors/")
        embed.set_thumbnail(url="https://i.imgur.com/CVSu1zc.png")
        embed.url = "https://nh-server.github.io/switch-guide/extras/rcm_injectors/"
        embed.description = "A list of portable payload injectors for the Nintendo Switch"
        await ctx.send(embed=embed)

    @commands.command()
    async def safemode(self, ctx):
        """How to boot into Safe Mode on the 3DS"""
        await self.simple_embed(ctx, """
        To boot into Safe Mode on the 3DS, you need to power off your device and power it back on while holding <:3ds_button_a:295004457098543104>+<:3ds_button_r:295004508294086656>+<:3ds_button_l:295004499511214080>+<:3ds_dpad_up:295004548916051981>.

        If you did it correctly, you should be prompted with a system update.
        """, title="Safe Mode on the 3DS", color=ConsoleColor.n3ds())

    @commands.command(aliases=["torrentclients", "torrentclient"])
    async def torrent(self, ctx):
        """Torrent Clients"""
        await self.simple_embed(ctx, """
        Here are links to some good torrent clients:
        • [qBittorrent](https://www.qbittorrent.org/download.php)
        • [Deluge](https://dev.deluge-torrent.org/wiki/Download)
        • [Flud](https://play.google.com/store/apps/details?id=com.delphicoder.flud&hl=en_US) (Android)""", title="Torrent Clients")

    @commands.command(aliases=['wiiubrowserfreeze'])
    async def fixwiiuexploit(self, ctx):
        """Quick fix for the web browser exploit on the Wii U"""
        embed = discord.Embed(title="How to Reset the Internet Browser Save Data", color=ConsoleColor.wiiu())
        embed.set_author(name="Nintendo", url="https://en-americas-support.nintendo.com/app/answers/detail/a_id/1507/~/how-to-delete-the-internet-browser-history")
        embed.set_thumbnail(url="https://i.imgur.com/28menlj.png")
        embed.url = "https://en-americas-support.nintendo.com/app/answers/detail/a_id/1507/~/how-to-delete-the-internet-browser-history"
        embed.description = "A common fix for those whose web browser keeps freezing their Wii U while attempting the exploit."
        await ctx.send(embed=embed)

    @commands.command(aliases=['missingpayload'])
    async def wiiupayload(self, ctx):
        """Missing payload"""
        await self.simple_embed(ctx, """
        Missing payload file on the SD.
        Make sure you have a [payload.elf](https://github.com/wiiu-env/homebrew_launcher_installer/releases/latest) in the wiiu folder""",
                                title="FSOpenFile Failed [...] payload.elf", color=ConsoleColor.wiiu())

    @commands.command()
    async def recover(self, ctx):
        """Troubleshooting guide for vWii"""
        embed = discord.Embed(title="Recover a vWii IOS/Channel", color=ConsoleColor.wiiu())
        embed.set_author(name="NH Discord Server", url="https://wiiu.hacks.guide/#/recover-vwii-ioses-channels")
        embed.set_thumbnail(url="https://i.imgur.com/CVSu1zc.png")
        embed.url = "https://wiiu.hacks.guide/#/recover-vwii-ioses-channels"
        embed.description = "A complete guide to recover a lost or corrupted system channel or IOS on vWii"
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def invite(self, ctx, name: str = ""):
        """Post an invite to an approved server"""
        if not name:
            ctx.command.reset_cooldown(ctx)
            if self.bot.invitefilter.invites:
                return await ctx.send(f"Valid server names are: {', '.join(x.alias for x in self.bot.invitefilter.invites)}")
            else:
                return await ctx.send("There is no approved servers!")

        invite = await self.bot.invitefilter.fetch_invite_by_alias(alias=name)

        if invite:
            await ctx.send(f"https://discord.gg/{invite.code}")
            if invite.is_temporary:
                if invite.uses > 1:
                    await self.bot.invitefilter.set_uses(code=invite.code, uses=invite.uses - 1)
                else:
                    await self.bot.invitefilter.delete(code=invite.code)
        else:
            ctx.command.reset_cooldown(ctx)
            await ctx.send(f"Invalid invite name. Valid server names are: {', '.join(x.alias for x in self.bot.invitefilter.invites)}")

    @commands.command()
    async def db(self, ctx, console=None):
        """Links to the relevant games database"""
        systems = ("3ds", "nx", "ns", "switch")
        channel_name = ctx.channel.name if not isinstance(ctx.channel, discord.DMChannel) else ""
        if console not in systems:
            if channel_name.startswith(systems):
                console = "auto"
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")
                ctx.command.reset_cooldown(ctx)
                return
        if check_console(console, channel_name, '3ds'):
            embed = discord.Embed(title="3DS Database", color=ConsoleColor.n3ds())
            embed.url = "http://3dsdb.com/"
            embed.description = "3DS database for game releases."
            await ctx.send(embed=embed)
        elif check_console(console, channel_name, ('nx', 'switch', 'ns')):
            embed = discord.Embed(title="Nintendo Switch Database", color=ConsoleColor.switch())
            embed.url = "http://nswdb.com/"
            embed.description = "Nintendo Switch database for game releases."
            await ctx.send(embed=embed)

    @commands.command(aliases=['masterkey', 'parentalpin'])
    async def mkey(self, ctx):
        """Master Key(mkey) generator for parental controls"""
        await self.simple_embed(ctx, """[Master key generator](https://mkey.salthax.org/) to remove the parental controls pin on Nintendo Consoles""")

    @commands.command(aliases=['noessential'])
    async def noexefs(self, ctx):
        """Instructions on what to do if essential.exefs is missing"""
        embed = discord.Embed(title="What to do if essential.exefs is missing", color=ConsoleColor.n3ds())
        embed.description = "In order to do this, you will need to boot back into GodMode9"
        embed.add_field(name="Steps to obtain essential.exefs", value=cleandoc("""
                1. Reinsert your SD card into your console
                2. Boot back into GodMode9 by holding start while powering on
                3. Navigate to SysNAND Virtual
                4. Select `essential.exefs`
                5. Select `copy to 0:/gm9/out`
                6. Power off your console and insert your SD card into your computer
                7. Navigate to `/gm9/out` on your SD, `essential.exefs` should be there
            """))
        await ctx.send(embed=embed)

    @commands.command(aliases=['cbhc'])
    async def cbhcrules(self, ctx):
        """The rules for the CBHC CFW on Wii U to avoid a brick"""
        embed = discord.Embed(title="Installing CBHC incorrectly can brick your Wii U!", color=ConsoleColor.wiiu())
        embed.add_field(name="Make sure to follow the following rules when installing CBHC:", value=cleandoc("""
                - The DS game has to be legitimately installed from the eShop!
                - Don’t format the system while CBHC is installed!
                - Don’t delete the user account that bought the DS VC game!
                - Don’t re-install the same game using WUP Installer or from the eShop!
                - Don’t install Haxchi over CBHC! (You will not brick, but it will cause a boot-loop! Hold A when booting to access the Homebrew Launcher and uninstall CBHC.)
                - Don’t uninstall the DS Virtual Console game without [properly uninstalling CBHC first](https://wiiu.hacks.guide/#/uninstall-cbhc)!
                - Don’t move the DS Virtual Console game to a USB drive!
            """))
        await ctx.send(embed=embed)

    @commands.command(aliases=['usm'])
    async def unsafe_mode(self, ctx):
        """unSAFE_MODE Guide"""
        await self.simple_embed(ctx, """
                    3DS Hacks Guide's [unSAFE_MODE](https://git.io/JfNQ4)
                    """, title="unSAFE_MODE")

    @commands.command(aliases=['dn'])
    async def downgrade(self, ctx, console=None):
        """Why not downgrade"""
        systems = ("3ds", "nx", "ns", "switch")
        channel_name = ctx.channel.name if not isinstance(ctx.channel, discord.DMChannel) else ""
        if console not in systems:
            if channel_name.startswith(systems):
                console = "auto"
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")
                ctx.command.reset_cooldown(ctx)
                return
        if check_console(console, channel_name, ('nx', 'switch', 'ns')):
            embed = discord.Embed(title="Downgrading on the Switch: Why you shouldn't do it", color=ConsoleColor.switch())
            embed.description = "Downgrading your firmware on the Switch is not recommended. This will generally lead to a lot of issues and won't solve anything."
            embed.add_field(name="Possible side effects from downgrading:", value=cleandoc("""
                * Unable to boot if performed incorrectly.
                * Unable to boot due to a mismatched efuse count.
                * Inability to use your gamecards.
                * Save data compatibility issues.
                * Games not launching.
            """))
        elif check_console(console, channel_name, '3ds'):
            embed = discord.Embed(title="Downgrading on the 3DS: Why you shouldn't do it", color=ConsoleColor.n3ds())
            embed.description = "Downgrading your firmware on the 3DS is not recommended. Although you *can*, you won't get any benefits from it."
            embed.add_field(name="Possible side effects from downgrading:", value=cleandoc("""
                * Unable to boot if performed incorrectly.
                * Unable to access online services.
                * Save data compatibility issues.
                * Games not launching.
            """))
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def unidb(self, ctx, *, query: str):
        res = self.unisearch(query)
        if not res:
            return await ctx.send("No app found!")

        embed = discord.Embed(title=res['title'], color=int(res['color'][1:], 16))
        embed.description = f"{res['description']}\n [[Download]({res['download_page']})] [[Source](https://github.com/{res['github']})]"
        embed.set_footer(text=f"by {res['author']}")
        embed.set_thumbnail(url=res["image"])

        f = None
        if qr_urls := res.get('qr'):
            embed.set_image(url=list(qr_urls.values())[0])
        elif res.get('downloads'):
            qr_url = ""
            for file, data in res['downloads'].items():
                if 'cia' in file:
                    qr_url = data['url']
                    break
                elif '3dsx' in file:
                    qr_url = data['url']
            if qr_url:
                buffer = BytesIO()
                qrcode.make(data=qr_url).save(buffer, "png")
                buffer.seek(0)
                f = discord.File(fp=buffer, filename="qr.png")
                embed.set_image(url="attachment://qr.png")
        await ctx.send(file=f, embed=embed)


add_md_files_as_commands(Assistance)
add_md_files_as_commands(Assistance, join(Assistance.data_dir, 'tutorial'), namespace=Assistance.tutorial)


def setup(bot):
    bot.add_cog(Assistance(bot))
