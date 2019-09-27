import aiohttp
import discord
import urllib.parse

from cogs.checks import check_staff_id
from discord.ext import commands
from inspect import cleandoc


class Assistance(commands.Cog):
    """
    Commands that will mostly be used in the help channels.
    """
    def __init__(self, bot):
        self.bot = bot
        self.systems = ("3ds", "wiiu", "vwii", "switch", "nx", "ns", "wii", "dsi", "legacy")
        print(f'Cog "{self.qualified_name}" loaded')

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

    @commands.guild_only()
    @commands.command(aliases=["sr", "Sr", "sR", "SR"], hidden=True)
    async def staffreq(self, ctx, *, msg_request: str = ""):
        """Request staff, with optional additional text. Trusted, Helpers, Staff, Retired Staff, Verified only."""
        author = ctx.author
        if not await check_staff_id(ctx, 'Helper', ctx.author.id) and (self.bot.roles['Verified'] not in author.roles) and (self.bot.roles['Trusted'] not in author.roles) and (self.bot.roles['Retired Staff'] not in author.roles):
            msg = f"{author.mention} You cannot use this command at this time. Please ask individual staff members if you need help."
            await ctx.send(msg)
            return
        await ctx.message.delete()
        # await ctx.send("Request sent.")
        msg = f"❗️ **Assistance requested**: {ctx.channel.mention} by {author.mention} | {ctx.author} @here"
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
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def guide(self, ctx, *, consoles=""):
        """Links to the recommended guides."""
        consoleslist = []
        consoleslist = [x for x in consoles.split() if x in self.systems and x not in consoleslist]
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
                embed.set_author(name="FlimFlam69 & Plailect", url="https://wiiu.hacks.guide/")
                embed.set_thumbnail(url="http://i.imgur.com/CpF12I4.png")
                embed.url = "https://wiiu.hacks.guide/"
                embed.description = "FlimFlam69 and Plailect's Wii U custom firmware + coldboothax guide"
                await ctx.send(embed=embed)
                continue
            if self.check_console(x, ctx.channel.name, ('vwii',)):
                embed = discord.Embed(title="Guide", color=discord.Color(0xFFFFFF))
                embed.set_author(name="FlimFlam69 & Plailect", url="https://wiiu.hacks.guide/vwii-modding")
                embed.set_thumbnail(url="https://i.imgur.com/FclGzNz.png")
                embed.url = "https://wiiu.hacks.guide/vwii-modding"
                embed.description = "FlimFlam69 and Plailect's vWii modding guide"
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

    @commands.command(aliases=['finalizing'])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def finalize(self, ctx):
        """Finalizing Setup"""
        await self.simple_embed(ctx, """
                    3DS Hacks Guide's [Finalizing Setup](https://3ds.hacks.guide/finalizing-setup)
                    """, title="Finalizing Setup")

    # Embed to Soundhax Download Website
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
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
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def dsp(self, ctx):
        """Links to Dsp1."""
        embed = discord.Embed(title="Dsp1", color=discord.Color.green())
        embed.set_author(name="zoogie", url="https://github.com/zoogie", icon_url="https://gbatemp.net/data/avatars/l/357/357147.jpg?1426471484")
        embed.description = "Dump 3DS's DSP component to SD for homebrew audio."
        embed.set_thumbnail(url="https://raw.githubusercontent.com/Cruel/DspDump/master/icon.png")
        embed.url = "https://github.com/zoogie/DSP1/releases"
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def ntrstream(self, ctx):
        """Snickerstream/NTR streaming guide"""
        embed = discord.Embed(title="Snickerstream: NTR Streaming Client", color=discord.Color.blue())
        embed.url = "https://gbatemp.net/threads/release-snickerstream-revived-a-proper-release-with-lots-of-improvements-and-new-features.488374/"
        embed.description = "How to use NTR CFW with Snickerstream to stream your 3DS' screen\n**Requires [Luma3DS 9.1](https://github.com/AuroraWright/Luma3DS/releases/tag/v9.1)**"
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
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def update(self, ctx):
        """Explains how to safely prepare for an update if you have boot9strap installed"""
        await self.simple_embed(ctx, """
                **Is it safe to update to current 3DS firmware?**
                
                **Luma3DS 9.1 and above**
                You can update safely.
                
                **Luma3DS 8.0 - 9.0**
                Follow the [manual Luma3DS update guide](https://gist.github.com/chenzw95/3b5b953c9c913e89fdda3c4c4d98d086), then you can update safely. Being on these Luma3DS \
versions on 11.8+ will cause a blackscreen until you update.
                
                **Luma3DS 7.1** 
                Follow the [B9S upgrade guide](https://3ds.hacks.guide/updating-b9s)
                
                **Luma3DS 7.0.5 and below**
                Follow the [a9lh-to-b9s guide](https://3ds.hacks.guide/a9lh-to-b9s)
                 
                **To find out your Luma3DS version, hold select on bootup and look at the top left corner of the top screen**
                """)

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

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def info3ds(self, ctx):
        """Links to eiphax explain page"""
        await self.simple_embed(ctx, "Want to learn more about the 3DS and CFW? <https://3ds.eiphax.tech/what.html>")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def cfwuses(self, ctx):
        """Links to eiphax cfw uses page"""
        await self.simple_embed(ctx, "Want to know what CFW can be used for? <https://3ds.eiphax.tech/tips.html>")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def updateb9s(self, ctx):
        """Links to the guide for updating b9s versions"""
        embed = discord.Embed(title="Updating B9S Guide", color=discord.Color(0xCE181E))
        embed.set_author(name="Plailect", url="https://3ds.hacks.guide/updating-b9s")
        embed.set_thumbnail(url="https://3ds.hacks.guide/images/bio-photo.png")
        embed.url = "https://3ds.hacks.guide/updating-b9s"
        embed.description = "A guide for updating to new B9S versions."
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def updateluma(self, ctx):
        """Links to the guide for updating Luma3DS manually (8.0 or later)"""
        embed = discord.Embed(title="Manually Updating Luma3DS", color=discord.Color(0xCE181E))
        embed.set_author(name="Chenzw", url="https://gist.github.com/chenzw95/3b5b953c9c913e89fdda3c4c4d98d086")
        embed.set_thumbnail(url="https://avatars0.githubusercontent.com/u/5243259?s=400&v=4")
        embed.url = "https://gist.github.com/chenzw95/3b5b953c9c913e89fdda3c4c4d98d086"
        embed.description = "A guide for manually updating Luma3ds. This is necessary if you receive the \"Failed to apply 1 Firm patch(es)\" error."
        await ctx.send(embed=embed)

    @commands.command(aliases=["a9lhtob9s", "updatea9lh"])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def atob(self, ctx):
        """Links to the guide for updating from a9lh to b9s"""
        embed = discord.Embed(title="Upgrading a9lh to b9s", color=discord.Color(0xCE181E))
        embed.set_author(name="Plailect", url="https://3ds.hacks.guide/a9lh-to-b9s")
        embed.set_thumbnail(url="https://3ds.hacks.guide/images/bio-photo.png")
        embed.url = "https://3ds.hacks.guide/a9lh-to-b9s"
        embed.description = "A guide for upgrading your device from arm9loaderhax to boot9strap."
        await ctx.send(embed=embed)

    # Gateway h&s troubleshooting command
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def gwhs(self, ctx):
        """Links to gateway health and safety inject troubleshooting"""
        await ctx.send("https://3ds.hacks.guide/troubleshooting#gw_fbi")

    # Hardmodder pastebin list
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def hmodders(self, ctx):
        """Links to approved hardmodder list"""
        await self.simple_embed(ctx, "Don't want to hardmod yourself? Ask one of the installers on the server! <https://pastebin.com/FAiczew4>")

    # Links to ctrtransfer guide
    @commands.command(aliases=["ctrtransfer", "ctrnandtransfer"])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def ctr(self, ctx):
        """Links to ctrtransfer guide"""
        embed = discord.Embed(title="Guide - ctrtransfer", color=discord.Color.orange())
        embed.set_author(name="Plailect", url="https://3ds.hacks.guide/")
        embed.set_thumbnail(url="https://3ds.hacks.guide/images/bio-photo.png")
        embed.url = "https://3ds.hacks.guide/ctrtransfer"
        embed.description = "How to do the 11.5.0-38 ctrtransfer"
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def modmoon(self, ctx):
        """Links to a tool for a mod manager"""
        await self.simple_embed(ctx, cleandoc("""
                                To install mods for Smash 3DS, and to manage other LayeredFS mods, \
[Mod-Moon](https://github.com/Swiftloke/ModMoon/releases) is recommended. Instructions for use can be found on the page.
                                """))

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def inoriwarn(self, ctx):
        """Warns users to keep the channels on-topic - Staff & Helper Declaration Only"""
        await self.simple_embed(ctx, """
                                **Please keep the channels clean and on-topic, further derailing will result in \
intervention.  A staff or helper will be the quickest route to resolution; you can \
contact available staff by private messaging the Mod-Mail bot.** A full list of staff \
and helpers can be found in #welcome-and-rules if you don't know who they are.
                                """)
        
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
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
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def vguides2(self, ctx):
        """Information about video guides relating to custom firmware"""
        await ctx.send("https://www.youtube.com/watch?v=miVDKgInzyg")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def ip(self, ctx):
        """How to check your IP"""
        embed = discord.Embed(title="Check your 3DSs IP (CFW)", color=discord.Color.dark_orange())
        embed.description = "1. FBI\n2. Remote Install\n3. Receive URLs over the network"
        embed.add_field(name="Check your 3DSs IP (Homebrew)", value="1. Open Homebrew Launcher\n2. Press Y")
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def stock(self, ctx, consoles=""):
        """Advisory for various Nintendo systems on stock firmware"""
        systems = ("3ds", "nx", "ns", "switch")
        consoleslist = []
        consoleslist = [x for x in consoles.split() if x in systems and x not in consoleslist]
        if not consoleslist:
            if ctx.channel.name.startswith(systems):
                consoleslist = ['auto']
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")
                return
        for x in consoleslist:
            if self.check_console(x, ctx.message.channel.name, '3ds'):
                embed = discord.Embed(title="Running stock (unmodified) 11.4+ firmware?", color=discord.Color.dark_orange())
                embed.add_field(name="NTRBoot", value="Requires a compatible NDS flashcart and maybe an additional DS(i) or hacked 3DS console depending on the flashcart (All versions, all hardware). [Guide](https://3ds.hacks.guide/ntrboot)", inline=False)
                embed.add_field(name="Seedminer", value="Requires a working NDS mode or Pokémon Picross (free from eshop) [Guide](https://3ds.hacks.guide/seedminer)", inline=False)
                embed.add_field(name="Hardmod", value="Requires soldering **Not for beginners!**. [Guide](https://git.io/fhQk9)", inline=False)
                await ctx.send(embed=embed)
                continue
            if self.check_console(x, ctx.message.channel.name, ('nx', 'switch', 'ns')):
                embed = discord.Embed(title="Using a first-generation Switch?", color=0xe60012)
                embed.description = cleandoc("""
                Use [our guide](https://nh-server.github.io/switch-guide/user_guide/getting_started/) to determine if your Switch is a first-gen unit.
                All firmware versions up to 8.1.0 are currently compatible with [Atmosphere](https://nh-server.github.io/switch-guide/).
                "Second-generation" invulnerable systems should **not** update past 7.0.1, as these systems may have \
custom firmware on this version (and versions below that) in the very far future.
                Downgrading is **impossible** on patched consoles, and isn't worth your time on unpatched ones. 
                """)
                await ctx.send(embed=embed)


    @commands.command(aliases=["fuse-3ds", "fuse", "fuse3ds"])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def ninfs(self, ctx):
        """Link to ninfs tutorial."""
        embed = discord.Embed(title="Extract and Decrypt games, NAND backups, and SD contents with ninfs", color=discord.Color(0xCE181E))
        embed.description = cleandoc("""
                            This is a tutorial that shows you how to use ninfs to extract the contents of games, \
NAND backups, and SD card contents. Windows, macOS, and Linux are supported.
                            """)
        embed.url = "https://gbatemp.net/threads/499994/"
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
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
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def readguide(self, ctx):
        """Read the guide please"""
        await self.simple_embed(ctx, """
                                Asking something that is on the guide will make everyone lose time, so please read and \
re-read the guide steps 2 or 3 times before coming here.
                                """, title="Please read the guide")

    @commands.command(aliases=["atmos", "ams"])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def atmosphere(self, ctx):
        """Download link for the latest Atmosphère version"""
        embed = discord.Embed(title="Atmosphère", color=discord.Color.blue())
        embed.set_author(name="Atmosphère-NX Team", url="https://github.com/Atmosphere-NX")
        embed.set_thumbnail(url="https://avatars2.githubusercontent.com/u/37918415?s=200&v=4")
        embed.url = "https://github.com/Atmosphere-NX/Atmosphere/releases/latest"
        embed.description = "Link to Atmosphère latest release"
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def hekate(self, ctx):
        """Download link for the latest Hekate version"""
        embed = discord.Embed(title="Hekate", color=discord.Color.red())
        embed.set_author(name="CTCaer", url="https://github.com/CTCaer")
        embed.set_thumbnail(url="https://imgur.com/kFEZyuC.png")
        embed.url = "https://github.com/CTCaer/hekate/releases/latest"
        embed.description = "Link to Hekate's latest release"
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def nxcfw(self, ctx):
        """NX CFW alternatives"""
        await self.simple_embed(ctx, """
                                Alternative CFWs like Kosmos and ReiNX are not recommended for the following reasons:
                                
                                * They are mostly based off Atmosphere
                                * When Nintendo updates the firmware, they take a very long time to catch up
                                * Most of the features they claim to offer can be enabled in Atmosphere with some \
additional configuration
                                * Atmosphere's emuNAND/emuMMC implementation is completely free and open source
                                """, title="Why Atmosphere?")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def formatsd(self, ctx):
        """Programs for formatting an SD card"""
        await self.simple_embed(ctx, """
                                Listed below are some utilities to format your SD card.
                                • Windows: [guiformat](http://www.ridgecrop.demon.co.uk/index.htm?guiformat.htm)
                                • Linux: [gparted](http://gparted.org/download.php)
                                • Mac: [Disk Utility](https://support.apple.com/guide/disk-utility/format-a-disk-for-windows-computers-dskutl1010) \
(Always choose "MS-DOS (FAT)" regardless of size, not ExFAT.)
                                """, title="Formatting your SD card")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def bigsd(self, ctx):
        """SD bigger than 32GB"""
        await self.simple_embed(ctx, """
                                If you want to change your SD card to one bigger than 32GB, you'll have to format it to FAT32.
                                Once it is FAT32, copy and paste ALL content from the old SD card to the new SD card.
                                Afterwards, put the SD card in the console, turn the console on and check that your data is there.
                                Warning: Do not put the new SD card in the console BEFORE you copy and paste everything to it. 
                                This will cause all of your current data to “disappear” when you try to use it on the console. 
                                If you accidentally do this, ask us for help.
                                You can do this with the tool of your preference.
                                Formatter examples:
                                • Windows: [guiformat](http://www.ridgecrop.demon.co.uk/index.htm?guiformat.htm)
                                • Linux: [gparted](http://gparted.org/download.php)
                                • Mac: [Disk Utility](https://support.apple.com/guide/disk-utility/format-a-disk-for-windows-computers-dskutl1010) \
(Always choose "MS-DOS (FAT)" regardless of size, not ExFAT.)
                                """, title="Big SD cards")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def sderrors(self, ctx):
        """SD Error Guide"""
        await self.simple_embed(ctx, """
                                Guide For Checking SD Card For Errors
                                http://3ds.eiphax.tech/sderrors.html
                                This covers Windows, Linux and Mac.
                                """, title="SD Card Errors")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
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
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def notbricked(self, ctx):
        """Missing boot.firm"""
        embed = discord.Embed(title="No, you are not bricked")
        embed.description = cleandoc("""
                            If your power LED turns on and off after you installed b9s, you are not bricked and are \
just missing a file called boot.firm in the root of your SD card.
                            """)
        embed.add_field(name="How to fix the issue", value="1. Check you inserted the SD card in your console\n 2. Place/replace the file, downloading it from https://github.com/AuroraWright/Luma3DS/releases", inline=False)
        embed.add_field(name="Checking your SD for errors or corruption", value="https://3ds.eiphax.tech/sderrors.html \n Please read the instructions carefully.", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def troubleshoot(self, ctx, *, console=""):
        """Troubleshooting guides for common issues"""
        embed = discord.Embed(title="Troubleshooting guide for most Seedminer-based methods", color=discord.Color(0xA2BAE0))
        embed.url = "https://3ds.eiphax.tech/issues.html"
        embed.description = "A simple troubleshooting guide for common CFW and homebrew installation issues \n when using Seedminer-based methods."
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
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
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def emureco(self, ctx):
        """Recommendation about EmuNAND"""
        await self.simple_embed(ctx, """
                                If you want to set up an EmuNAND the first thing to know is that you probably don't \
need it; if you don't know what an EmuNAND is, you don't need one.
                                """, title="EmuNAND Recommendation")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def failedupdate(self, ctx):
        """Notice about failed update on Wii U"""
        await self.simple_embed(ctx, """
                                 A failed update in Download Management does not mean there is an update and the system \
is trying to download it. This means your blocking method (DNS etc.) is working and \
the system can't check for an update.
                                 """, color=discord.Color(0x009AC7))

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def ctrmount(self, ctx):
        """Failed to mount CTRNAND error"""
        await self.simple_embed(ctx, """
                                While following the guide, after installing boot9strap, if you get an error that says \
"Failed to mount CTRNAND", just continue on with the guide.
                                """)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def emptysd(self, ctx):
        """What to do if you delete all your SD card contents"""
        await self.simple_embed(ctx, """
                                If you have lost the contents of your SD card with CFW, you will need in SD root:
                                -`boot.3dsx` from Homebrew launcher [here](https://github.com/fincs/new-hbmenu/releases/latest/)
                                -`boot.firm` from [luma3ds latest release](https://github.com/AuroraWright/Luma3DS/releases/latest)
                                Then repeat the [finalizing setup](https://3ds.hacks.guide/finalizing-setup) page.
                                """, color=discord.Color.red())

    # Luma downloadlinks
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def luma(self, ctx, lumaversion=""):
        """Download links for Luma versions"""
        if len(lumaversion) >= 3 and lumaversion[0].isdigit() and lumaversion[1] == "." and lumaversion[2].isdigit():
            await self.simple_embed(ctx, f"Luma v{lumaversion}\nhttps://github.com/AuroraWright/Luma3DS/releases/tag/v{lumaversion}", color=discord.Color.blue())
        elif lumaversion == "latest":
            await self.simple_embed(ctx, "Latest Luma Version:\nhttps://github.com/AuroraWright/Luma3DS/releases/latest", color=discord.Color.blue())
        else:
            await self.simple_embed(ctx, """
                                    Download links for the most common Luma3DS releases:
                                    [Latest Luma](https://github.com/AuroraWright/Luma3DS/releases/latest)
                                    [Luma v7.0.5](https://github.com/AuroraWright/Luma3DS/releases/tag/v7.0.5)
                                    [Luma v7.1](https://github.com/AuroraWright/Luma3DS/releases/tag/v7.1)
                                    """, color=discord.Color.blue())

    # Embed to broken TWL Troubleshooting
    @commands.command(aliases=["twlfix"])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def twl(self, ctx):
        """Information on how to fix a broken TWL Partition"""
        await self.simple_embed(ctx, """
                                If you already have CFW, use [TWLFix-CFW](https://github.com/MechanicalDragon0687/TWLFix-CFW/releases/)
                                If you already have homebrew but not CFW, use [TWLFix-3DS](https://github.com/MechanicalDragon0687/TWLFix-3DS/releases/)
                                If you have neither CFW nor homebrew, it is easier to get homebrew and use the previous option. You could also get a DSiWare app and follow: [TWLFix Stock](https://github.com/MechanicalDragon0687/TWLFix/wiki/Instructions/)
                                Each of these instructions require that you perform a system update after running the apps or restoring the DSiWare
                                """, "Fix broken TWL", color=discord.Color(0xA2BAE0))

    @commands.command(aliases=["redscr"])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def boot3dsx(self, ctx):
        """Download link for 3DS Homebrew Launcher, boot.3dsx"""
        await self.simple_embed(ctx, "The 3DS Homebrew Launcher, [boot.3dsx](https://github.com/fincs/new-hbmenu/releases/download/v2.1.0/boot.3dsx)")

    @commands.command(aliases=["greenscr"])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def b9stool(self, ctx):
        """Download link for B9STool, boot.nds"""
        await self.simple_embed(ctx, "The B9S installation tool for DSiWare exploits.\nB9STool, [boot.nds](https://github.com/zoogie/b9sTool/releases)")

    # Intructions for deleting home menu Extdata
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
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
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def deltheme(self, ctx):
        """Deleting home menu theme data"""
        await self.simple_embed(ctx, """
                                1. Navigate to the following folder on your SD card: \
`/Nintendo 3DS/(32 Character ID)/(32 Character ID)/extdata/00000000/`
                                2. Delete the corresponding folder for your region:
                                  USA: `000002cd`
                                  EUR: `000002ce`
                                  JPN: `000002cc`
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
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def pminit(self, ctx):
        """Fix for the PM init failed error"""
        await self.simple_embed(ctx, """
                                If you are receiving a "PM init failed" error when attempting to launch safehax and \
are not on 11.3, use [this version of safehax.](https://github.com/TiniVi/safehax/releases/tag/r19)
                                """)

    # Embed to Apache Thunder's Flashcart Launcher
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def flashcart(self, ctx):
        """Launcher for old flashcarts"""
        embed = discord.Embed(title="Launcher for old flashcards (r4,m3,dstt,dsx,etc)", color=discord.Color(0x42f462))
        embed.set_author(name="Apache Thunder", url="https://gbatemp.net/threads/r4-stage2-twl-flashcart-launcher-and-perhaps-other-cards-soon%E2%84%A2.416434/")
        embed.set_thumbnail(url="https://gbatemp.net/data/avatars/m/105/105648.jpg")
        embed.url = "https://gbatemp.net/threads/r4-stage2-twl-flashcart-launcher-and-perhaps-other-cards-soon%E2%84%A2.416434/"
        embed.description = "Launcher for old flashcards"
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
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
            if self.check_console(x, ctx.channel.name, ('3ds')):
                embed = discord.Embed(title="Virtual Console Injects for 3DS", color=discord.Color.blue())
                embed.set_author(name="Asdolo", url="https://gbatemp.net/members/asdolo.389539/")
                embed.set_thumbnail(url="https://i.imgur.com/rHa76XM.png")
                embed.url = "https://mega.nz/#!qnAE1YjC!q3FRHgIAVEo4nRI2IfANHJr-r7Sil3YpPYE4w8ZbUPY"
                embed.description = ("The recommended way to play old classics on your 3DS.\n"
                                 "Usage guide [here](http://3ds.eiphax.tech/nsui.html)")
                await ctx.send(embed=embed)

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
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def dump(self, ctx, consoles=""):
        """How to dump games and data for CFW consoles"""
        dumps = ("3ds", "nx", "ns", "switch")
        consoleslist = []
        consoleslist = [x for x in consoles.split() if x in dumps and x not in consoleslist]
        if not consoleslist:
            if ctx.channel.name.startswith(dumps):
                consoleslist = ['auto']
            else:
                await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in dumps])}.")
                return
        for x in consoleslist:
            if self.check_console(x, ctx.channel.name, '3ds'):
                embed = discord.Embed(title="GodMode9 dump/build Guide", color=discord.Color(0x66FFFF))
                embed.set_author(name="Chroma Ryu", url="https://github.com/knight-ryu12/godmode9-layeredfs-usage/wiki/Godmode9-CIA-Dumping-and-Building")
                embed.set_thumbnail(url="https://i.imgur.com/U8NA9lx.png")
                embed.url = "https://github.com/knight-ryu12/godmode9-layeredfs-usage/wiki/Godmode9-CIA-Dumping-and-Building"
                embed.description = "How to dump/build CIAs and Files using GodMode9"
                await ctx.send(embed=embed)
                continue
            if self.check_console(x, ctx.channel.name, ('switch', 'nx', 'ns')):
                embed = discord.Embed(title="Switch dump/build Guide", color=discord.Color(0xCB0004))
                embed.set_author(name="SuchMeme", url="https://suchmememanyskill.github.io/guides/switchdumpguide/")
                embed.set_thumbnail(url="https://i.imgur.com/FkKB0er.png")
                embed.url = "https://suchmememanyskill.github.io/guides/switchdumpguide/"
                embed.description = ("How to dump/build NSPs using NXDumpTool\n"
                                     "BAN Warning: only for use using offline emummc" );
                await ctx.send(embed=embed)


    # Embed to Chroma Ryu's cartinstall guide
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
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
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
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
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def sighax(self, ctx):
        """Information about sighax"""
        embed = discord.Embed(title="Sighax Information", color=discord.Color(0x0000ff))
        embed.set_author(name="SciresM", url="https://www.reddit.com/r/3dshacks/comments/67f6as/psa_clearing_up_some_misconceptions_about_sighax/")
        embed.set_thumbnail(url="https://i.imgur.com/11ajkdJ.jpg")
        embed.url = "https://www.reddit.com/r/3dshacks/comments/67f6as/psa_clearing_up_some_misconceptions_about_sighax/"
        embed.description = "PSA About Sighax"
        await ctx.send(embed=embed)

    @commands.command(name="7zip")
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def p7zip(self, ctx):
        """Download a .7z file extractor"""
        embed = discord.Embed(title="Download 7-Zip or The Unarchiver", color=discord.Color(0x0000ff))
        embed.description = ("To be able to extract .7z files, you will need an extractor that supports this format.\n"
                             "• Windows: [7-Zip](https://www.7-zip.org)\n"
                             "• Mac: [The Unarchiver](https://theunarchiver.com)")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def wiiuhdd(self, ctx):
        """Message on HDDs on the Wii U"""
        await self.simple_embed(ctx, """
                                If you're having trouble getting your HDD to work with your WiiU, it might be due to the HDD not getting enough power. \
One way to fix this is by using an y-cable to connect the HDD to two USB ports.
                                """)

    # Information about pending Switch updates
    @commands.command(aliases=["nxupdate"])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def nsupdate(self, ctx):
        """Erase pending updates on Nintendo Switch"""
        await self.simple_embed(ctx, """
                                When an update is downloaded, but not installed, the console will not display the \
firmware version in System Settings.
                                
                                • To fix this, *power the console off* (hold the power button, follow on-screen prompts).\
***Hold*** Volume Down and Volume Up, then Power. When you see Maintenance Mode, you \
may reboot, and check System Settings.
                                
                                *To block automatic update downloads, enter 163.172.141.219 as your primary DNS and \
45.248.48.62 as your secondary DNS for your home network.*
                                 """, title="How to delete pending Switch Updates")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
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
    @commands.group()
    async def tutorial(self, ctx):
        """Links to one of multiple guides"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @tutorial.command()
    async def pokemon(self, ctx):
        """Displays different guides for Pokemon"""
        embed = discord.Embed(title="Possible guides for **Pokemon**:", color=discord.Color.red())
        embed.description = "**pkhex**|**pkhax**|**pkgen** Links to PKHeX tutorial\n**randomize** Links to layeredfs randomizing tutorial"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["pkhax", "pkgen"])
    async def pkhex(self, ctx):
        """Links to PKHeX tutorial"""
        embed = discord.Embed(title="PKHeX tutorial", color=discord.Color.red())
        embed.set_thumbnail(url="https://i.imgur.com/rr7Xf3E.jpg")
        embed.url = "https://3ds.eiphax.tech/pkhex.html"
        embed.description = "Basic tutorial for PKHeX"
        await ctx.send(embed=embed)

    @tutorial.command()
    async def randomize(self, ctx):
        """Links to layeredfs randomizing tutorial"""
        embed = discord.Embed(title="Randomizing with LayeredFS", color=discord.Color.red())
        embed.set_thumbnail(url="https://i.imgur.com/rr7Xf3E.jpg")
        embed.url = "https://zetadesigns.github.io/randomizing-layeredfs.html"
        embed.description = "Basic tutorial for randomizing with LayeredFS"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["Animal_crossing"])
    async def acnl(self, ctx):
        """Links to AC:NL editing tutorial"""
        embed = discord.Embed(title="AC:NL editing tutorial", color=discord.Color.green())
        embed.set_thumbnail(url="https://i.imgur.com/3rVToMF.png")
        embed.url = "https://3ds.eiphax.tech/acnl.html"
        embed.description = "Basic tutorial for AC:NL editing"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["twilightmenu", "dsimenu++", "srloader"])
    async def twlmenu(self, ctx):
        """Links to twlmenu tutorial"""
        embed = discord.Embed(title="TWiLightMenu++ tutorial", color=discord.Color.purple())
        embed.set_thumbnail(url="https://avatars3.githubusercontent.com/u/16110127?s=400&v=4")
        embed.url = "https://3ds.eiphax.tech/twlmenu.html"
        embed.description = "Basic tutorial for TWiLightMenu++"
        await ctx.send(embed=embed)

    @tutorial.command(aliases=["3dsvcextract", "gbabios", "dumpbios"])
    async def vcextract(self, ctx):
        """Links to 3DS VC and GBA bios Extraction Tutorial"""
        embed = discord.Embed(title="3DS VC Extraction Tutorial", color=discord.Color.red())
        embed.set_author(name="Glazed_Belmont")
        embed.set_thumbnail(url="https://i.imgur.com/TgdOPkG.png")
        embed.url = "https://github.com/GlaZedBelmont/3DS-Tutorials/wiki/3DS-VC-and-GBA-bios-Extraction-Tutorial"
        embed.description = "Basic tutorial to extract a rom out of your VC titles"
        await ctx.send(embed=embed)  
        
    @commands.command()
    async def tinydb(self, ctx):
        """Community-maintained homebrew database"""
        embed = discord.Embed(title="Tinydb", color=discord.Color.green())
        embed.set_author(name="DeadPhoenix")
        embed.set_thumbnail(url="https://files.frozenchen.me/kNJz8.png")
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
            except aiohttp.ClientConnectionError:
                return await ctx.send("I can't connect to tinydb 💢")
        if response['success']:
            release = response['result']['newest_release']
            embed = discord.Embed(title=release['name'], image=release['qr_url'], description=f"{release['description']}\n [[Download]({release['download_url']})] [[Source]({response['result']['github_url']})]")
            embed.set_image(url=release['qr_url'])
            embed.set_footer(text=f"by {release['author']}")
            return await ctx.send(embed=embed)
        return await ctx.send(f"Couldnt find {self.bot.escape_text(app)} in tinydb!")

    @commands.command(aliases=["appatch", "dsscene"])
    async def ap(self, ctx):
        """Anti-piracy patching guide"""
        embed = discord.Embed(title="AP Guide", color=discord.Color.purple())
        embed.set_author(name="Glazed_Belmont")
        embed.set_thumbnail(url="https://i.imgur.com/TgdOPkG.png")
        embed.url = "https://github.com/GlaZedBelmont/3DS-Tutorials/wiki/AP-Patching"
        embed.description = "An AP-Patching guide"
        await ctx.send(embed=embed)
                             
   @commands.command
    async def cios(self, ctx):
        """cIOS installation guide"""
        embed = discord.Embed(title="cIOS Guide", color=discord.Color.green())
        embed.set_author(name="tj_cool")
        embed.set_thumbnail(url="https://i.imgur.com/sXSNYyV.jpg")
        embed.url = "https://sites.google.com/site/completesg/backup-launchers/installation
        embed.description = "A cIOS installation guide"
        await ctx.send(embed=embed)
                             
    @commands.command()
    async def sdroot(self, ctx):
        """Picture to say what the heck is the root""" 
        embed = discord.Embed()
        embed.set_image(url="https://i.imgur.com/pVS2Lc6.png")
        await ctx.send(embed=embed)             
                             
    # Information about autoRCM
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def autorcm(self, ctx):
        """Guide and Warnings about AutoRCM"""
        embed = discord.Embed(title="Guide", color=discord.Color(0xCB0004))
        embed.set_author(name="NH Discord Server")
        embed.set_thumbnail(url="https://i.imgur.com/CVSu1zc.png")
        embed.url = "https://nh-server.github.io/switch-guide/extras/autorcm/"
        embed.description = "Guide and Warnings about AutoRCM"
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def exfat(self, ctx):
        """exFAT on Switch: why not to use it"""
        await self.simple_embed(ctx, """
                                The recommended filesystem format for the Switch is FAT32. 
                                
                                While the Switch supports exFAT through an additional update from Nintendo, here are reasons not to use it:
                                
                                * This filesystem is prone to corruption.
                                * Nintendo does not use files larger than 4GB even while exFAT is used.
                                """, title="exFAT on Switch: Why you shouldn't use it")
        
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
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
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def ninetydns(self, ctx):
        """90DNS IP adresses"""
        await self.simple_embed(ctx, """
                                The public 90DNS IP adresses are:
                                - `163.172.141.219`
                                - `45.248.48.62`
                                
                                To set these go to System Settings -> Internet -> Connection Settings -> Your wifi Network -> DNS to Manual -> Set primary and secondary DNS to the previously listed IPs -> Save Settings.
                                
                                You will have to manually set these for each WiFi connection you have set up.
                                """, title="90DNS IP adressses")

    @commands.command(aliases=['missingco'])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def missingconfig(self, ctx):
        """No main boot entries found solution"""
        await self.simple_embed(ctx, """
                                You forgot to copy the "hekate_ipl.ini" file to the bootloader folder on your sd card, or forgot to insert your sd card before booting hekate.

                                Note that if hekate can't find a config, it'll create one. So likely you now have a hekate_ipl.ini in your bootloader folder, replace it with the one from the guide
                                """, title="Getting the \"No main boot entries found\" error in hekate?")
def setup(bot):
    bot.add_cog(Assistance(bot))
