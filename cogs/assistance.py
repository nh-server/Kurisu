import aiohttp
import asyncio
import discord
import urllib.parse

from discord.ext import commands
from inspect import cleandoc
from utils.utils import ConsoleColor
from utils.checks import check_if_user_can_sr


class Assistance(commands.Cog, command_attrs=dict(cooldown=commands.Cooldown(1, 30.0, commands.BucketType.channel))):
    """
    Commands that will mostly be used in the help channels.
    """

    nx_firmware = "12.0.3"
    ams_ver = "0.19.4"
    hekate_ver = "5.5.7"
    last_revision = "June 9th, 2021"

    def __init__(self, bot):
        self.bot = bot
        self.systems = ("3ds", "wiiu", "vwii", "switch", "nx", "ns", "wii", "dsi", "legacy")

    async def simple_embed(self, ctx, text, *, title="", color=discord.Color.default()):
        embed = discord.Embed(title=title, color=color)
        embed.description = cleandoc(text)
        await ctx.send(embed=embed)

    def check_console(self, message, channel, consoles):
        message = message.lower()
        if message in consoles:
            return True
        elif ("wii" not in consoles or channel.startswith("legacy")) and channel.startswith(consoles) and message not in self.systems:
            return True
        return False

    @check_if_user_can_sr()
    @commands.guild_only()
    @commands.command(aliases=["sr", "Sr", "sR", "SR"], cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
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
        consoleslist = {x for x in consoles.split() if x in self.systems}
        channel_name = ctx.channel.name if not isinstance(ctx.channel, discord.DMChannel) else ""

        if not consoleslist:
            if channel_name.startswith(self.systems):
                consoleslist = ['auto']
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in self.systems])}.")

                ctx.command.reset_cooldown(ctx)
                return
        for x in consoleslist:
            if self.check_console(x, channel_name, '3ds'):
                embed = discord.Embed(title="Guide", color=ConsoleColor.n3ds())
                embed.set_author(name="NH & Friends", url="https://3ds.hacks.guide/")
                embed.set_thumbnail(url="https://nintendohomebrew.com/pics/nhplai.png")
                embed.url = "https://3ds.hacks.guide/"
                embed.description = "A complete guide to 3DS custom firmware, from stock to boot9strap."
                await ctx.send(embed=embed)
                continue
            if self.check_console(x, channel_name, ('wiiu',)):
                embed = discord.Embed(title="Guide", color=ConsoleColor.wiiu())
                embed.set_author(name="NH Discord Server", url="https://wiiu.hacks.guide/")
                embed.set_thumbnail(url="https://i.imgur.com/CVSu1zc.png")
                embed.url = "https://wiiu.hacks.guide/"
                embed.description = "A complete Wii U custom firmware + coldboothax guide"
                await ctx.send(embed=embed)
                continue
            if self.check_console(x, channel_name, ('vwii',)):
                embed = discord.Embed(title="Guide", color=ConsoleColor.wiiu())
                embed.set_author(name="NH Discord Server", url="https://wiiu.hacks.guide/#/vwii-modding")
                embed.set_thumbnail(url="https://i.imgur.com/FclGzNz.png")
                embed.url = "https://wiiu.hacks.guide/#/vwii-modding"
                embed.description = "A complete vWii modding guide"
                await ctx.send(embed=embed)
                continue
            if self.check_console(x, channel_name, ('switch', 'nx', 'ns')):
                embed = discord.Embed(title="Guide", color=ConsoleColor.switch())
                embed.set_author(name="NH Discord Server", url="https://nh-server.github.io/switch-guide/")
                embed.set_thumbnail(url="https://i.imgur.com/CVSu1zc.png")
                embed.url = "https://nh-server.github.io/switch-guide/"
                embed.description = "A Switch guide from stock to Atmosphere"
                await ctx.send(embed=embed)
                continue
            if self.check_console(x, channel_name, ('legacy', 'wii')):
                embed = discord.Embed(title="Guide", color=ConsoleColor.wii())
                embed.set_author(name="RiiConnect24", url="https://wii.guide/")
                embed.set_thumbnail(url="https://i.imgur.com/KI6IXmm.png")
                embed.url = "https://wii.guide/"
                embed.description = "A complete original Wii softmod guide"
                await ctx.send(embed=embed)
            if self.check_console(x, channel_name, ('legacy', 'dsi')):
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

    @commands.command()
    async def dsp(self, ctx):
        """Links to Dsp1."""
        embed = discord.Embed(title="Dsp1", color=discord.Color.green())
        embed.set_author(name="zoogie", url="https://github.com/zoogie", icon_url="https://gbatemp.net/data/avatars/l/357/357147.jpg?1426471484")
        embed.description = "Dump 3DS's DSP component to SD for homebrew audio."
        embed.set_thumbnail(url="https://raw.githubusercontent.com/Cruel/DspDump/master/icon.png")
        embed.url = "https://github.com/zoogie/DSP1/releases"
        await ctx.send(embed=embed)

    @commands.command()
    async def seedminer(self, ctx):
        """Links the seedminer guide"""
        embed = discord.Embed(title="Seedminer", color=discord.Color(0xb4eb4d))
        embed.set_author(name="NH & Friends", url="https://3ds.hacks.guide/seedminer")
        embed.set_thumbnail(url="https://nintendohomebrew.com/pics/nhplai.png")
        embed.url = "https://3ds.hacks.guide/seedminer"
        embed.description = "A guide on how to do the seedminer process to get your 3ds' movable.sed file"
        await ctx.send(embed=embed)

    @commands.command(aliases=['3dslanding'])
    async def getstarted(self, ctx):
        """Links the 3DS get-started page"""
        embed = discord.Embed(title="3DS CFW guide", color=ConsoleColor.n3ds())
        embed.set_author(name="NH & Friends", url="https://3ds.hacks.guide/get-started")
        embed.set_thumbnail(url="https://nintendohomebrew.com/pics/nhplai.png")
        embed.url = "https://3ds.hacks.guide/get-started"
        embed.description = "How to hack your 3DS console on any firmware from 1.0.0 to 11.14"
        await ctx.send(embed=embed)

    @commands.command(aliases=['snickerstream'])
    async def ntrstream(self, ctx):
        """Snickerstream/NTR streaming guide"""
        embed = discord.Embed(title="Snickerstream: NTR Streaming Client", color=ConsoleColor.n3ds())
        embed.url = "https://gbatemp.net/threads/release-snickerstream-revived-a-proper-release-with-lots-of-improvements-and-new-features.488374/"
        embed.description = "How to use NTR CFW with Snickerstream to stream your 3DS' screen"
        embed.add_field(name="Guide and Advice", value=cleandoc("""
                Easy [install guide](https://github.com/RattletraPM/Snickerstream/wiki/Streaming-with-NTR) for streaming with Snickerstream.
                Snickerstream [app download](https://github.com/RattletraPM/Snickerstream/releases/latest)
                Having issues? Check the following:
                • Are you connected to the Internet?
                • Is your antivirus program blocking the program?
                • Make sure you typed the IP correctly.
                • Make sure you are using the latest BootNTR Selector with NTR 3.6.
                More detailed troubleshooting [available here](https://github.com/RattletraPM/Snickerstream/wiki/Troubleshooting)
                Other information about Snickerstream on [Snickerstream's GitHub Wiki](https://github.com/RattletraPM/Snickerstream/wiki)
                """))
        await ctx.send(embed=embed)

    @commands.command()
    async def update(self, ctx, *, consoles=""):
        """Explains how to safely prepare for an update for a hacked console"""

        systems = ('3ds', 'nx', 'ns', 'switch')
        wanted_consoles = list(set(x for x in consoles.split() if x in systems))
        channel_name = ctx.channel.name if not isinstance(ctx.channel, discord.DMChannel) else ""

        if not wanted_consoles:
            if channel_name.startswith(systems):
                wanted_consoles = ["auto"]
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}")

                ctx.command.reset_cooldown(ctx)
                return

        for console in wanted_consoles:
            if self.check_console(console, channel_name, "3ds"):
                await self.simple_embed(ctx,
                    "**Is it safe to update to current 3DS firmware?**\n\n"

                    "**Luma3DS 10.2.1 and above**\n"
                    "You can update safely.\n\n"

                    "**Luma3DS 8.0 - 10.2**\n"
                    "Follow the [manual Luma3DS update guide](https://gist.github.com/lilyuwuu/3a7ba3dcd2476e6b5f4b6f66fa173bd6), then you can update safely. Being on these Luma3DS "
                    "versions on 11.8+ will cause an error screen until you update.\n\n"

                    "**Luma3DS 7.1**\n"
                    "Follow the [B9S upgrade guide](https://3ds.hacks.guide/updating-b9s)\n\n"

                    "**Luma3DS 7.0.5 and below**\n"
                    "Follow the [a9lh-to-b9s guide](https://3ds.hacks.guide/a9lh-to-b9s)\n\n"

                    "**To find out your Luma3DS version, hold select on bootup and look at the top left corner of the top screen**\n",
                                        color=ConsoleColor.n3ds())
            elif self.check_console(console, channel_name, ("switch", "nx", "ns")):
                embed = discord.Embed(title="Updating Guide", color=ConsoleColor.switch())
                embed.set_author(name="NH Discord Server", url="https://nh-server.github.io/switch-guide/")
                embed.set_thumbnail(url="https://i.imgur.com/CVSu1zc.png")
                embed.url = "https://nh-server.github.io/switch-guide/extras/updating/"
                embed.description = "A guide and general recommendations for updating your switch with emuMMC."
                await ctx.send(embed=embed)

    @commands.command(aliases=["checkluma"])
    @commands.cooldown(rate=1, per=15.0, type=commands.BucketType.channel)
    async def lumacheck(self, ctx):
        """How to check Luma version"""
        embed = discord.Embed(title="Please check your Luma version.", color=ConsoleColor.n3ds())
        embed.description = "In order to do this, you will need to load the Luma Configuration screen."
        embed.add_field(name="Steps to open Luma Configuration", value=cleandoc("""
                1. Turn your console off.
                2. Hold the SELECT button.
                3. While still holding SELECT, turn the console on.
                4. Provide a photo of your console's screens, or if you can see the version, tell us here.
                """))
        await ctx.send(embed=embed)

    @commands.command(aliases=["lowspace", "lowbackup"])
    @commands.cooldown(rate=1, per=15.0, type=commands.BucketType.channel)
    async def nospace(self, ctx):
        """Low space NAND Backup"""
        embed = discord.Embed(title="How to create a 3DS NAND backup without enough space on the SD card", color=ConsoleColor.n3ds())
        embed.add_field(name="Steps to create the backup", value=cleandoc("""
                1. Copy the Nintendo 3DS folder from the root of your SD card to your computer then delete it from **the SD card.**
                2. Boot GodMode9 by holding START on boot then preform a normal NAND backup. After that, power off the system.
                3. Copy the files in gm9/out on your SD card to a safe spot on your computer. Then, delete the files from **the SD card.**
                4. Copy the Nintendo 3DS folder to your SD card root then delete it **from your computer.**
                """))
        await ctx.send(embed=embed)

    @commands.command()
    async def cfwuses(self, ctx, console=""):
        """Uses for CFW on Wii U and 3DS"""
        systems = ("3ds", "wiiu", "nx", "ns", "switch")
        channel_name = ctx.channel.name if not isinstance(ctx.channel, discord.DMChannel) else ""
        if console not in systems:
            if channel_name.startswith(systems):
                console = "auto"
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")

                ctx.command.reset_cooldown(ctx)
                return
        if self.check_console(console, channel_name, '3ds'):
            """Links to eiphax cfw uses page"""
            await self.simple_embed(ctx, "Want to know what CFW can be used for? <https://3ds.eiphax.tech/tips.html>")
        elif self.check_console(console, channel_name, ('switch', 'nx', 'ns')):
            embed = discord.Embed(title="What can I do with a hacked switch?", color=ConsoleColor.switch())
            embed.description = cleandoc("""
                There is no complete list about what is possible and what not, but to give you an idea of what you can do, here is an overview:

                -Have custom themes,
                -Run emulators (up to N64 works, with a bit of modification GCN/Wii work fine as well but it varies from game to game),
                -Run custom homebrew apps,
                -Backup, edit and restore game saves,
                -Dump game cartridges (to look at the contents, for example)
                -Mod games,
                -Run Android or Linux on your Switch,
                -Still have access to normal stock features (e.g. eShop, online services etc.)""")
            await ctx.send(embed=embed)
        elif self.check_console(console, channel_name, ('wiiu',)):
            embed = discord.Embed(title="What can Wii U CFW be used for?", color=ConsoleColor.wiiu())
            embed.add_field(name="Among other things, it allows you to do the following:", value=cleandoc("""
                        - Use “ROM hacks” for games that you own.
                        - Backup, edit and restore saves for many games.
                        - Play games for older systems with various emulators, using RetroArch or other standalone emulators.
                        - Play out-of-region games.
                        - Dump your Wii U game discs to a format that can be installed on your internal or external Wii U storage drive.
                    """))
            await ctx.send(embed=embed)

    @commands.command()
    async def updateb9s(self, ctx):
        """Links to the guide for updating b9s versions"""
        embed = discord.Embed(title="Updating B9S Guide", color=ConsoleColor.n3ds())
        embed.set_author(name="NH & Friends", url="https://3ds.hacks.guide/updating-b9s")
        embed.set_thumbnail(url="https://nintendohomebrew.com/pics/nhplai.png")
        embed.url = "https://3ds.hacks.guide/updating-b9s"
        embed.description = "A guide for updating to new B9S versions."
        await ctx.send(embed=embed)

    @commands.command(aliases=["lumaupdate"])
    async def updateluma(self, ctx):
        """Links to the guide for updating Luma3DS manually (8.0 or later)"""
        embed = discord.Embed(title="Manually Updating Luma3DS", color=ConsoleColor.n3ds())
        embed.set_author(name="chenzw + lily", url="https://gist.github.com/lilyuwuu/3a7ba3dcd2476e6b5f4b6f66fa173bd6")
        embed.set_thumbnail(url="https://avatars0.githubusercontent.com/u/5243259?s=400&v=4")
        embed.url = "https://gist.github.com/lilyuwuu/3a7ba3dcd2476e6b5f4b6f66fa173bd6"
        embed.description = "A guide for manually updating Luma3ds. This is necessary if you receive the \"Failed to apply 1 Firm patch(es)\" or \"pm\" errors."
        await ctx.send(embed=embed)

    @commands.command(aliases=["a9lhtob9s", "updatea9lh"])
    async def atob(self, ctx):
        """Links to the guide for updating from a9lh to b9s"""
        embed = discord.Embed(title="Upgrading a9lh to b9s", color=ConsoleColor.n3ds())
        embed.set_author(name="NH & Friends", url="https://3ds.hacks.guide/a9lh-to-b9s")
        embed.set_thumbnail(url="https://nintendohomebrew.com/pics/nhplai.png")
        embed.url = "https://3ds.hacks.guide/a9lh-to-b9s"
        embed.description = "A guide for upgrading your device from arm9loaderhax to boot9strap."
        await ctx.send(embed=embed)

    @commands.command(aliases=["atobwhat", "a9lhhow"])
    async def a9lhrec(self, ctx):
        """Advice for b9stool with a9lh conflict"""
        embed = discord.Embed(title="arm9loaderhax Detected!", color=ConsoleColor.n3ds())
        embed.description = "A9LH + b9stool information"
        embed.add_field(name="Guide and Advice", value=cleandoc("""
                If you are seeing an "arm9loaderhax detected!" message in b9stool, you should attempt to boot into the luma configuration menu before simply pressing A. If you can access the config, you should follow the normal a9lh-to-b9s guide instead of using b9stool.

                If you appear to not actually have a9lh installed, you may press A to continue in b9stool. Once you do so and unlock NAND writing, one of two things will happen. If you reboot into an installer and then a luma config, you did actually have a9lh and it was successfully replaced with b9s. If you reboot to the home menu normally, you did not have a9lh and you should run b9stool again once.

                If you're seeing an "a9lh detected! brick avoided!" error, you are on an old version of b9stool and should update your boot.nds to the latest.
                """))
        await ctx.send(embed=embed)

    @commands.command()
    async def hmodders(self, ctx):
        """Links to approved hardmodder list"""
        await self.simple_embed(ctx, "Don't want to hardmod yourself? Ask one of the installers on the server! <https://pastebin.com/FAiczew4>")

    @commands.command(aliases=["ctrtransfer", "ctrnandtransfer"])
    async def ctr(self, ctx):
        """Links to ctrtransfer guide"""
        embed = discord.Embed(title="Guide - ctrtransfer", color=ConsoleColor.n3ds())
        embed.set_author(name="NH & Friends", url="https://3ds.hacks.guide/")
        embed.set_thumbnail(url="https://nintendohomebrew.com/pics/nhplai.png")
        embed.url = "https://3ds.hacks.guide/ctrtransfer"
        embed.description = "How to do the 11.5.0-38 ctrtransfer"
        await ctx.send(embed=embed)

    @commands.command()
    async def modmoon(self, ctx):
        """Links to a tool for a mod manager"""
        await self.simple_embed(ctx, cleandoc("""
                                To install mods for Smash 3DS, and to manage other LayeredFS mods, \
[Mod-Moon](https://github.com/Swiftloke/ModMoon/releases) is recommended.

                                Instructions for usage can be found [in this thread.](https://gbatemp.net/threads/modmoon-a-beautiful-simple-and-compact-mods-manager-for-the-nintendo-3ds.519080#)
                                """), color=ConsoleColor.n3ds())

    @commands.command()
    async def inoriwarn(self, ctx):
        """Warns users to keep the channels on-topic - Staff & Helper Declaration Only"""
        await self.simple_embed(ctx, """
                                **Please keep the channels clean and on-topic, further derailing will result in \
intervention.  A staff or helper will be the quickest route to resolution; you can \
contact available staff by private messaging the Mod-Mail bot.** A full list of staff \
and helpers can be found in #welcome-and-rules if you don't know who they are.
                                """)

    @commands.command()
    async def vguides(self, ctx):
        """Information about video guides relating to custom firmware"""
        embed = discord.Embed(title="Why you should not use video guides", color=discord.Color.dark_orange())
        embed.description = cleandoc("""
                Reasons to not use video guides:
                - Most uploaders do not edit their guides after uploading, even if there are mistakes
                - When methods become outdated, the information is not updated
                - Difficult to give assistance with
                - Most videos also refer to a pre-packaged download, which are often outdated and poorly organised
                """)
        embed.add_field(name="Recommended Solution", value="Read a trusted written tutorial. Try `.guide` for a list.")
        await ctx.send(embed=embed)

    @commands.command()
    async def vguides2(self, ctx):
        """Video Guides 2: Electric Boogaloo"""
        embed = discord.Embed(title="More information about video guides", color=discord.Color.dark_orange())
        embed.description = cleandoc("""
                Other problems with video guides:
                - Uploaders tend to care more about views than helping the community, so they don't remove old content
                - This usually leads to confusion about which method is best, or most current
                - Every uploader has a different route through each method, which often makes it very difficult to give assistance
                - Pre-packaged downloads are often hosted on the uploader's server, which they use to generate clicks and revenue
                - Pre-packaged downloads ("AIOs") are also very often outdated and not maintained by the creators
                """)
        embed.add_field(name="Recommended Solution", value="Read a trusted written tutorial. Try `.guide` for a list.")
        await ctx.send(embed=embed)

    @commands.command()
    async def ip(self, ctx):
        """How to check your IP"""
        embed = discord.Embed(title="Check your 3DSs IP (CFW)", color=ConsoleColor.n3ds())
        embed.description = "1. FBI\n2. Remote Install\n3. Receive URLs over the network"
        embed.add_field(name="Check your 3DSs IP (Homebrew)", value="1. Open Homebrew Launcher\n2. Press Y")
        await ctx.send(embed=embed)

    @commands.command()
    async def stock(self, ctx, console=None):
        """Advisory for various Nintendo systems on stock firmware"""
        systems = ("3ds", "nx", "ns", "switch")
        channel_name = ctx.channel.name if not isinstance(ctx.channel, discord.DMChannel) else ""
        if console not in systems:
            if channel_name.startswith(systems):
                console = "auto"
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")

                ctx.command.reset_cooldown(ctx)
                return
        if self.check_console(console, channel_name, '3ds'):
            embed = discord.Embed(title="Running stock (unmodified) 3DS firmware?", color=ConsoleColor.n3ds())
            embed.add_field(name="Hardware Dependant", value="The latest update to common guide methods mean that the best method for you now depends on what hardware you have. Please read the [guide](https://3ds.hacks.guide/get-started)", inline=False)
            await ctx.send(embed=embed)
        elif self.check_console(console, channel_name, ('nx', 'switch', 'ns')):
            await self.simple_embed(ctx,
            """
            Use [our guide](https://nh-server.github.io/switch-guide/user_guide/getting_started/) to determine if your Switch is a first-gen unit.
            **First generation consoles (RCM exploitable)**
            All of these can run [Atmosphere](https://nh-server.github.io/switch-guide/). Make sure that Atmosphere is compatible with the latest firmware version before you update.

            **Second generation consoles ("patched" units, Switch Lite, Mariko, etc.)**

            **"Old" Patched Switch (HAC-001)**: Do NOT update past 7.0.1. Units on 7.0.1 and below will eventually get CFW. Units on 8.0.0 and higher are not expected to be hacked and can be updated.
            **"New" Switch (HAC-001-01)**: Do NOT update past 8.0.1. Units on 8.0.1 and below will likely get homebrew. Units on 8.1.0 and higher are not expected to be hacked and can be updated.
            **Switch Lite (HDH-001)**: Do NOT update past 8.0.1. Units on 8.0.1 and below will likely get homebrew. Units on 8.1.0 and higher are not expected to be hacked and can be updated.

            Downgrading is **impossible** on patched consoles, and isn't worth your time on unpatched ones.
            """, title="Looking to hack your Switch?", color=ConsoleColor.switch())

    @commands.command()
    async def newver(self, ctx, console=None):
        """Quick advice for new versions"""
        systems = ("3ds", "nx", "ns", "switch")
        channel_name = ctx.channel.name if not isinstance(ctx.channel, discord.DMChannel) else ""
        if console not in systems:
            if channel_name.startswith(systems):
                console = "auto"
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")

                ctx.command.reset_cooldown(ctx)
                return

        if self.check_console(console, channel_name, '3ds'):
            embed = discord.Embed(title="Is the new 3DS update safe?", color=ConsoleColor.n3ds())
            embed.description = cleandoc("""
            Currently, the latest 3DS system firmware is `11.14.0-46`.

            If you currently have CFW installed (boot9strap/Luma):
            Is your Luma version up to date? If your Luma version is 10.2.1 or above, **updating is safe**.
            If it is 10.2 or below, please type `.update` in <#261581918653513729> and follow the information there.

            If you DO NOT currently have CFW installed (stock console):
            11.14.0-46 can be hacked with current methods. **Updating is safe**.
            *Last edited: November 16th, 2020*
            """)
            await ctx.send(embed=embed)

        elif self.check_console(console, channel_name, ('nx', 'switch', 'ns')):
            embed = discord.Embed(title="Is the new Switch update safe?", color=ConsoleColor.switch())
            embed.description = cleandoc(f"""
            Currently, the latest Switch system firmware is `{self.nx_firmware}`.

            If your Switch is **unpatched and can access RCM**:
            Atmosphere and Hekate currently support {self.nx_firmware}, and unpatched units will always be hackable.
            You should follow the precautions in our update guide, and always update Atmosphere and Hekate before updating the system firmware.

            If your Switch is **hardware patched and cannot access RCM**:
            Stay on the lowest possible firmware version. Any Switch that is patched and above 7.0.1 is unlikely to be hackable.
            *Last edited: {self.last_revision}*
            """)
            await ctx.send(embed=embed)

    @commands.command()
    async def what(self, ctx, console=None):
        """Links to 'what' style pages"""
        systems = ("3ds", "nx", "ns", "switch")
        channel_name = ctx.channel.name if not isinstance(ctx.channel, discord.DMChannel) else ""
        if console not in systems:
            if channel_name.startswith(systems):
                console = "auto"
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")

                ctx.command.reset_cooldown(ctx)
                return

        if self.check_console(console, channel_name, '3ds'):
            embed = discord.Embed(title="what?", color=ConsoleColor.n3ds())
            embed.set_thumbnail(url="https://eiphax.tech/assets/eip2.png")
            embed.url = "https://3ds.eiphax.tech/what.html"
            embed.description = "Basic things about the 3DS and CFW"
            await ctx.send(embed=embed)

        elif self.check_console(console, channel_name, ('nx', 'switch', 'ns')):
            embed = discord.Embed(title="The NX Nutshell", color=ConsoleColor.switch())
            embed.set_thumbnail(url="https://eiphax.tech/assets/eip2.png")
            embed.url = "https://nx.eiphax.tech/nutshell.html"
            embed.description = "Basic things about the Switch and CFW"
            await ctx.send(embed=embed)

    @commands.command()
    async def baninfo(self, ctx, console=None):
        """Links to ban information pages"""
        systems = ("3ds", "nx", "ns", "switch")
        channel_name = ctx.channel.name if not isinstance(ctx.channel, discord.DMChannel) else ""
        if console not in systems:
            if channel_name.startswith(systems):
                console = "auto"
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")

                ctx.command.reset_cooldown(ctx)
                return

        if self.check_console(console, channel_name, '3ds'):
            embed = discord.Embed(title="3DS Bans", color=ConsoleColor.n3ds())
            embed.description = cleandoc("""
            Nintendo has shown a marked lack of care about bans on the 3DS lately.
            However, such things as piracy and cheating online/cheating in multiplayer games have been known causes for NNID/console bans in the past.
            eShop fraud (eg credit card chargebacks) will also get you banned.

            You can enable online status and Spotpass/Streetpass as these do not seem to be high risk at this time.
            """)
            await ctx.send(embed=embed)

        elif self.check_console(console, channel_name, ('nx', 'switch', 'ns')):
            embed = discord.Embed(title="NX Bans", color=ConsoleColor.switch())
            embed.set_thumbnail(url="https://eiphax.tech/assets/gunther.png")
            embed.url = "https://nx.eiphax.tech/ban"
            embed.description = "Bans on the Switch are complicated. Please click the embed header link and read the linked page to learn more."
            await ctx.send(embed=embed)

    @commands.command()
    async def bigsd(self, ctx, console=None):
        """Embeds big sd information"""
        systems = ("3ds", "nx", "ns", "switch")
        channel_name = ctx.channel.name if not isinstance(ctx.channel, discord.DMChannel) else ""
        if console not in systems:
            if channel_name.startswith(systems):
                console = "auto"
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")

                ctx.command.reset_cooldown(ctx)
                return

        if self.check_console(console, channel_name, '3ds'):
            embed = discord.Embed(title="Big SD", color=ConsoleColor.n3ds())
            embed.description = cleandoc("""
            Although Nintendo says the official SD size limit is 32GB, the 3DS can accept cards up to 2TB.
            In order to use them, you will have to format them to FAT32 first.
            You can do this using these tools:

            -GUIFormat for Windows: http://ridgecrop.co.uk/index.htm?guiformat.htm
            -gparted for Linux: https://gparted.org/download.php
            -Disk Utility for macOS: https://support.apple.com/guide/disk-utility/format-a-disk-for-windows-computers-dskutl1010

            IMPORTANT: On macOS, always select "MS-DOS (Fat)". Formatting will erase all data on the card. Make a backup first.
            """)
            await ctx.send(embed=embed)

        elif self.check_console(console, channel_name, ('nx', 'switch', 'ns')):
            embed = discord.Embed(title="Big SD", color=ConsoleColor.switch())
            embed.description = cleandoc("""
            Although Nintendo supports large SD cards in EXFAT format, it is recommended to use FAT32.
            In order to change the card's format, you will need to use an external utility.
            Here are some suggestions:

            -GUIFormat for Windows: http://ridgecrop.co.uk/index.htm?guiformat.htm
            -gparted for Linux: https://gparted.org/download.php
            -Disk Utility for macOS: https://support.apple.com/guide/disk-utility/format-a-disk-for-windows-computers-dskutl1010

            IMPORTANT: On macOS, always select "MS-DOS (Fat)". Formatting will erase all data on the card. Make a backup first.
            """)
            await ctx.send(embed=embed)

    @commands.command()
    async def transfersd(self, ctx, console=None):
        """Embeds sd transfer information"""
        systems = ("3ds", "nx", "ns", "switch")
        channel_name = ctx.channel.name if not isinstance(ctx.channel, discord.DMChannel) else ""
        if console not in systems:
            if channel_name.startswith(systems):
                console = "auto"
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")

                ctx.command.reset_cooldown(ctx)
                return

        if self.check_console(console, channel_name, '3ds'):
            embed = discord.Embed(title="Moving SD Cards", color=ConsoleColor.n3ds())
            embed.description = cleandoc("""
            Moving SD cards on a 3DS is easy.
            First, ensure the new SD card is in the FAT32 format.
            If it is above 32GB, you will need to format it using one of these tools:

            -GUIFormat for Windows: http://ridgecrop.co.uk/index.htm?guiformat.htm
            -gparted for Linux: https://gparted.org/download.php
            -Disk Utility for macOS: https://support.apple.com/guide/disk-utility/format-a-disk-for-windows-computers-dskutl1010

            Once the new card is in FAT32, move all your content from the old SD to the new SD.
            IMPORTANT: On macOS, always select "MS-DOS (Fat)". Formatting will erase all data on the card. Make a backup first.
            IMPORTANT: Do not put the new SD card in the console before moving all your data to it.
            """)
            await ctx.send(embed=embed)

        elif self.check_console(console, channel_name, ('nx', 'switch', 'ns')):
            embed = discord.Embed(title="Moving SD cards", color=ConsoleColor.switch())
            embed.set_author(name="NH Discord Server", url="https://switchgui.de/switch-guide/")
            embed.set_thumbnail(url="https://i.imgur.com/CVSu1zc.png")
            embed.url = "https://switchgui.de/switch-guide/extras/transfer_sd/"
            embed.description = "A guide to moving SD cards with emuMMC"
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
        if self.check_console(console, channel_name, '3ds'):
            embed = discord.Embed(title="eip's problem solver packs", color=ConsoleColor.n3ds())
            embed.description = cleandoc("""
            Please visit the following page and read the information provided.
            https://3ds.eiphax.tech/catalyst.html
            """)
            await ctx.send(embed=embed)
        elif self.check_console(console, channel_name, ('nx', 'switch', 'ns')):
            embed = discord.Embed(title="eip's problem solver pack", color=ConsoleColor.switch())
            embed.description = cleandoc("""
            Please visit the following page and read the information provided.
            https://nx.eiphax.tech/catalyst.html
            """)
            await ctx.send(embed=embed)

    @commands.command()
    async def hbl(self, ctx):
        """Get Homebrew Launcher working on 11.4+ firmware"""
        await self.simple_embed(ctx, """
                                If you wish to access the Homebrew Launcher on 11.4+, you have two options.
                                First of all, you can use Steelminer, a free exploit to install the Homebrew Launcher. However, homebrew-only access has disadvantages.
                                For example, homebrew-only is often unstable and will crash unexpectedly. Also, it is limited in features and system access.
                                The second option is to install CFW, or custom firmware. Please use `.guide 3ds` for a list of ways to get CFW.
                                Here is a [Steelhax guide](https://git.io/fhbGY). Do NOT proceed to `Installing boot9strap` if you do not want CFW.
                                """)

    @commands.command()
    async def readguide(self, ctx):
        """Read the guide please"""
        await self.simple_embed(ctx, """
                                Asking something that is on the guide will make everyone lose time, so please read and \
re-read the guide steps 2 or 3 times before coming here.
                                """, title="Please read the guide")

    @commands.command(aliases=["atmos", "ams"])
    async def atmosphere(self, ctx):
        """Download link for the latest Atmosphère version"""
        embed = discord.Embed(title="Atmosphère", color=discord.Color.blue())
        embed.set_author(name="Atmosphère-NX Team", url="https://github.com/Atmosphere-NX")
        embed.set_thumbnail(url="https://avatars2.githubusercontent.com/u/37918415?s=200&v=4")
        embed.url = "https://github.com/Atmosphere-NX/Atmosphere/releases"
        embed.description = "Link to Atmosphère latest release"
        await ctx.send(embed=embed)

    @commands.command()
    async def hekate(self, ctx):
        """Download link for the latest Hekate version"""
        embed = discord.Embed(title="Hekate", color=discord.Color.red())
        embed.set_author(name="CTCaer", url="https://github.com/CTCaer")
        embed.set_thumbnail(url="https://imgur.com/kFEZyuC.png")
        embed.url = "https://github.com/CTCaer/hekate/releases/latest"
        embed.description = "Link to Hekate's latest release"
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

    SDFORMAT_TEXT = """
                Here are some links to common FAT32 formatting tools:
                • [GUIFormat](http://ridgecrop.co.uk/index.htm?guiformat.htm) (Windows)
                • [gparted](https://gparted.org/download.php) + [dosfstools](https://github.com/dosfstools/dosfstools) (Linux)
                • [Disk Utility](https://support.apple.com/guide/disk-utility/format-a-disk-for-windows-computers-dskutl1010) (MacOS)
                MacOS: Always select "MS-DOS (FAT)", even if the card is larger than 32GB."""

    @commands.command(aliases=["sdformat"])
    async def formatsd(self, ctx):
        """SD Format Tools"""
        await self.simple_embed(ctx, self.SDFORMAT_TEXT, title="SD Formatting Tools")

    @commands.command()
    async def lumabug(self, ctx):
        """Luma Black Screen Bug"""
        await self.simple_embed(ctx, """
                                If you have Luma3DS and your console is stuck on a black screen after you power it on, \
follow these steps:
                                1. Power off the console.
                                2. Take out any game cartridge, but leave the SD card in.
                                3. Power on the console.
                                4. Leave the console open and powered on for 10-15 minutes. Do not touch the console \
during this time.
                                If the console boots successfully in that time, the bug is now fixed and is unlikely to \
happen again. If the console still fails to boot to home menu, come back and ask for more help. Mention that you have \
already tried the Luma black screen process.
                                """, title="Luma Black Screen Bug")

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
    async def bfm4(self, ctx):
        """Information about BruteforceMovable and how the friend code may not always be needed"""
        await self.simple_embed(ctx, """
                                If BruteforceMovable is now at step 4, download your `movable.sed` and continue. \
You do not need to do anything more related to `movable_part1.sed`, Python, or the \
command line. The `movable.sed` is the final product and requires no further processing.
                                **You do not need to go back and get the friend code, or do anything more
                                with the friend code.
                                It does not matter if the friend does not add you back.
                                The bot already has your information and has removed you as a friend.**
                                """, title="BruteforceMovable Advice")

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
        if self.check_console(console, channel_name, '3ds'):
            embed = discord.Embed(title="EmuNAND for 3DS", color=ConsoleColor.n3ds())
            embed.description = cleandoc("""
            With the recent advances in hacking methods and safety, it is no longer recommended to use an emuNAND on a 3DS/2DS system.
            Generally, for most users, there is no reason or benefit to using an emuNAND on a 3DS/2DS system.
            If you do not know what an emuNAND is, or is used for, you do not need one.
            """)
            await ctx.send(embed=embed)
        elif self.check_console(console, channel_name, ('nx', 'switch', 'ns')):
            embed = discord.Embed(title="EmuMMC/EmuNAND for Switch", color=ConsoleColor.switch())
            embed.description = cleandoc("""
            On the Switch system, it is recommended to use an emuMMC/emuNAND.
            An emuMMC/emuNAND will take up approximately 30GB on your SD card, so the SD card must be 64GB or above.
            The purpose of an emuMMC/emuNAND is to give you a safe place to use custom firmware functions.
            This will allow you to keep your sysMMC/sysNAND clean, so you can use it online.
            Following the default NH server guide (type `.guide` for a link) will set you up with an emuMMC/emuNAND.
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

    @commands.command()
    async def ctrmount(self, ctx):
        """Failed to mount CTRNAND error"""
        await self.simple_embed(ctx, """
                                While following the guide, after installing boot9strap, if you get an error that says \
"Failed to mount CTRNAND", just continue on with the guide.
                                """, color=ConsoleColor.n3ds())

    @commands.command()
    async def emptysd(self, ctx):
        """What to do if you delete all your SD card contents"""
        await self.simple_embed(ctx, """
                                Please follow the directions on the 3DS Hacks Guide [Restoring CFW](https://3ds.hacks.guide/restoring-cfw) page.
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
                                If you already have CFW, use [TWLFix-CFW](https://github.com/MechanicalDragon0687/TWLFix-CFW/releases/)
                                If you already have homebrew but not CFW, use [TWLFix-3DS](https://github.com/MechanicalDragon0687/TWLFix-3DS/releases/)
                                If you have neither CFW nor homebrew, it is easier to get homebrew and use the previous option. You could also get a DSiWare app and follow: [TWLFix Stock](https://github.com/MechanicalDragon0687/TWLFix/wiki/Instructions/)
                                Each of these instructions require that you perform a system update after running the apps or restoring the DSiWare
                                """, title="Fix broken TWL", color=ConsoleColor.legacy())

    @commands.command(aliases=["redscr"])
    async def boot3dsx(self, ctx):
        """Download link for 3DS Homebrew Launcher, boot.3dsx"""
        await self.simple_embed(ctx, "The 3DS Homebrew Launcher, [boot.3dsx](https://github.com/fincs/new-hbmenu/releases/download/v2.1.0/boot.3dsx)")

    @commands.command(aliases=["greenscr", "bootnds"])
    async def b9stool(self, ctx):
        """Download link for B9STool, boot.nds"""
        await self.simple_embed(ctx, "The B9S installation tool for DSiWare exploits.\nB9STool, [boot.nds](https://github.com/zoogie/b9sTool/releases)")

    @commands.command(aliases=["faketiks"])
    async def faketik(self, ctx):
        """Download link for faketik"""
        await self.simple_embed(ctx, "3DS ticket spoofing utility, faketik: [faketik.3dsx](https://github.com/ihaveamac/faketik/releases)")

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
        if self.check_console(console, channel_name, '3ds'):
            await self.simple_embed(ctx, """
                            1. Navigate to the following folder on your SD card: \
`/Nintendo 3DS/(32 Character ID)/(32 Character ID)/extdata/00000000/`
                            2. Delete the corresponding folder for your region:
                              USA: `000002cd`
                              EUR: `000002ce`
                              JPN: `000002cc`
                              """, title="How to delete Home Menu Theme Data", color=ConsoleColor.n3ds())
        elif self.check_console(console, channel_name, ('nx', 'switch', 'ns')):
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
        embed.set_thumbnail(url="https://nintendohomebrew.com/pics/nhplai.png")
        embed.url = "https://3ds.hacks.guide/godmode9-usage"
        embed.description = "GodMode9 usage guide"
        await ctx.send(embed=embed)

    @commands.command()
    async def pminit(self, ctx):
        """Fix for the PM init failed error"""
        await self.simple_embed(ctx, """
                                If you are receiving a "PM init failed" error when attempting to launch safehax and \
are not on 11.3, use [this version of safehax.](https://github.com/TiniVi/safehax/releases/tag/r19)
                                """, color=ConsoleColor.n3ds())

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
            if self.check_console(x, channel_name, ('3ds',)):
                embed = discord.Embed(title="Virtual Console Injects for 3DS", color=ConsoleColor.n3ds())
                embed.set_author(name="Asdolo", url="https://gbatemp.net/members/asdolo.389539/")
                embed.set_thumbnail(url="https://i.imgur.com/rHa76XM.png")
                embed.url = "https://mega.nz/#!qnAE1YjC!q3FRHgIAVEo4nRI2IfANHJr-r7Sil3YpPYE4w8ZbUPY"
                embed.description = ("The recommended way to play old classics on your 3DS.\n"
                                     "Usage guide [here](http://3ds.eiphax.tech/nsui.html).")
                await ctx.send(embed=embed)
                continue

            if self.check_console(x, channel_name, ('wiiu', 'wii u')):
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
        if self.check_console(console, channel_name, '3ds'):
            embed = discord.Embed(title="GodMode9 dump/build Guide", color=ConsoleColor.n3ds())
            embed.set_author(name="NH & Friends", url="https://3ds.hacks.guide/dumping-titles-and-game-cartridges")
            embed.set_thumbnail(url="https://nintendohomebrew.com/pics/nhplai.png")
            embed.url = "https://3ds.hacks.guide/dumping-titles-and-game-cartridges"
            embed.description = "How to dump/build CIAs and Files using GodMode9"
            await ctx.send(embed=embed)
        elif self.check_console(console, channel_name, ('switch', 'nx', 'ns')):
            embed = discord.Embed(title="Switch dump/build Guide", color=ConsoleColor.switch())
            embed.set_author(name="SuchMeme", url="https://suchmememanyskill.github.io/guides/switchdumpguide/")
            embed.set_thumbnail(url="https://i.imgur.com/FkKB0er.png")
            embed.url = "https://suchmememanyskill.github.io/guides/switchdumpguide/"
            embed.description = ("How to dump/build NSPs using NXDumpTool\n"
                                 "BAN Warning: only for use using offline emummc")
            await ctx.send(embed=embed)
        elif self.check_console(console, channel_name, ('wiiu',)):
            embed = discord.Embed(title="Wii U dump/install Guide", color=ConsoleColor.wiiu())
            embed.set_author(name="NH Discord Server", url="https://wiiu.hacks.guide/#/dump-games")
            embed.set_thumbnail(url="https://i.imgur.com/CVSu1zc.png")
            embed.url = "https://wiiu.hacks.guide/#/dump-games"
            embed.description = "How to dump/install Wii U game discs using disc2app and WUP Installer GX2"
            await ctx.send(embed=embed)
        elif self.check_console(console, channel_name, 'vwii'):
            embed = discord.Embed(title="vWii dump Guide", color=ConsoleColor.wii())
            embed.set_author(name="NH Discord Server", url="https://wiiu.hacks.guide/#/dump-wii-games")
            embed.set_thumbnail(url="https://i.imgur.com/CVSu1zc.png")
            embed.url = "https://wiiu.hacks.guide/#/dump-wii-games"
            embed.description = "How to dump Wii game discs on vWii using CleanRip"
            await ctx.send(embed=embed)
        elif self.check_console(console, channel_name, 'dsi'):
            embed = discord.Embed(title="GodMode9i dump Guide", color=ConsoleColor.legacy())
            embed.set_author(name="NightScript", url="https://dsi.cfw.guide/dumping-game-cards")
            embed.url = "https://dsi.cfw.guide/dumping-game-cards"
            embed.description = "How to dump cartridges on a Nintendo DSi using GodMode9i"
            await ctx.send(embed=embed)

    @commands.command()
    async def cartinstall(self, ctx):
        """How to install 3DS cartridges to the SD card"""
        embed = discord.Embed(title="3DS Cart Install Guide", color=discord.Color(0x66FFFF))
        embed.set_author(name="Chroma Ryu", url="https://github.com/knight-ryu12/godmode9-layeredfs-usage/wiki/CartInstall-guide")
        embed.set_thumbnail(url="https://i.imgur.com/U8NA9lx.png")
        embed.url = "https://github.com/knight-ryu12/godmode9-layeredfs-usage/wiki/CartInstall-guide"
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

    @commands.command(aliases=["updateprep", "nxupdate"])
    async def nsupdate(self, ctx):
        """What you should do before updating a Nintendo Switch"""
        await self.simple_embed(ctx, cleandoc(f"""
                                     **Make sure your version of Atmosphere is up to date and that it supports the latest firmware**

                                     **Atmosphere {self.ams_ver} (latest release)**
                                     Supports up to firmware {self.nx_firmware}.

                                     *To find Atmosphere's version information, while booted into CFW, go into System Settings -> System, and look at \
the text under the System Update button. If it says that a system update is ready instead of displaying the CFW version, type .pendingupdate to learn \
how to delete it.*

                                     **Make sure your version of Hekate is up to date and that it supports the latest firmware**

                                     **Hekate {self.hekate_ver} (latest release)**
                                     Supports up to firmware {self.nx_firmware}.

                                     *To find Hekate's version information, once Hekate starts, look in the top left corner of the screen. If you use auto-boot, hold `volume -` to stop it.*

                                     **If you use a custom theme (Atmosphere 0.10.0 and above)**
                                     Delete or rename `/atmosphere/contents/0100000000001000` on your SD card prior to updating, \
as custom themes must be reinstalled for most firmware updates. **Note: On Atmosphere 0.9.4 or below, `contents` is called `titles`.**
                                """), title="What do I need to do before updating my system firmware when running CFW?", color=ConsoleColor.switch())

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

    @tutorial.command(aliases=["romhack", "romhacks"], cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def layeredfs(self, ctx):
        """How to use Luma 8.0+ LayeredFs"""
        embed = discord.Embed(title="LayeredFs Guide", color=discord.Color(0x66FFFF))
        embed.set_author(name="Chroma Ryu", url="https://github.com/knight-ryu12/godmode9-layeredfs-usage/wiki/Using-Luma3DS'-layeredfs-(Only-version-8.0-and-higher)")
        embed.set_thumbnail(url="https://i.imgur.com/U8NA9lx.png")
        embed.url = "https://github.com/knight-ryu12/godmode9-layeredfs-usage/wiki/Using-Luma3DS'-layeredfs-(Only-version-8.0-and-higher)"
        embed.description = "How to use Luma 8.0+ LayeredFs for ROM Hacking."
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
        embed.url = "https://wiki.ds-homebrew.com/ds-index/3ds-forwarders"
        embed.description = "Tutorial for NDS Forwarders"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["3dsvcextract"], cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def vcextract(self, ctx):
        """Links to 3DS Virtual Console Extraction Tutorial"""
        embed = discord.Embed(title="3DS VC Extraction Tutorial", color=ConsoleColor.n3ds())
        embed.set_author(name="Glazed_Belmont")
        embed.set_thumbnail(url="https://i.imgur.com/TgdOPkG.png")
        embed.url = "https://glazedbelmont.github.io/vcextract/"
        embed.description = "Basic tutorial to extract a rom out of your VC titles"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["wiiuvcextract"], cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def vcextractwiiu(self, ctx):
        """Links to Wii U Virtual Console Extraction Tutorial"""
        embed = discord.Embed(title="Wii U VC Extraction Tutorial", color=ConsoleColor.wiiu())
        embed.set_author(name="lendun, Lazr")
        embed.set_thumbnail(url="https://i.imgur.com/qXc4TY5.png")
        embed.url = "https://lendunistus.github.io/wiiuvcextract-guide/"
        embed.description = "Tutorial to extract a ROM out of your Wii U VC titles"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["gbabios"], cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def gbabiosdump(self, ctx):
        """Links to GBA Bios Extraction Tutorial"""
        embed = discord.Embed(title="GBA Bios Extraction Tutorial", color=discord.Color(0x551A8B))
        embed.set_author(name="Glazed_Belmont")
        embed.set_thumbnail(url="https://i.imgur.com/TgdOPkG.png")
        embed.url = "https://glazedbelmont.github.io/gbabiosdump/"
        embed.description = "Basic tutorial to extract a GBA bios"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["fuse-3ds", "fuse", "fuse3ds"], cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def ninfs(self, ctx):
        """Link to ninfs tutorial."""
        embed = discord.Embed(title="Extract and Decrypt games, NAND backups, and SD contents with ninfs", color=ConsoleColor.n3ds())
        embed.description = cleandoc("""
                            This is a tutorial that shows you how to use ninfs to extract the contents of games, \
NAND backups, and SD card contents. Windows, macOS, and Linux are supported.
                            """)
        embed.url = "https://gbatemp.net/threads/499994/"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["appatch", "dsscene"], cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def ap(self, ctx):
        """Anti-piracy patching guide"""
        embed = discord.Embed(title="AP Guide", color=ConsoleColor.legacy())
        embed.set_author(name="Glazed_Belmont")
        embed.set_thumbnail(url="https://i.imgur.com/TgdOPkG.png")
        embed.url = "https://glazedbelmont.github.io/appatching/"
        embed.description = "An AP-Patching guide"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["cheats", "3dscheats"], cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def cpcheats(self, ctx):
        """Checkpoint/Rosalina cheat guide"""
        embed = discord.Embed(title="3DS Cheats Guide", color=discord.Color.purple())
        embed.set_author(name="Krieg")
        embed.set_thumbnail(url="https://3ds.eiphax.tech/pic/krieg.png")
        embed.url = "https://3ds.eiphax.tech/cpcheats.html"
        embed.description = "A guide to using cheats with Checkpoint and Rosalina"
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
        if self.check_console(console, channel_name, "3ds"):
            embed.title = "3DS FTP Guide"
            embed.url = "https://3ds.eiphax.tech/ftp.html"
        elif self.check_console(console, channel_name, ("nx", "ns", "switch")):
            embed.title = "Switch FTP Guide"
            embed.url = "https://nx.eiphax.tech/ftp.html"
        embed.colour = discord.Color.purple()
        embed.set_author(name="Krieg")
        embed.set_thumbnail(url="https://3ds.eiphax.tech/pic/krieg.png")
        embed.description = "A guide to using ftp with FTPD and WinSCP"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["ntrplugins"], cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def plugins(self, ctx):
        """NTR Plugins guide"""
        embed = discord.Embed(title="3DS NTR Plugins Guide", color=discord.Color.purple())
        embed.set_author(name="Krieg")
        embed.set_thumbnail(url="https://3ds.eiphax.tech/pic/krieg.png")
        embed.url = "https://3ds.eiphax.tech/ntrplugins"
        embed.description = "A guide to using plugins with NTR"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["citraobs"], cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def obscitra(self, ctx):
        """OBS and Citra guide"""
        embed = discord.Embed(title="OBS and Citra Guide", color=discord.Color.purple())
        embed.set_author(name="Krieg")
        embed.set_thumbnail(url="https://3ds.eiphax.tech/pic/krieg.png")
        embed.url = "https://kriegisrei.github.io/obscitra/"
        embed.description = "A guide to recording Citra with OBS"
        await ctx.send(embed=embed)

    @tutorial.command(cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def gbadump(self, ctx):
        """Links to GBA Dump guide"""
        embed = discord.Embed(title="Dumping GBA games", color=discord.Color.purple())
        embed.set_thumbnail(url="https://wiki.no-intro.org/resources/assets/wiki.png")
        embed.url = "https://wiki.no-intro.org/index.php?title=Game_Boy_Advance_Dumping_Guide"
        embed.description = "How to dump GBA cartridges"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["carttodigitalsave", "ctdsave"])
    async def transfersave(self, ctx):
        """Links to cart to digital version save transfer tutorial"""
        embed = discord.Embed(title="Cart to digital version save transfer tutorial", color=discord.Color.purple())
        embed.url = "https://redkerry135.github.io/transfersave/"
        embed.description = "A tutorial about how to transfer a save from the cart version of a game to a digital version of that game."
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
        if self.check_console(console, channel_name, '3ds'):
            embed = discord.Embed(title="3DS Themes Tutorial", color=discord.Color.dark_orange())
            embed.url = "https://itspizzatime1501.github.io/guides/themes/"
            embed.description = "Tutorial for installing themes on the 3DS"
            await ctx.send(embed=embed)
        elif self.check_console(console, channel_name, ('nx', 'switch', 'ns')):
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
    async def tinydb(self, ctx):
        """Community-maintained homebrew database"""
        embed = discord.Embed(title="Tinydb", color=discord.Color.green())
        embed.set_author(name="DeadPhoenix")
        embed.set_thumbnail(url="https://files.frozenchen.cl/kNJz8.png")
        embed.url = "http://tinydb.eiphax.tech"
        embed.description = "A Community-maintained homebrew database"
        await ctx.send(embed=embed)

    @commands.command(aliases=["tinydbsearch"])
    @commands.cooldown(rate=1, per=15.0, type=commands.BucketType.channel)
    async def tinysearch(self, ctx, *, app=""):
        """Search for your favorite homebrew app in tinydb"""
        if not app or app.startswith("..") or "/.." in app:
            return await ctx.send("Enter a search term to search for applications.")
        encodedapp = urllib.parse.quote(app)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"https://api.homebrew.space/search/{encodedapp}", timeout=2) as resp:
                    response = await resp.json()
            except (aiohttp.ServerConnectionError, aiohttp.ClientConnectorError, aiohttp.ClientResponseError, asyncio.TimeoutError):
                return await ctx.send("I can't connect to tinydb 💢")
        if response and len(response) > 0:
            release = response[0]['latestRelease']['3ds_release_files'][0]
            embed = discord.Embed(title=response[0]['name'], image=f"https://api.homebrew.space/qr/{response[0]['id']}/", description=f"{response[0]['description']}\n [[Download]({release['download_url']})] [[Source](https://github.com/{response[0]['github_owner']}/{response[0]['github_repository']})]")
            embed.set_image(url=rf"https://api.homebrew.space/qr/{response[0]['id']}/")
            embed.set_footer(text=f"by {response[0]['github_owner']}")
            return await ctx.send(embed=embed)
        return await ctx.send(f"Couldnt find {self.bot.escape_text(app)} in tinydb!")

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

    @commands.command(aliases=['whatsid0', 'id0'])
    async def whatisid0(self, ctx):
        """Picture to say what the heck is the id0"""
        embed = discord.Embed()
        embed.set_image(url="https://media.discordapp.net/attachments/196635695958196224/677996125034250280/unknown-76.png")
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

    @commands.command(aliases=['switchserial'])
    async def serial(self, ctx):
        """Picture to show what the hell a serial is"""
        embed = discord.Embed(title="Don't know where your Switch's serial is?", color=ConsoleColor.switch())
        embed.description = "This is where the serial is located. Use this number to check if you are patched."
        embed.set_image(url="https://i.imgur.com/03NfeFN.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def exfat(self, ctx):
        """exFAT on Switch: why not to use it"""
        reasons = """
                The recommended filesystem format for the Switch is FAT32.

                While the Switch supports exFAT through an additional update from Nintendo, here are reasons not to use it:

                * CFW may fail to boot due to a missing exFAT update in Horizon
                * This filesystem is prone to corruption.
                * Nintendo doesn't use files larger than 4GB, even with large games and exFAT.
                """

        await self.simple_embed(ctx, f"{reasons}{self.SDFORMAT_TEXT}", title="exFAT on Switch: Why you shouldn't use it")

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

    @commands.command(aliases=['ntrboot', 'ntrcartlist', 'ntrbootcartlist'])
    async def ntrcart(self, ctx):
        imagelink = "https://i.imgur.com/duMthYp.png"
        title = "Which flashcarts work with NTRBoot?"
        embed = discord.Embed(title=title, color=ConsoleColor.n3ds())
        embed.set_image(url=imagelink)
        embed.description = "To see an always up to date list of compatible flashcarts go to https://3ds.hacks.guide/ntrboot"
        await ctx.send(embed=embed)

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
        Make sure you have a [payload.elf](https://github.com/wiiu-env/homebrew_launcher_installer/releases/latest) in the wiiu folder.""",
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
        if self.check_console(console, channel_name, '3ds'):
            embed = discord.Embed(title="3DS Database", color=ConsoleColor.n3ds())
            embed.url = "http://3dsdb.com/"
            embed.description = "3DS database for game releases."
            await ctx.send(embed=embed)
        elif self.check_console(console, channel_name, ('nx', 'switch', 'ns')):
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

    @commands.command(aliases=['systransfer'])
    async def transfer(self, ctx):
        """If you want to keep homebrew apps when doing a system transfer:"""
        embed = discord.Embed(title="What to do if you want to keep homebrew apps during a system transfer", color=ConsoleColor.n3ds())
        embed.description = "Keeping Homebrew Apps after system transfer"
        embed.add_field(name="Steps to system transfer", value=cleandoc("""
                1. Install CFW on the new console using [3ds.hacks.guide](https://3ds.hacks.guide/)
                2. Do a system transfer by navigating to system settings, other settings, system transfer.
                3. If prompted, choose a PC-Based Transfer.
                4. To access the Homebrew Launcher on the new console, do `Section III - Homebrew Launcher` in [Finalizing Setup](https://3ds.hacks.guide/finalizing-setup)
                5. On the console you transfered to, run [faketik](https://github.com/ihaveamac/faketik/releases) in the Homebrew Launcher.
                6. Your Homebrew apps should appear on the homescreen!
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


def setup(bot):
    bot.add_cog(Assistance(bot))
