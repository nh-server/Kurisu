import aiohttp
import discord
import urllib.parse

from utils.checks import check_if_user_can_sr
from discord.ext import commands
from inspect import cleandoc


class Assistance(commands.Cog, command_attrs=dict(cooldown=commands.Cooldown(1, 30.0, commands.BucketType.channel))):
    """
    Commands that will mostly be used in the help channels.
    """
    def __init__(self, bot):
        self.bot = bot
        self.systems = ("3ds", "wiiu", "vwii", "switch", "nx", "ns", "wii", "dsi", "legacy")

    async def simple_embed(self, ctx, text, title="", color=discord.Color.default()):
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
        # await ctx.send("Request sent.")
        msg = f"❗️ **Assistance requested**: {ctx.channel.mention} by {author.mention} | {str(author)} @here"
        if msg_request != "":
            # msg += "\n✏️ __Additional text__: " + msg_request
            embed = discord.Embed(color=discord.Color.gold())
            embed.description = msg_request
        await self.bot.channels['mods'].send(msg, embed=(embed if msg_request != "" else None))
        try:
            await author.send(f"✅ Online staff have been notified of your request in {ctx.channel.mention}.", embed=(embed if msg_request != "" else None))
        except discord.errors.Forbidden:
            pass

    @commands.guild_only()
    @commands.command()
    async def guide(self, ctx, *, consoles=""):
        """Links to the recommended guides."""
        consoleslist = {x for x in consoles.split() if x in self.systems}
        if not consoleslist:
            if ctx.channel.name.startswith(self.systems):
                consoleslist = ['auto']
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in self.systems])}.")
                return
        for x in consoleslist:
            if self.check_console(x, ctx.channel.name, '3ds'):
                embed = discord.Embed(title="Guide", color=discord.Color(0xCE181E))
                embed.set_author(name="Plailect", url="https://3ds.hacks.guide/")
                embed.set_thumbnail(url="https://3ds.hacks.guide/images/bio-photo.png")
                embed.url = "https://3ds.hacks.guide/"
                embed.description = "A complete guide to 3DS custom firmware, from stock to boot9strap."
                await ctx.send(embed=embed)
                continue
            if self.check_console(x, ctx.channel.name, ('wiiu',)):
                embed = discord.Embed(title="Guide", color=discord.Color(0x009AC7))
                embed.set_author(name="NH Discord Server", url="https://wiiu.hacks.guide/")
                embed.set_thumbnail(url="https://i.imgur.com/CVSu1zc.png")
                embed.url = "https://wiiu.hacks.guide/"
                embed.description = "A complete Wii U custom firmware + coldboothax guide"
                await ctx.send(embed=embed)
                continue
            if self.check_console(x, ctx.channel.name, ('vwii',)):
                embed = discord.Embed(title="Guide", color=discord.Color(0xFFFFFF))
                embed.set_author(name="NH Discord Server", url="https://wiiu.hacks.guide/#/vwii-modding")
                embed.set_thumbnail(url="https://i.imgur.com/FclGzNz.png")
                embed.url = "https://wiiu.hacks.guide/#/vwii-modding"
                embed.description = "A complete vWii modding guide"
                await ctx.send(embed=embed)
                continue
            if self.check_console(x, ctx.channel.name, ('switch', 'nx', 'ns')):
                embed = discord.Embed(title="Guide", color=discord.Color(0xCB0004))
                embed.set_author(name="NH Discord Server", url="https://nh-server.github.io/switch-guide/")
                embed.set_thumbnail(url="https://i.imgur.com/CVSu1zc.png")
                embed.url = "https://nh-server.github.io/switch-guide/"
                embed.description = "A Switch guide from stock to Atmosphere"
                await ctx.send(embed=embed)
                continue
            if self.check_console(x, ctx.channel.name, ('legacy', 'wii')):
                embed = discord.Embed(title="Guide", color=discord.Color(0x009AC7))
                embed.set_author(name="tj_cool", url="https://sites.google.com/site/completesg/")
                embed.set_thumbnail(url="https://i.imgur.com/KI6IXmm.png")
                embed.url = "https://sites.google.com/site/completesg/"
                embed.description = "A complete original Wii softmod guide"
                await ctx.send(embed=embed)
            if self.check_console(x, ctx.channel.name, ('legacy', 'dsi')):
                embed = discord.Embed(title="Guide", color=discord.Color(0xCB0004))
                embed.set_author(name="jerbear64 & emiyl", url="https://dsi.cfw.guide/")
                embed.set_thumbnail(url="https://i.imgur.com/T227BW0.png")
                embed.url = "https://dsi.cfw.guide/"
                embed.description = "A complete Nintendo DSi homebrew guide, from stock to HiyaCFW"
                await ctx.send(embed=embed)

    @commands.command(aliases=['finalizing', 'finalising', 'finalise'])
    async def finalize(self, ctx):
        """Finalizing Setup"""
        await self.simple_embed(ctx, """
                    3DS Hacks Guide's [Finalizing Setup](https://3ds.hacks.guide/finalizing-setup)
                    """, title="Finalizing Setup")

    # Embed to Soundhax Download Website
    @commands.command()
    async def soundhax(self, ctx):
        """Links to Soundhax Website"""
        embed = discord.Embed(title="Soundhax", color=discord.Color.blue())
        embed.set_author(name="Ned Williamson", url="http://soundhax.com/")
        embed.set_thumbnail(url="http://i.imgur.com/lYf0jan.png")
        embed.url = "http://soundhax.com"
        embed.description = "Free 3DS Primary Entrypoint <= 11.3"
        await ctx.send(embed=embed)

    # dsp dumper command
    @commands.command()
    async def dsp(self, ctx):
        """Links to Dsp1."""
        embed = discord.Embed(title="Dsp1", color=discord.Color.green())
        embed.set_author(name="zoogie", url="https://github.com/zoogie", icon_url="https://gbatemp.net/data/avatars/l/357/357147.jpg?1426471484")
        embed.description = "Dump 3DS's DSP component to SD for homebrew audio."
        embed.set_thumbnail(url="https://raw.githubusercontent.com/Cruel/DspDump/master/icon.png")
        embed.url = "https://github.com/zoogie/DSP1/releases"
        await ctx.send(embed=embed)

    @commands.command(aliases=['snickerstream'])
    async def ntrstream(self, ctx):
        """Snickerstream/NTR streaming guide"""
        embed = discord.Embed(title="Snickerstream: NTR Streaming Client", color=discord.Color.blue())
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

    @commands.guild_only()
    @commands.command()
    async def update(self, ctx, *, consoles=""):
        """Explains how to safely prepare for an update for a hacked console"""

        systems = ('3ds', 'nx', 'ns', 'switch')
        wanted_consoles = list(set(x for x in consoles.split() if x in systems))

        if not wanted_consoles:
            if ctx.channel.name.startswith(systems):
                wanted_consoles = ["auto"]
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}")
                return

        for console in wanted_consoles:
            if self.check_console(console, ctx.channel.name, "3ds"):
                await self.simple_embed(ctx,
                    "**Is it safe to update to current 3DS firmware?**\n\n"

                    "**Luma3DS 9.1 and above**\n"
                    "You can update safely.\n\n"
                
                    "**Luma3DS 8.0 - 9.0**\n"
                    "Follow the [manual Luma3DS update guide](https://gist.github.com/chenzw95/3b5b953c9c913e89fdda3c4c4d98d086), then you can update safely. Being on these Luma3DS "
                    "versions on 11.8+ will cause an error screen until you update.\n\n"
                
                    "**Luma3DS 7.1**\n"
                    "Follow the [B9S upgrade guide](https://3ds.hacks.guide/updating-b9s)\n\n"
                
                    "**Luma3DS 7.0.5 and below**\n"
                    "Follow the [a9lh-to-b9s guide](https://3ds.hacks.guide/a9lh-to-b9s)\n\n"
                 
                    "**To find out your Luma3DS version, hold select on bootup and look at the top left corner of the top screen**\n"
                )

            elif self.check_console(console, ctx.channel.name, ("switch", "nx", "ns")):
                embed = discord.Embed(title="Updating Guide", color=discord.Color(0xCB0004))
                embed.set_author(name="NH Discord Server", url="https://nh-server.github.io/switch-guide/")
                embed.set_thumbnail(url="https://i.imgur.com/CVSu1zc.png")
                embed.url = "https://nh-server.github.io/switch-guide/extras/updating/"
                embed.description = "A guide and general recommendations for updating your switch with emuMMC."
                await ctx.send(embed=embed)

    @commands.command(aliases=["checkluma"])
    @commands.cooldown(rate=1, per=15.0, type=commands.BucketType.channel)
    async def lumacheck(self, ctx):
        """How to check Luma version"""
        embed = discord.Embed(title="Please check your Luma version.", color=discord.Color.blue())
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
        embed = discord.Embed(title="How to create a 3DS NAND backup without enough space on the SD card", color=discord.Color.blue())
        embed.add_field(name="Steps to create the backup", value=cleandoc("""
                1. Copy the Nintendo 3DS folder from the root of your SD card to your computer then delete it from **the SD card.**
                2. Boot GodMode9 by holding START on boot then preform a normal NAND backup. After that, power off the system.
                3. Copy the files in gm9/out on your SD card to a safe spot on your computer. Then, delete the files from **the SD card.**
                4. Copy the Nintendo 3DS folder to your SD card root then delete it **from your computer.**
                """))
        await ctx.send(embed=embed)

    @commands.command()
    async def cfwuses(self, ctx):
        """Links to eiphax cfw uses page"""
        await self.simple_embed(ctx, "Want to know what CFW can be used for? <https://3ds.eiphax.tech/tips.html>")

    @commands.command()
    async def updateb9s(self, ctx):
        """Links to the guide for updating b9s versions"""
        embed = discord.Embed(title="Updating B9S Guide", color=discord.Color(0xCE181E))
        embed.set_author(name="Plailect", url="https://3ds.hacks.guide/updating-b9s")
        embed.set_thumbnail(url="https://3ds.hacks.guide/images/bio-photo.png")
        embed.url = "https://3ds.hacks.guide/updating-b9s"
        embed.description = "A guide for updating to new B9S versions."
        await ctx.send(embed=embed)

    @commands.command()
    async def updateluma(self, ctx):
        """Links to the guide for updating Luma3DS manually (8.0 or later)"""
        embed = discord.Embed(title="Manually Updating Luma3DS", color=discord.Color(0xCE181E))
        embed.set_author(name="Chenzw", url="https://gist.github.com/chenzw95/3b5b953c9c913e89fdda3c4c4d98d086")
        embed.set_thumbnail(url="https://avatars0.githubusercontent.com/u/5243259?s=400&v=4")
        embed.url = "https://gist.github.com/chenzw95/3b5b953c9c913e89fdda3c4c4d98d086"
        embed.description = "A guide for manually updating Luma3ds. This is necessary if you receive the \"Failed to apply 1 Firm patch(es)\" error."
        await ctx.send(embed=embed)

    @commands.command(aliases=["a9lhtob9s", "updatea9lh"])
    async def atob(self, ctx):
        """Links to the guide for updating from a9lh to b9s"""
        embed = discord.Embed(title="Upgrading a9lh to b9s", color=discord.Color(0xCE181E))
        embed.set_author(name="Plailect", url="https://3ds.hacks.guide/a9lh-to-b9s")
        embed.set_thumbnail(url="https://3ds.hacks.guide/images/bio-photo.png")
        embed.url = "https://3ds.hacks.guide/a9lh-to-b9s"
        embed.description = "A guide for upgrading your device from arm9loaderhax to boot9strap."
        await ctx.send(embed=embed)

    @commands.command(aliases=["atobwhat", "a9lhhow"])
    async def a9lhrec(self, ctx):
        """Advice for b9stool with a9lh conflict"""
        embed = discord.Embed(title="arm9loaderhax Detected!", color=discord.Color.blue())
        embed.description = "A9LH + b9stool information"
        embed.add_field(name="Guide and Advice", value=cleandoc("""
                If you are seeing an "arm9loaderhax detected!" message in b9stool, you should attempt to boot into the luma configuration menu before simply pressing A. If you can access the config, you should follow the normal a9lh-to-b9s guide instead of using b9stool.
                
                If you appear to not actually have a9lh installed, you may press A to continue in b9stool. Once you do so and unlock NAND writing, one of two things will happen. If you reboot into an installer and then a luma config, you did actually have a9lh and it was successfully replaced with b9s. If you reboot to the home menu normally, you did not have a9lh and you should run b9stool again once.
                
                If you're seeing an "a9lh detected! brick avoided!" error, you are on an old version of b9stool and should update your boot.nds to the latest.
                """))
        await ctx.send(embed=embed)

    # Hardmodder pastebin list
    @commands.command()
    async def hmodders(self, ctx):
        """Links to approved hardmodder list"""
        await self.simple_embed(ctx, "Don't want to hardmod yourself? Ask one of the installers on the server! <https://pastebin.com/FAiczew4>")

    # Links to ctrtransfer guide
    @commands.command(aliases=["ctrtransfer", "ctrnandtransfer"])
    async def ctr(self, ctx):
        """Links to ctrtransfer guide"""
        embed = discord.Embed(title="Guide - ctrtransfer", color=discord.Color.orange())
        embed.set_author(name="Plailect", url="https://3ds.hacks.guide/")
        embed.set_thumbnail(url="https://3ds.hacks.guide/images/bio-photo.png")
        embed.url = "https://3ds.hacks.guide/ctrtransfer"
        embed.description = "How to do the 11.5.0-38 ctrtransfer"
        await ctx.send(embed=embed)

    @commands.command()
    async def modmoon(self, ctx):
        """Links to a tool for a mod manager"""
        await self.simple_embed(ctx, cleandoc("""
                                To install mods for Smash 3DS, and to manage other LayeredFS mods, \
[Mod-Moon](https://github.com/Swiftloke/ModMoon/releases) is recommended. Instructions for use can be found on the page.
                                """))

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
                - They get outdated quickly
                - Tough to update and give assistance for
                - Can be misinformative and dangerous for the console
                """)
        embed.add_field(name="Recommended Solution", value="Read a trusted written tutorial. Try `.guide` for a list.")
        await ctx.send(embed=embed)

    @commands.command()
    async def vguides2(self, ctx):
        """Information about video guides relating to custom firmware"""
        await ctx.send("https://www.youtube.com/watch?v=miVDKgInzyg")

    @commands.command()
    async def ip(self, ctx):
        """How to check your IP"""
        embed = discord.Embed(title="Check your 3DSs IP (CFW)", color=discord.Color.dark_orange())
        embed.description = "1. FBI\n2. Remote Install\n3. Receive URLs over the network"
        embed.add_field(name="Check your 3DSs IP (Homebrew)", value="1. Open Homebrew Launcher\n2. Press Y")
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def stock(self, ctx, console=None):
        """Advisory for various Nintendo systems on stock firmware"""
        systems = ("3ds", "nx", "ns", "switch")
        if console not in systems:
            if ctx.channel.name.startswith(systems):
                console = "auto"
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")
                return
        if self.check_console(console, ctx.message.channel.name, '3ds'):
            embed = discord.Embed(title="Running stock (unmodified) 11.4+ firmware?", color=discord.Color.dark_orange())
            embed.add_field(name="NTRBoot", value="Requires a compatible NDS flashcart and maybe an additional DS(i) or hacked 3DS console depending on the flashcart (All versions, all hardware). [Guide](https://3ds.hacks.guide/ntrboot)", inline=False)
            embed.add_field(name="Seedminer", value="Requires a working NDS mode or Pokémon Picross (free from eshop) [Guide](https://3ds.hacks.guide/seedminer)", inline=False)
            embed.add_field(name="Hardmod", value="Requires soldering **Not for beginners!**. [Guide](https://git.io/fhQk9)", inline=False)
            await ctx.send(embed=embed)
        elif self.check_console(console, ctx.message.channel.name, ('nx', 'switch', 'ns')):
            embed = discord.Embed(title="Looking to hack your Switch?", color=0xe60012)
            embed.description = cleandoc("""
            Use [our guide](https://nh-server.github.io/switch-guide/user_guide/getting_started/) to determine if your Switch is a first-gen unit.
            **First generation consoles (RCM exploitable)**
            All of these can run [Atmosphere](https://nh-server.github.io/switch-guide/). Make sure that Atmosphere is compatible with the latest firmware version before you update.

            **Second generation consoles ("patched" units, Switch Lite, Mariko, etc.)**

            **"Old" Patched Switch (HAC-001)**: Do NOT update past 7.0.1. Units on 7.0.1 and below will eventually get CFW. Units on 8.0.0 and higher are not expected to be hacked and can be updated.
            **"New" Switch (HAC-001-01)**: Do NOT update past 8.0.1. Units on 8.0.1 and below will likely get homebrew. Units on 8.1.0 and higher are not expected to be hacked and can be updated.
            **Switch Lite (HDH-001)**: Do NOT update past 8.0.1. Units on 8.0.1 and below will likely get homebrew. Units on 8.1.0 and higher are not expected to be hacked and can be updated.

            Downgrading is **impossible** on patched consoles, and isn't worth your time on unpatched ones.
            """)
            await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def newver(self, ctx, console=None):
        """Quick advice for new versions"""
        systems = ("3ds", "nx", "ns", "switch")
        if console not in systems:
            if ctx.channel.name.startswith(systems):
                console = "auto"
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")
                return

        if self.check_console(console, ctx.message.channel.name, '3ds'):
            embed = discord.Embed(title="Is the new 3DS update safe?", color=0xe60012)
            embed.description = cleandoc("""
            Currently, the latest 3DS system firmware is `11.13.0-45`.
            
            If you currently have CFW installed (boot9strap/Luma):
            Is your Luma version up to date? If your Luma version is 9.1 or above, **updating is safe**.
            If it is 9.0 or below, please type `.update` in <#261581918653513729> and follow the information there.
            
            If you DO NOT currently have CFW installed (stock console):
            11.13.0-45 can be hacked with current methods. **Updating is safe**.
            *Last edited: December 3, 2019*
            """)
            await ctx.send(embed=embed)

        elif self.check_console(console, ctx.message.channel.name, ('nx', 'switch', 'ns')):
            embed = discord.Embed(title="Is the new Switch update safe?", color=0xe60012)
            embed.description = cleandoc("""
            Currently, the latest Switch system firmware is `10.0.4`.

            If your Switch is **unpatched and can access RCM**:
            Atmosphere and Hekate currently support 10.0.4, and unpatched units will always be hackable.
            You should follow the precautions in our update guide, and always update Atmosphere and Hekate before updating the system firmware.
            
            If your Switch is **hardware patched and cannot access RCM**:
            Stay on the lowest possible firmware version. Any Switch that is patched and above 7.0.1 is unlikely to be hackable.
            *Last edited: June 5, 2020*
            """)
            await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def what(self, ctx, console=None):
        """Links to 'what' style pages"""
        systems = ("3ds", "nx", "ns", "switch")
        if console not in systems:
            if ctx.channel.name.startswith(systems):
                console = "auto"
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")
                return

        if self.check_console(console, ctx.message.channel.name, '3ds'):
            embed = discord.Embed(title="what?", color=discord.Color.purple())
            embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/250051871962562562/726ae27792fc496755805397722c1e8e.png?size=1024")
            embed.url = "https://3ds.eiphax.tech/what.html"
            embed.description = "Basic things about the 3DS and CFW"
            await ctx.send(embed=embed)

        elif self.check_console(console, ctx.message.channel.name, ('nx', 'switch', 'ns')):
            embed = discord.Embed(title="The NX Nutshell", color=discord.Color.purple())
            embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/250051871962562562/726ae27792fc496755805397722c1e8e.png?size=1024")
            embed.url = "https://nx.eiphax.tech/nutshell.html"
            embed.description = "Basic things about the Switch and CFW"
            await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def catalyst(self, ctx, console=None):
        """Link to problem solvers"""
        systems = ("3ds", "nx", "ns", "switch")
        if not console:
            if ctx.channel.name.startswith(systems):
                console = "auto"
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")
                return
        if self.check_console(console, ctx.message.channel.name, '3ds'):
            embed = discord.Embed(title="eip's problem solver packs", color=0xe60012)
            embed.description = cleandoc("""
            Please visit the following page and read the information provided.
            https://3ds.eiphax.tech/catalyst.html
            """)
            await ctx.send(embed=embed)
        elif self.check_console(console, ctx.message.channel.name, ('nx', 'switch', 'ns')):
            embed = discord.Embed(title="eip's problem solver pack", color=0xe60012)
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
        embed.url = "https://github.com/Atmosphere-NX/Atmosphere/releases/latest"
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

    # Why various Switch cfws aren't supported or recommended
    @commands.guild_only()
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
            return
        await self.simple_embed(ctx, info['info'], title=f"Why {info['title']} isn't recommended")

    @commands.command(aliases=["sderror", "sderrors", "bigsd", "sd"])
    async def sdguide(self, ctx):
        """SD Troubleshooter"""
        await self.simple_embed(ctx, """
                    Need to do something with your SD card? Find advice in [this guide](https://3ds.eiphax.tech/sd.html)
                    """, title="SD Troubleshooter")

    SDFORMAT_TEXT = """
                Here are some links to common FAT32 formatting tools:
                • [GUIFormat](http://www.ridgecrop.demon.co.uk/index.htm?guiformat.htm) (Windows)
                • [gparted](https://gparted.org/download.php) (Linux)
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
        embed = discord.Embed(title="Troubleshooting guide for most Seedminer-based methods", color=discord.Color(0xA2BAE0))
        embed.url = "https://3ds.eiphax.tech/issues.html"
        embed.description = "A simple troubleshooting guide for common CFW and homebrew installation issues \n when using Seedminer-based methods."
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

    @commands.guild_only()
    @commands.command()
    async def emureco(self, ctx, console=None):
        """Quick advice for emunands"""
        systems = ("3ds", "nx", "ns", "switch")
        if console not in systems:
            if ctx.channel.name.startswith(systems):
                console = "auto"
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")
                return
        if self.check_console(console, ctx.message.channel.name, '3ds'):
            embed = discord.Embed(title="EmuNAND for 3DS", color=0xe60012)
            embed.description = cleandoc("""
            With the recent advances in hacking methods and safety, it is no longer recommended to use an emuNAND on a 3DS/2DS system.
            Generally, for most users, there is no reason or benefit to using an emuNAND on a 3DS/2DS system.
            If you do not know what an emuNAND is, or is used for, you do not need one.
            """)
            await ctx.send(embed=embed)
        elif self.check_console(console, ctx.message.channel.name, ('nx', 'switch', 'ns')):
            embed = discord.Embed(title="EmuMMC/EmuNAND for Switch", color=0xe60012)
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
                                 """, color=discord.Color(0x009AC7))

    @commands.command()
    async def ctrmount(self, ctx):
        """Failed to mount CTRNAND error"""
        await self.simple_embed(ctx, """
                                While following the guide, after installing boot9strap, if you get an error that says \
"Failed to mount CTRNAND", just continue on with the guide.
                                """)

    @commands.command()
    async def emptysd(self, ctx):
        """What to do if you delete all your SD card contents"""
        await self.simple_embed(ctx, """
                                If you have lost the contents of your SD card with CFW, you will need in SD root:
                                -`boot.firm` and `boot.3dsx` from [luma3ds latest release](https://github.com/LumaTeam/Luma3DS/releases/latest)
                                Then repeat the [finalizing setup](https://3ds.hacks.guide/finalizing-setup) page.
                                """, color=discord.Color.red())

    # Luma downloadlinks
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

    # Embed to broken TWL Troubleshooting
    @commands.command(aliases=["twlfix"])
    async def twl(self, ctx):
        """Information on how to fix a broken TWL Partition"""
        await self.simple_embed(ctx, """
                                If you already have CFW, use [TWLFix-CFW](https://github.com/MechanicalDragon0687/TWLFix-CFW/releases/)
                                If you already have homebrew but not CFW, use [TWLFix-3DS](https://github.com/MechanicalDragon0687/TWLFix-3DS/releases/)
                                If you have neither CFW nor homebrew, it is easier to get homebrew and use the previous option. You could also get a DSiWare app and follow: [TWLFix Stock](https://github.com/MechanicalDragon0687/TWLFix/wiki/Instructions/)
                                Each of these instructions require that you perform a system update after running the apps or restoring the DSiWare
                                """, "Fix broken TWL", color=discord.Color(0xA2BAE0))

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

    # Intructions for deleting home menu Extdata
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

    @commands.guild_only()
    @commands.command()
    async def deltheme(self, ctx, console=None):
        """Deleting home menu theme data"""
        systems = ("3ds", "nx", "ns", "switch")
        if console not in systems:
            if ctx.channel.name.startswith(systems):
                console = "auto"
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")
                return
        if self.check_console(console, ctx.message.channel.name, '3ds'):
            await self.simple_embed(ctx, """
                            1. Navigate to the following folder on your SD card: \
`/Nintendo 3DS/(32 Character ID)/(32 Character ID)/extdata/00000000/`
                            2. Delete the corresponding folder for your region:
                              USA: `000002cd`
                              EUR: `000002ce`
                              JPN: `000002cc`
                              """, title="How to delete Home Menu Theme Data")
        elif self.check_console(console, ctx.message.channel.name, ('nx', 'switch', 'ns')):
            await self.simple_embed(ctx, """
                            1. Navigate to the following folder on your SD card: `/atmosphere/contents`
                            2. Delete the folder with the name `0100000000001000`
                            **Note: On Atmosphere 0.9.4 or below, `contents` is called `titles`.**
                              """, title="How to delete Home Menu Theme Data")

    @commands.command(aliases=['godmode9'])
    async def gm9(self, ctx):
        """Links to the guide on GodMode9"""
        embed = discord.Embed(title="GodMode9 Usage", color=discord.Color(0x66FFFF))
        embed.set_author(name="Plailect", url="https://3ds.hacks.guide/godmode9-usage")
        embed.set_thumbnail(url="https://3ds.hacks.guide/images/bio-photo.png")
        embed.url = "https://3ds.hacks.guide/godmode9-usage"
        embed.description = "GodMode9 usage guide"
        await ctx.send(embed=embed)

    @commands.command()
    async def pminit(self, ctx):
        """Fix for the PM init failed error"""
        await self.simple_embed(ctx, """
                                If you are receiving a "PM init failed" error when attempting to launch safehax and \
are not on 11.3, use [this version of safehax.](https://github.com/TiniVi/safehax/releases/tag/r19)
                                """)

    # Embed to Apache Thunder's Flashcart Launcher
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
    @commands.guild_only()
    async def vc(self, ctx, *, consoles=""):
        """Link to Virtual Console Injects for 3DS/Wiiu."""
        injects = ("3ds", "wiiu")
        consoleslist = []
        consoleslist = [x for x in consoles.split() if x in injects and x not in consoleslist]
        if not consoleslist:
            if ctx.channel.name.startswith(injects):
                consoleslist = ['auto']
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in injects])}.")
                return
        for x in consoleslist:
            if self.check_console(x, ctx.channel.name, ('3ds',)):
                embed = discord.Embed(title="Virtual Console Injects for 3DS", color=discord.Color.blue())
                embed.set_author(name="Asdolo", url="https://gbatemp.net/members/asdolo.389539/")
                embed.set_thumbnail(url="https://i.imgur.com/rHa76XM.png")
                embed.url = "https://mega.nz/#!qnAE1YjC!q3FRHgIAVEo4nRI2IfANHJr-r7Sil3YpPYE4w8ZbUPY"
                embed.description = ("The recommended way to play old classics on your 3DS.\n"
                                     "Usage guide [here](http://3ds.eiphax.tech/nsui.html)")
                await ctx.send(embed=embed)
                continue

            if self.check_console(x, ctx.channel.name, ('wiiu', 'wii u')):
                embed1 = discord.Embed(title="Wii and GameCube games for WiiU", color=discord.Color.red())
                embed1.set_author(name="TeconMoon")
                embed1.set_thumbnail(url="https://gbatemp.net/data/avatars/m/300/300039.jpg")
                embed1.url = "https://gbatemp.net/threads/release-wiivc-injector-script-gc-wii-homebrew-support.483577/"
                embed1.description = "The recommended way to play Wii and gamecube games on your WiiU"
                await ctx.send(embed=embed1)

                embed2 = discord.Embed(title="Virtual Console Injects for WiiU", color=discord.Color.red())
                embed2.set_author(name="CatmanFan")
                embed2.set_thumbnail(url="https://gbatemp.net/data/avatars/m/398/398221.jpg")
                embed2.url = "https://gbatemp.net/threads/release-injectiine-wii-u-virtual-console-injector.491386/"
                embed2.description = "The recommended way to play old classics on your WiiU"
                await ctx.send(embed=embed2)

    # Embed to Console Dump Guides
    @commands.guild_only()
    @commands.command()
    async def dump(self, ctx, console=None):
        """How to dump games and data for CFW consoles"""
        systems = ("3ds", "nx", "ns", "switch", "wiiu", "vwii")
        if console not in systems:
            if ctx.channel.name.startswith(systems):
                console = "auto"
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")
                return
        if self.check_console(console, ctx.channel.name, '3ds'):
            embed = discord.Embed(title="GodMode9 dump/build Guide", color=discord.Color(0x66FFFF))
            embed.set_author(name="Chroma Ryu", url="https://github.com/knight-ryu12/godmode9-layeredfs-usage/wiki/Godmode9-CIA-Dumping-and-Building")
            embed.set_thumbnail(url="https://i.imgur.com/U8NA9lx.png")
            embed.url = "https://github.com/knight-ryu12/godmode9-layeredfs-usage/wiki/Godmode9-CIA-Dumping-and-Building"
            embed.description = "How to dump/build CIAs and Files using GodMode9"
            await ctx.send(embed=embed)
        elif self.check_console(console, ctx.channel.name, ('switch', 'nx', 'ns')):
            embed = discord.Embed(title="Switch dump/build Guide", color=discord.Color(0xCB0004))
            embed.set_author(name="SuchMeme", url="https://suchmememanyskill.github.io/guides/switchdumpguide/")
            embed.set_thumbnail(url="https://i.imgur.com/FkKB0er.png")
            embed.url = "https://suchmememanyskill.github.io/guides/switchdumpguide/"
            embed.description = ("How to dump/build NSPs using NXDumpTool\n"
                                 "BAN Warning: only for use using offline emummc")
            await ctx.send(embed=embed)
        elif self.check_console(console, ctx.channel.name, ('wiiu',)):
            embed = discord.Embed(title="Wii U dump/install Guide", color=discord.Color(0x009AC7))
            embed.set_author(name="NH Discord Server", url="https://wiiu.hacks.guide/#/dump-games")
            embed.set_thumbnail(url="https://i.imgur.com/CVSu1zc.png")
            embed.url = "https://wiiu.hacks.guide/#/dump-games"
            embed.description = "How to dump/install Wii U game discs using disc2app and WUP Installer GX2"
            await ctx.send(embed=embed)
        elif self.check_console(console, ctx.channel.name, ('vwii')):
            embed = discord.Embed(title="vWii dump Guide", color=discord.Color(0x009AC7))
            embed.set_author(name="NH Discord Server", url="https://wiiu.hacks.guide/#/dump-wii-games")
            embed.set_thumbnail(url="https://i.imgur.com/CVSu1zc.png")
            embed.url = "https://wiiu.hacks.guide/#/dump-wii-games"
            embed.description = "How to dump Wii game discs on vWii using CleanRip"
            await ctx.send(embed=embed)

    # Embed to Chroma Ryu's cartinstall guide
    @commands.command()
    async def cartinstall(self, ctx):
        """How to install 3DS cartridges to the SD card"""
        embed = discord.Embed(title="3DS Cart Install Guide", color=discord.Color(0x66FFFF))
        embed.set_author(name="Chroma Ryu", url="https://github.com/knight-ryu12/godmode9-layeredfs-usage/wiki/CartInstall-guide")
        embed.set_thumbnail(url="https://i.imgur.com/U8NA9lx.png")
        embed.url = "https://github.com/knight-ryu12/godmode9-layeredfs-usage/wiki/CartInstall-guide"
        embed.description = "How to install 3DS cartridges to the SD card"
        await ctx.send(embed=embed)

    # Embed to Chroma Ryu's layeredfs guide
    @commands.command()
    async def layeredfs(self, ctx):
        """How to use Luma 8.0+ LayeredFs"""
        embed = discord.Embed(title="LayeredFs Guide", color=discord.Color(0x66FFFF))
        embed.set_author(name="Chroma Ryu", url="https://github.com/knight-ryu12/godmode9-layeredfs-usage/wiki/Using-Luma3DS'-layeredfs-(Only-version-8.0-and-higher)")
        embed.set_thumbnail(url="https://i.imgur.com/U8NA9lx.png")
        embed.url = "https://github.com/knight-ryu12/godmode9-layeredfs-usage/wiki/Using-Luma3DS'-layeredfs-(Only-version-8.0-and-higher)"
        embed.description = "How to use Luma 8.0+ LayeredFs for ROM Hacking."
        await ctx.send(embed=embed)

    # Information about sighax
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

    # Information about how to prep for Switch updates
    @commands.command(aliases=["updateprep", "nxupdate"])
    async def nsupdate(self, ctx):
        """What you should do before updating a Nintendo Switch"""
        await self.simple_embed(ctx, cleandoc("""
                                     **Make sure your version of Atmosphere is up to date and that it supports the latest firmware**

                                     **Atmosphere 0.13.0 (latest release)**
                                     Supports up to firmware 10.0.4.

                                     *To find Atmosphere's version information, while booted into CFW, go into System Settings -> System, and look at \
the text under the System Update button. If it says that a system update is ready instead of displaying the CFW version, type .pendingupdate to learn \
how to delete it.*

                                     **Make sure your version of Hekate is up to date and that it supports the latest firmware**
                                     
                                     **Hekate 5.3.0 (latest release)**
                                     Supports up to firmware 10.0.4.
                                     
                                     *To find Hekate's version information, once Hekate starts, look in the top left corner of the screen. If you use auto-boot, hold `volume -` to stop it.*
                                     
                                     **If you use a custom theme (Atmosphere 0.10.0 and above)**
                                     Delete or rename `/atmosphere/contents/0100000000001000` on your SD card prior to updating, \
as custom themes must be reinstalled for most firmware updates. **Note: On Atmosphere 0.9.4 or below, `contents` is called `titles`.**
                                """), title="What do I need to do before updating my system firmware when running CFW?")

    # Information about pending Switch updates
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
                                 """, title="How to delete pending Switch Updates")

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

    # Creates tutorial command group
    @commands.group(cooldown=commands.Cooldown(0, 0, commands.BucketType.channel), invoke_without_command=True)
    async def tutorial(self, ctx):
        """Links to one of multiple guides"""
        await ctx.send_help(ctx.command)

    @tutorial.command(cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def pokemon(self, ctx):
        """Displays different guides for Pokemon"""
        embed = discord.Embed(title="Possible guides for **Pokemon**:", color=discord.Color.red())
        embed.description = "**pkhex**|**pkhax**|**pkgen** Links to PKHeX tutorial\n**randomize** Links to layeredfs randomizing tutorial"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["pkhax", "pkgen"], cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def pkhex(self, ctx):
        """Links to PKHeX tutorial"""
        embed = discord.Embed(title="PKHeX tutorial", color=discord.Color.red())
        embed.set_thumbnail(url="https://i.imgur.com/rr7Xf3E.jpg")
        embed.url = "https://3ds.eiphax.tech/pkhex.html"
        embed.description = "Basic tutorial for PKHeX"
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
        embed.set_thumbnail(url="https://avatars3.githubusercontent.com/u/16110127?s=400&v=4")
        embed.url = "https://3ds.eiphax.tech/twlmenu.html"
        embed.description = "Basic tutorial for TWiLightMenu++"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["forwarders", "forwarder", "twlforwarders"], cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def ndsforwarders(self, ctx):
        """Links to nds forwarders"""
        embed = discord.Embed(title="NDS Forwarder Guide", color=discord.Color.purple())
        embed.set_thumbnail(url="https://avatars3.githubusercontent.com/u/16110127?s=400&v=4")
        embed.url = "https://gbatemp.net/threads/nds-forwarder-cias-for-your-home-menu.426174/"
        embed.description = "Tutorial for NDS Forwarders"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["3dsvcextract"], cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def vcextract(self, ctx):
        """Links to 3DS Virtual Console Extraction Tutorial"""
        embed = discord.Embed(title="3DS VC Extraction Tutorial", color=discord.Color.red())
        embed.set_author(name="Glazed_Belmont")
        embed.set_thumbnail(url="https://i.imgur.com/TgdOPkG.png")
        embed.url = "https://glazedbelmont.github.io/vcextract/"
        embed.description = "Basic tutorial to extract a rom out of your VC titles"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["gbabios"], cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def gbabiosdump(self, ctx):
        """Links to GBA Bios Extraction Tutorial"""
        embed = discord.Embed(title="GBA Bios Extraction Tutorial", color=discord.Color.red())
        embed.set_author(name="Glazed_Belmont")
        embed.set_thumbnail(url="https://i.imgur.com/TgdOPkG.png")
        embed.url = "https://glazedbelmont.github.io/gbabiosdump/"
        embed.description = "Basic tutorial to extract a GBA bios"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["fuse-3ds", "fuse", "fuse3ds"], cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def ninfs(self, ctx):
        """Link to ninfs tutorial."""
        embed = discord.Embed(title="Extract and Decrypt games, NAND backups, and SD contents with ninfs", color=discord.Color(0xCE181E))
        embed.description = cleandoc("""
                            This is a tutorial that shows you how to use ninfs to extract the contents of games, \
NAND backups, and SD card contents. Windows, macOS, and Linux are supported.
                            """)
        embed.url = "https://gbatemp.net/threads/499994/"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["appatch", "dsscene"], cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def ap(self, ctx):
        """Anti-piracy patching guide"""
        embed = discord.Embed(title="AP Guide", color=discord.Color.purple())
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

    @tutorial.command(aliases=["ftpd", "3dsftp"], cooldown=commands.Cooldown(0, 0, commands.BucketType.channel))
    async def ftp(self, ctx):
        """FTPD/WinSCP ftp guide"""
        embed = discord.Embed(title="3DS FTP Guide", color=discord.Color.purple())
        embed.set_author(name="Krieg")
        embed.set_thumbnail(url="https://3ds.eiphax.tech/pic/krieg.png")
        embed.url = "https://3ds.eiphax.tech/ftp.html"
        embed.description = "A guide to using ftp with FTPD and WinSCP"
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
        embed.url = "https://github.com/redkerry135/tutorials/wiki/Moving-a-save-from-a-cart-to-a-digital-game"
        embed.description = "A tutorial about how to transfer a save from the cart version of a game to a digital version of that game."
        await ctx.send(embed=embed)

    @commands.guild_only()
    @tutorial.command(aliases=["theme"])
    async def themes(self, ctx, console=None):
        """Links to tutorials for installing themes"""
        systems = ("3ds", "nx", "ns", "switch")
        if console not in systems:
            if ctx.channel.name.startswith(systems):
                console = "auto"
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")
                return
        if self.check_console(console, ctx.message.channel.name, '3ds'):
            embed = discord.Embed(title="3DS Themes Tutorial", color=discord.Color.dark_orange())
            embed.url = "https://itspizzatime1501.github.io/guides/themes/"
            embed.description = "Tutorial for installing themes on the 3DS"
            await ctx.send(embed=embed)
        elif self.check_console(console, ctx.message.channel.name, ('nx', 'switch', 'ns')):
            embed = discord.Embed(title="Switch Themes Tutorial", color=discord.Color.dark_orange())
            embed.url = "https://nh-server.github.io/switch-guide/extras/theming/"
            embed.description = "Tutorial for installing themes on the Switch"
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
                async with session.get(f"https://tinydb.eiphax.tech/api/search/{encodedapp}", timeout=2) as resp:
                    response = await resp.json()
            except (aiohttp.ServerConnectionError, aiohttp.ClientConnectorError, aiohttp.ClientResponseError):
                return await ctx.send("I can't connect to tinydb 💢")
        if response['success']:
            release = response['result']['newest_release']
            embed = discord.Embed(title=release['name'], image=release['qr_url'], description=f"{release['description']}\n [[Download]({release['download_url']})] [[Source]({response['result']['github_url']})]")
            embed.set_image(url=release['qr_url'])
            embed.set_footer(text=f"by {release['author']}")
            return await ctx.send(embed=embed)
        return await ctx.send(f"Couldnt find {self.bot.escape_text(app)} in tinydb!")

    @commands.command()
    async def cios(self, ctx):
        """cIOS installation guide"""
        embed = discord.Embed(title="cIOS Guide", color=discord.Color.green())
        embed.set_author(name="tj_cool")
        embed.set_thumbnail(url="https://i.imgur.com/sXSNYyV.jpg")
        embed.url = "https://sites.google.com/site/completesg/backup-launchers/installation"
        embed.description = "A cIOS installation guide"
        await ctx.send(embed=embed)

    @commands.command()
    async def sdroot(self, ctx):
        """Picture to say what the heck is the root"""
        embed = discord.Embed()
        embed.set_image(url="https://i.imgur.com/7PIvVjJ.png")
        await ctx.send(embed=embed)

    @commands.command(aliases=['whatsid0', 'id0'])
    async def whatisid0(self, ctx):
        """Picture to say what the heck is the id0"""
        embed = discord.Embed()
        embed.set_image(url="https://media.discordapp.net/attachments/196635695958196224/677996125034250280/unknown-76.png")
        await ctx.send(embed=embed)

    # Information about autoRCM
    @commands.command()
    async def autorcm(self, ctx):
        """Guide and Warnings about AutoRCM"""
        embed = discord.Embed(title="Guide", color=discord.Color(0xCB0004))
        embed.set_author(name="NH Discord Server")
        embed.set_thumbnail(url="https://i.imgur.com/CVSu1zc.png")
        embed.url = "https://nh-server.github.io/switch-guide/extras/autorcm/"
        embed.description = "Guide and Warnings about AutoRCM"
        await ctx.send(embed=embed)

    @commands.command(aliases=['switchserial'])
    async def serial(self, ctx):
        """Picture to show what the hell a serial is"""
        embed = discord.Embed(title="Don't know where your Switch's serial is?", color=discord.Color.red())
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
        """90DNS IP adresses"""
        await self.simple_embed(ctx, """
                                The public 90DNS IP adresses are:
                                - `207.246.121.77` (USA)
                                - `163.172.141.219`(France)
                                
                                To set these go to System Settings -> Internet -> Connection Settings -> Your wifi Network -> DNS to Manual -> Set primary and secondary DNS to the previously listed IPs -> Save Settings.

                                Set the primary DNS server to the IP that is closest to you and the other as your secondary DNS.
                                
                                You will have to manually set these for each WiFi connection you have set up.
                                
                                [Follow these steps](https://nh-server.github.io/switch-guide/extras/blocking_updates/#testing-if-your-90dns-connection-is-working) to ensure that the connection is safe and not blocked by your ISP.
                                """, title="90DNS IP adressses")

    @commands.command(aliases=['missingco'])
    async def missingconfig(self, ctx):
        """No main boot entries found solution"""
        await self.simple_embed(ctx, """
                                You forgot to copy the "hekate_ipl.ini" file to the bootloader folder on your sd card, or forgot to insert your sd card before booting hekate.

                                Note that if hekate can't find a config, it'll create one. So likely you now have a hekate_ipl.ini in your bootloader folder, replace it with the one from the guide
                                """, title="Getting the \"No main boot entries found\" error in hekate?")

    @commands.command(aliases=['ntrboot', 'ntrcartlist', 'ntrbootcartlist'])
    async def ntrcart(self, ctx):
        imagelink = "https://i.imgur.com/362bH8k.png"
        title = "Which flashcarts work with NTRBoot?"
        embed = discord.Embed(title=title, color=discord.Color.default())
        embed.set_image(url=imagelink)
        await ctx.send(embed=embed)

    @commands.command(aliases=['injector'])
    async def injectors(self, ctx):
        embed = discord.Embed(title="List of switch payload injectors", color=discord.Color(0xCE181E))
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
        """, title="Safe Mode on the 3DS")

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
        embed = discord.Embed(title="How to Reset the Internet Browser Save Data", color=discord.Color(0x009AC7))
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
        Make sure you have a [payload.elf](https://github.com/wiiu-env/homebrew_launcher_installer/releases/latest) in the wiiu folder.""", title="FSOpenFile Failed [...] payload.elf")

    @commands.command()
    async def recover(self, ctx):
        """Troubleshooting guide for vWii"""
        embed = discord.Embed(title="Recover a vWii IOS/Channel", color=0xe60012)
        embed.set_author(name="NH Discord Server", url="https://wiiu.hacks.guide/#/recover-vwii-ioses-channels")
        embed.set_thumbnail(url="https://i.imgur.com/CVSu1zc.png")
        embed.url = "https://wiiu.hacks.guide/#/recover-vwii-ioses-channels"
        embed.description = "A complete guide to recover a lost or corrupted system channel or IOS on vWii"
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def invite(self, ctx, name: str):
        """Available servers are:
        twl, switchroot, acnl, flagbrew, themeplaza, smashultimate, ndsbrew, citra, homebrew, skyrimnx, pkhexautolegality, reswitched, cemu, dragoninjector, vita, henkaku, universal, r3DS, smash4, switchlan, ctgp7, retronx"""
        name = name.casefold()

        # When adding invites, make sure the keys are lowercase, or the command will not find it when invoked!
        invites = {
            'twl':'yD3spjv',
            'switchroot': '9d66FYg',
            'acnl':'EZSxqRr',
            'flagbrew': 'bGKEyfY',
            'themeplaza': '2hUQwXz',
            'smashultimate': 'ASJyTrZ',
            'ndsbrew': 'XRXjzY5',
            'citra': 'FAXfZV9',
            'homebrew': 'C29hYvh',
            'skyrimnx': 'FhhfvVj',
            'pkhexautolegality': 'tDMvSRv',
            'reswitched': 'ZdqEhed',
            'cemu': '5psYsup',
            'dragoninjector': 'HdSFXbh',
            'vita': 'JXEKeg6',
            'henkaku': 'm7MwpKA',
            'universal': 'KDJCfGF',
            'smash4': 'EUZJhUJ',
            'switchlan': 'SbxDMER',
            'ctgp7': '0uTPwYv3SPQww54l',
            'retronx': 'vgvZN9W',
            'r3ds': '3ds',
            'lovepotion' : 'ggbKkhc',
        }

        if name in invites:
            await ctx.send(f"https://discord.gg/{invites[name]}")
        else:
            await ctx.send(f"Invalid invite code. Valid server names are: {', '.join(invites.keys())}")

    @commands.guild_only()
    @commands.command()
    async def db(self, ctx, console=None):
        """Links to the relevant games database"""
        systems = ("3ds", "nx", "ns", "switch")
        if console not in systems:
            if ctx.channel.name.startswith(systems):
                console = "auto"
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")
                return
        if self.check_console(console, ctx.message.channel.name, '3ds'):
            embed = discord.Embed(title="3DS Database", color=discord.Color.dark_orange())
            embed.url = "http://3dsdb.com/"
            embed.description = "3DS database for game releases."
            await ctx.send(embed=embed)
        elif self.check_console(console, ctx.message.channel.name, ('nx', 'switch', 'ns')):
            embed = discord.Embed(title="Nintendo Switch Database", color=discord.Color.dark_orange())
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
        embed = discord.Embed(title="What to do if essential.exefs is missing", color=discord.Color.magenta())
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
        embed = discord.Embed(title="What to do if you want to keep homebrew apps during a system transfer", color=discord.Color.magenta())
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
        embed = discord.Embed(title="Installing CBHC incorrectly can brick your Wii U!", color=discord.Color.red())
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
                    3DS Hacks Guide's [unSAFE_MODE](https://3ds.hacks.guide/installing-boot9strap-(usm))
                    """, title="unSAFE_MODE")

        
def setup(bot):
    bot.add_cog(Assistance(bot))
