import discord
from discord.ext import commands
from addons.checks import check_staff
from inspect import cleandoc

class Assistance:
    """
    Commands that will mostly be used in #help-and-questions.
    """
    def __init__(self, bot):
        self.bot = bot
        self.systems = ("3ds", "wiiu", "switch", "nx", "ns", "wii", "dsi", "legacy")
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    async def simple_embed(self, text, title="", color=discord.Color.default()):
        embed = discord.Embed(title=title, color=color)
        embed.description = cleandoc(text)
        await self.bot.say("", embed=embed)

    def check_console(self, message, channel, consoles):
        message = message.lower()
        if message in consoles:
            return True
        elif (not "wii" in consoles or channel.startswith("legacy")) and channel.startswith(consoles) and not message in self.systems:
            return True
        else:
            return False

    @commands.command(pass_context=True, aliases=["sr", "Sr", "sR", "SR"], hidden=True)
    async def staffreq(self, ctx, *, msg_request=""):
        """Request staff, with optional additional text. Trusted, Helpers, Staff, Retired Staff, Verified only."""
        author = ctx.message.author
        if not check_staff(ctx.message.author.id, 'Helper') and (self.bot.verified_role not in author.roles) and (self.bot.trusted_role not in author.roles) and (self.bot.retired_role not in author.roles):
            msg = "{0} You cannot used this command at this time. Please ask individual staff members if you need help.".format(author.mention)
            await self.bot.say(msg)
            return
        await self.bot.delete_message(ctx.message)
        # await self.bot.say("Request sent.")
        msg = "❗️ **Assistance requested**: {0} by {1} | {2}#{3} @here".format(ctx.message.channel.mention, author.mention, author.name, ctx.message.author.discriminator)
        if msg_request != "":
            # msg += "\n✏️ __Additional text__: " + msg_request
            embed = discord.Embed(color=discord.Color.gold())
            embed.description = msg_request
        await self.bot.send_message(self.bot.mods_channel, msg, embed=(embed if msg_request != "" else None))
        try:
            await self.bot.send_message(author, "✅ Online staff have been notified of your request in {0}.".format(ctx.message.channel.mention), embed=(embed if msg_request != "" else None))
        except discord.errors.Forbidden:
            pass

    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def guide(self, ctx, *, consoles="None"):
        """Links to the recommended guides."""
        consoleslist = []
        for x in consoles.split():
            if x in self.systems and x not in consoleslist:
                consoleslist.append(x)
        if not consoleslist:
            if ctx.message.channel.name.startswith(self.systems):
                consoleslist.append("None")
            else:
                await self.bot.say("Please specify console(s). Valid options: 3ds, wiiu, switch, wii, dsi.")
                return
        for x in consoleslist:
            if self.check_console(x, ctx.message.channel.name, '3ds'):
                embed = discord.Embed(title="Guide", color=discord.Color(0xCE181E))
                embed.set_author(name="Plailect", url="https://3ds.hacks.guide/")
                embed.set_thumbnail(url="https://3ds.hacks.guide/images/bio-photo.png")
                embed.url = "https://3ds.hacks.guide/"
                embed.description = "A complete guide to 3DS custom firmware, from stock to boot9strap."
                await self.bot.say("", embed=embed)
                continue
            if self.check_console(x, ctx.message.channel.name, ('wiiu', 'wii u')):
                embed = discord.Embed(title="Guide", color=discord.Color(0x009AC7))
                embed.set_author(name="FlimFlam69 & Plailect", url="https://wiiu.hacks.guide/")
                embed.set_thumbnail(url="http://i.imgur.com/CpF12I4.png")
                embed.url = "https://wiiu.hacks.guide/"
                embed.description = "FlimFlam69 and Plailect's Wii U custom firmware + coldboothax guide"
                await self.bot.say("", embed=embed)
                continue
            if self.check_console(x, ctx.message.channel.name, ('switch', 'nx')):
                embed = discord.Embed(title="Guide", color=discord.Color(0xCB0004))
                embed.set_author(name="NH Discord Server", url="https://nh-server.github.io/switch-guide/")
                embed.set_thumbnail(url="https://i.imgur.com/CVSu1zc.png")
                embed.url = "https://nh-server.github.io/switch-guide/"
                embed.description = "A Switch guide from stock to Atmosphere"
                await self.bot.say("", embed=embed)
                continue
            if self.check_console(x, ctx.message.channel.name, ('legacy', 'wii')):
                embed = discord.Embed(title="Guide", color=discord.Color(0x009AC7))
                embed.set_author(name="tj_cool", url="https://sites.google.com/site/completesg/")
                embed.url = "https://sites.google.com/site/completesg/"
                embed.description = "A complete original Wii softmod guide"
                await self.bot.say("", embed=embed)
            if self.check_console(x, ctx.message.channel.name, ('legacy', 'dsi')):
                embed = discord.Embed(title="Guide", color=discord.Color(0xCB0004))
                embed.set_author(name="jerbear64 & emiyl", url="https://dsi.cfw.guide/")
                embed.url = "https://dsi.cfw.guide/"
                embed.description = "A complete Nintendo DSi homebrew guide, from stock to HiyaCFW"
                await self.bot.say("", embed=embed)	

    @commands.command(aliases=["finalizing","finalizingsetup"])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def finalize(self):
        """Finalizing Setup"""
        await self.simple_embed("""
                    3DS Hacks Guide's [Finalizing Setup](https://3ds.hacks.guide/finalizing-setup)
                    """, title="Finalizing Setup")

    #Embed to Soundhax Download Website
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def soundhax(self):
        """Links to Soundhax Website"""
        embed = discord.Embed(title="Soundhax", color=discord.Color.blue())
        embed.set_author(name="Ned Williamson", url="http://soundhax.com/")
        embed.set_thumbnail(url="http://i.imgur.com/lYf0jan.png")
        embed.url = "http://soundhax.com"
        embed.description = "Free 3DS Primary Entrypoint <= 11.3"
        await self.bot.say("", embed=embed)

    # dsp dumper command
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def dsp(self):
        """Links to Dsp1."""
        embed = discord.Embed(title="Dsp1", color=discord.Color.green())
        embed.set_author(name="zoogie", url="https://github.com/zoogie", icon_url="https://gbatemp.net/data/avatars/l/357/357147.jpg?1426471484")
        embed.description = "Dump 3DS's DSP component to SD for homebrew audio."
        embed.set_thumbnail(url="https://raw.githubusercontent.com/Cruel/DspDump/master/icon.png")
        embed.url = "https://github.com/zoogie/DSP1/releases"
        await self.bot.say("", embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def ntrstream(self):
        """Links to ntr streaming guide"""
        embed = discord.Embed(title="3DS Streaming Guide", color=discord.Color.blue())
        embed.url = "https://gbatemp.net/threads/release-snickerstream-revived-a-proper-release-with-lots-of-improvements-and-new-features.488374/"
        embed.description = "How to use NTR CFW with Snickerstream to stream your 3DS' screen"
        embed.add_field(name="4 common fixes", value=cleandoc("""
                • Are you connected to the Internet?
                • Is your antivirus program blocking the program?
                • Make sure you typed the IP correctly.
                • Make sure you are on the latest preview for NTR 3.6.
                """))
        await self.bot.say("", embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def update(self):
        """Explains how to safely prepare for an update if you have boot9strap installed"""
        await self.simple_embed("""
                **Is it safe to update to 11.9?**
                
                **Luma3DS 9.1**
                You can update to 11.9 safely.
                
                **Luma3DS 8.0 - 9.0**
                Follow this guide: (https://bit.ly/2Q58acr), then you can update to 11.9. Being on these Luma3DS \
versions on 11.9 will cause a blackscreen until you update.
                
                **Luma3DS 7.1** 
                Follow the [B9S upgrade guide](https://3ds.hacks.guide/updating-b9s)
                
                **Luma3DS <=7.0.5**
                Follow the [a9lh-to-b9s guide](https://3ds.hacks.guide/a9lh-to-b9s)
                 
                **To find out your Luma3DS version, hold select on bootup and look at the top left corner of the top screen**
                """)
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def updateb9s(self):
        """Links to the guide for updating b9s versions"""
        embed = discord.Embed(title="Updating B9S Guide", color=discord.Color(0xCE181E))
        embed.set_author(name="Plailect", url="https://3ds.hacks.guide/updating-b9s")
        embed.set_thumbnail(url="https://3ds.hacks.guide/images/bio-photo.png")
        embed.url = "https://3ds.hacks.guide/updating-b9s"
        embed.description = "A guide for updating to new B9S versions."
        await self.bot.say("", embed=embed)
    
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def updateluma(self):
        """Links to the guide for updating Luma3DS manually (8.0 or later)"""
        embed = discord.Embed(title="Manually Updating Luma3DS", color=discord.Color(0xCE181E))
        embed.set_author(name="Chenzw", url="https://gist.github.com/chenzw95/3b5b953c9c913e89fdda3c4c4d98d086")
        embed.set_thumbnail(url="https://avatars0.githubusercontent.com/u/5243259?s=400&v=4")
        embed.url = "https://gist.github.com/chenzw95/3b5b953c9c913e89fdda3c4c4d98d086"
        embed.description = "A guide for manually updating Luma3ds. This is necessary if you receive the \"Failed to apply 1 Firm patch(es)\" error."
        await self.bot.say("", embed=embed)

    @commands.command(aliases=["a9lhtob9s","updatea9lh"])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def atob(self):
        """Links to the guide for updating from a9lh to b9s"""
        embed = discord.Embed(title="Upgrading a9lh to b9s", color=discord.Color(0xCE181E))
        embed.set_author(name="Plailect", url="https://3ds.hacks.guide/a9lh-to-b9s")
        embed.set_thumbnail(url="https://3ds.hacks.guide/images/bio-photo.png")
        embed.url = "https://3ds.hacks.guide/a9lh-to-b9s"
        embed.description = "A guide for upgrading your device from arm9loaderhax to boot9strap."
        await self.bot.say("", embed=embed)

    # Gateway h&s troubleshooting command
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def gwhs(self):
        """Links to gateway health and safety inject troubleshooting"""
        await self.bot.say("https://3ds.hacks.guide/troubleshooting#gw_fbi")

    # Hardmodder pastebin list
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def hmodders(self):
        """Links to approved hardmodder list"""
        await self.simple_embed("Don't want to hardmod yourself? Ask one of the installers on the server! <https://pastebin.com/FAiczew4>")

    # Links to ctrtransfer guide
    @commands.command(aliases=["ctrtransfer","ctrnandtransfer"])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def ctr(self):
        """Links to ctrtransfer guide"""
        embed = discord.Embed(title="Guide - ctrtransfer", color=discord.Color.orange())
        embed.set_author(name="Plailect", url="https://3ds.hacks.guide/")
        embed.set_thumbnail(url="https://3ds.hacks.guide/images/bio-photo.png")
        embed.url = "https://3ds.hacks.guide/ctrtransfer"
        embed.description = "How to do the 11.5.0-38 ctrtransfer"
        await self.bot.say("", embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def modmoon(self):
        """Links to a tool for a mod manager"""
        await self.simple_embed(cleandoc("""
                                To install mods for Smash 3DS, and to manage other LayeredFS mods, \
[Mod-Moon](https://github.com/Swiftloke/ModMoon/releases) is recommended. Instructions for use can be found on the page.
                                """))

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def inoriquest(self):
        """Tells user to be descriptive"""
        await self.simple_embed("""
                                > Reminder: if you would like someone to help you, please be as descriptive as \
possible, of your situation, things you have done, as little as they may seem, \
aswell as assisting materials. Asking to ask wont expedite your process, and may delay assistance.
                                """)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def inoriwarn(self):
        """Warns users to keep the channels on-topic - Staff & Helper Declaration Only"""
        await self.simple_embed("""
                                **Please keep the channels clean and on-topic, further derailing will result in \
intervention.  A staff or helper will be the quickest route to resolution; you can \
contact available staff by private messaging the Mod-Mail bot.** A full list of staff \
and helpers can be found in #welcome-and-rules if you don't know who they are.
                                """)
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def vguides(self):
        """Information about video guides relating to custom firmware"""
        embed = discord.Embed(title="Why you should not use video guides", color=discord.Color.dark_orange())
        embed.description = cleandoc("""
                Reasons to not use video guides:
                - They get outdated quickly
                - Tough to update and give assistance for
                - Can be misinformative and dangerous for the console
                """)
        embed.add_field(name="Recommended Solution", value="Read a trusted written tutorial. Try `.guide` for a list.")
        await self.bot.say("", embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def vguides2(self):
        """Information about video guides relating to custom firmware"""
        await self.bot.say("https://www.youtube.com/watch?v=miVDKgInzyg")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def ip(self):
        """How to check your IP"""
        embed = discord.Embed(title="Check your 3DSs IP (CFW)", color=discord.Color.dark_orange())
        embed.description = "1. FBI\n2. Remote Install\n3. Recieve URLs over the network"
        embed.add_field(name="Check your 3DSs IP (Homebrew)", value="1. Open Homebrew Launcher\n2. Press Y")
        await self.bot.say("", embed=embed)

    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def stock(self, ctx, consoles=""):
        """Advisory for various Nintendo systems on stock firmware"""
        system = ("3ds", "nx", "ns", "switch")
        consoleslist = []
        for x in consoles.split():
            if x in system and x not in consoleslist:
                consoleslist.append(x)
        if not consoleslist:
            if ctx.message.channel.name.startswith(system):
                consoleslist.append("None")
            else:
                await self.bot.say("Please specify a console; valid options are: 3ds, switch")
                return
        for x in consoleslist: 
            if self.check_console(x, ctx.message.channel.name, '3ds'):
                embed = discord.Embed(title="Running stock (unmodified) 11.4+ firmware?", color=discord.Color.dark_orange())
                embed.add_field(name="NTRBoot", value="Requires a compatible NDS flashcart and maybe an additional DS(i) or hacked 3DS console depending on the flashcart (All versions, all hardware). [Guide](https://3ds.hacks.guide/ntrboot)", inline=False)
                embed.add_field(name="Seedminer", value="Requires a DSiWare game from the eshop (free or paid) or Steel Diver: Sub Wars (free from eshop) [Guide](https://3ds.hacks.guide/seedminer)", inline=False)
                embed.add_field(name="Hardmod", value="Requires soldering **Not for beginners!**. [Guide](https://git.io/fhQk9)", inline=False)
                await self.bot.say(embed=embed)
            if self.check_console(x, ctx.message.channel.name, ('nx', 'switch', 'ns')):
                embed = discord.Embed(title="Using a first-generation Switch?", color=0xe60012)
                embed.description = cleandoc("""
                Use [our guide](https://nh-server.github.io/switch-guide/user_guide/getting_started/) to determine if your Switch is a first-gen unit.
                All firmware versions up to 7.0.1 are currently compatible with [Atmosphere](https://nh-server.github.io/switch-guide/).
                "Second-generation" invulnerable systems should **not** update past 4.1.0, as these systems may have \
custom firmware on this version in the very far future.
                Downgrading is **impossible** on patched consoles, and isn't worth your time on unpatched ones. 
                """)
                await self.bot.say("", embed=embed)

    @commands.command(aliases=["fuse-3ds", "fuse"])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def fuse3ds(self):
        """Link to fuse-3ds tutorial."""
        embed = discord.Embed(title="Extract/Decrypt games, NAND backups, and SD contents with fuse-3ds", color=discord.Color(0xCE181E))
        embed.description = cleandoc("""
                            This is a tutorial that shows you how to use fuse-3ds to extract the contents of games, \
NAND backups, and SD card contents. Windows, macOS, and Linux are supported.
                            """)
        embed.url = "https://gbatemp.net/threads/499994/"
        await self.bot.say("", embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def hbl(self):
        """Get Homebrew Launcher working on 11.4+ firmware"""
        await self.simple_embed("""
                                If you wish to access the Homebrew Launcher on 11.4+, you have two options.
                                First of all, you can use Steelminer, a free exploit to install the Homebrew Launcher. However, homebrew-only access has disadvantages.
                                For example, homebrew-only is often unstable and will crash unexpectedly. Also, it is limited in features and system access.
                                The second option is to install CFW, or custom firmware. Please use `.guide 3ds` for a list of ways to get CFW.
                                Here is a [Steelhax guide](https://git.io/fhbGY). Do NOT proceed to `Installing boot9strap` if you do not want CFW.
                                """)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def readguide(self):
        """Read the guide please"""
        await self.simple_embed("""
                                Asking something that is on the guide will make everyone lose time, so please read and \
re-read the guide steps 2 or 3 times before coming here.
                                """, title="Please read the guide")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def bigsd(self):
        """SD bigger than 32GB"""
        await self.simple_embed("""
                                If you want to change your SD card to one bigger than 32GB then you'll have to \
format it to FAT32.
                                You can do this with the tool of your preference.
                                Formatter examples:
                                • Windows: [guiformat](http://www.ridgecrop.demon.co.uk/index.htm?guiformat.htm)
                                • Linux: [gparted](http://gparted.org/download.php)
                                • Mac: [Disk Utility](https://support.apple.com/guide/disk-utility/format-a-disk-for-windows-computers-dskutl1010) \
(Always choose "MS-DOS (FAT)" regardless of size, not ExFAT.)
                                """
                                , title="Big SD cards")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def sderrors(self):
        """SD Error Guide"""
        await self.simple_embed("""
                                Guide For Checking SD Card For Errors
                                http://3ds.eiphax.tech/sderrors.html
                                This covers Windows, Linux and Mac.
                                """, title="SD Card Errors")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def lumabug(self):
        """Luma Black Screen Bug"""
        await self.simple_embed("""
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
    async def notbricked(self):
        """Missing boot.firm"""
        embed = discord.Embed(title="No, you are not bricked")
        embed.description = cleandoc("""
                            If your power LED turns on and off after you installed b9s, you are not bricked and are \
just missing a file called boot.firm in the root of your SD card.
                            """)
        embed.add_field(name="How to fix the issue", value="1. Check you inserted the SD card in your console\n 2. Place/replace the file, downloading it from https://github.com/AuroraWright/Luma3DS/releases", inline=False)
        embed.add_field(name="Checking your SD for errors or corruption", value="https://3ds.eiphax.tech/sderrors.html \n Please read the instructions carefully.", inline=False)
        await self.bot.say("", embed=embed)

    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def troubleshoot(self, ctx, *, console=""):
        """Troubleshooting guides for common issues"""
        if self.check_console(console, ctx.message.channel.name, '3ds'):
            embed=discord.Embed(title="Troubleshooting guide for *miner methods", color=discord.Color(0xA2BAE0))
            embed.url="https://3ds.eiphax.tech/issues.html"
            embed.description = "A simple troubleshooting guide for common CFW and homebrew installation issues \n when using seedminer-based methods."
            await self.bot.say("", embed=embed)


    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def emureco(self):
        """Recommendation about EmuNAND"""
        await self.simple_embed("""
                                If you want to set up an EmuNAND the first thing to know is that you probably don't \
need it; if you don't know what an EmuNAND is, you don't need one.
                                """, title="EmuNAND Recommendation")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def failedupdate(self):
        """Notice about failed update on Wii U"""
        await self.simple_embed("""
                                 A failed update in Download Management does not mean there is an update and the system \
is trying to download it. This means your blocking method (DNS etc.) is working and \
the system can't check for an update.
                                 """, color=discord.Color(0x009AC7))

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def ctrmount(self):
        """Failed to mount CTRNAND error"""
        await self.simple_embed("""
                                While following the guide, after installing boot9strap, if you get an error that says \
"Failed to mount CTRNAND", just continue on with the guide.
                                """)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def emptysd(self):
        """What to do if you delete all your SD card contents"""
        await self.simple_embed("""
                                If you have lost the contents of your SD card with CFW, you will need in SD root:
                                -Homebrew launcher executable [here](https://smealum.github.io/ninjhax2/boot.3dsx)
                                -`boot.firm` from [luma3ds latest release 7z](https://github.com/AuroraWright/Luma3DS/releases/latest)
                                Then repeat the [finalizing setup](https://3ds.hacks.guide/finalizing-setup) page.
                                """, color=discord.Color.red())

    # Luma downloadlinks
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def luma(self, lumaversion=""):
        """Download links for Luma versions"""
        if lumaversion != "":
            await self.simple_embed("Luma v{}\nhttps://github.com/AuroraWright/Luma3DS/releases/tag/v{}".format(lumaversion, lumaversion), color=discord.Color.blue())
        else:
            await self.simple_embed("""
                                    Download links for the most common Luma3DS releases:
                                    [Latest Luma](https://github.com/AuroraWright/Luma3DS/releases/latest)
                                    [Luma v7.0.5](https://github.com/AuroraWright/Luma3DS/releases/tag/v7.0.5)
                                    [Luma v7.1](https://github.com/AuroraWright/Luma3DS/releases/tag/v7.1)
                                    """, color=discord.Color.blue())

    # Embed to broken TWL Troubleshooting
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def twl(self):
        """Information on how to fix a broken TWL Partition"""
        embed = discord.Embed(title="Fix broken TWL", color=discord.Color(0xA2BAE0))
        embed.set_author(name="Plailect", url="https://3ds.hacks.guide/troubleshooting#dsi--ds-functionality-is-broken-after-completing-the-guide")
        embed.set_thumbnail(url="https://3ds.hacks.guide/images/bio-photo.png")
        embed.url = "https://3ds.hacks.guide/troubleshooting#dsi--ds-functionality-is-broken-after-completing-the-guide"
        embed.description = "Instructions on how to fix a broken TWL after doing the guide"
        await self.bot.say("", embed=embed)

    @commands.command(aliases=["redscr"])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def boot3dsx(self):
        """Download link for 3DS Homebrew Launcher, boot.3dsx"""
        await self.simple_embed("The 3DS Homebrew Launcher, [boot.3dsx](https://github.com/fincs/new-hbmenu/releases/download/v2.0.0/boot.3dsx)")

    # Intructions for deleting home menu Extdata
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def homext(self):
        """Deleting home menu extdata"""
        await self.simple_embed("""
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
    async def deltheme(self):
        """Deleting home menu theme data"""
        await self.simple_embed("""
                                1. Navigate to the following folder on your SD card: \
`/Nintendo 3DS/(32 Character ID)/(32 Character ID)/extdata/00000000/`
                                2. Delete the corresponding folder for your region:
                                  USA: `000002cd`
                                  EUR: `000002ce`
                                  JPN: `000002cc`
                                  """, title="How to delete Home Menu Theme Data")

    @commands.command(aliases=['godmode9'])
    async def gm9(self):
        """Links to the guide on GodMode9"""
        embed = discord.Embed(title="GodMode9 Usage", color=discord.Color(0x66FFFF))
        embed.set_author(name="Plailect", url="https://3ds.hacks.guide/godmode9-usage")
        embed.set_thumbnail(url="https://3ds.hacks.guide/images/bio-photo.png")
        embed.url = "https://3ds.hacks.guide/godmode9-usage"
        embed.description = "GodMode9 usage guide"
        await self.bot.say("", embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def pminit(self):
        """Fix for the PM init failed error"""
        await self.simple_embed("""
                                If you are receiving a "PM init failed" error when attempting to launch safehax and \
are not on 11.3, use [this version of safehax.](https://github.com/TiniVi/safehax/releases/tag/r19)
                                """)

    # Embed to Apache Thunder's Flashcart Launcher
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def flashcart(self):
        """Launcher for old flashcarts"""
        embed = discord.Embed(title="Launcher for old flashcards (r4,m3,dstt,dsx,etc)", color=discord.Color(0x42f462))
        embed.set_author(name="Apache Thunder", url="https://gbatemp.net/threads/r4-stage2-twl-flashcart-launcher-and-perhaps-other-cards-soon%E2%84%A2.416434/")
        embed.set_thumbnail(url="https://gbatemp.net/data/avatars/m/105/105648.jpg")
        embed.url = "https://gbatemp.net/threads/r4-stage2-twl-flashcart-launcher-and-perhaps-other-cards-soon%E2%84%A2.416434/"
        embed.description = "Launcher for old flashcards"
        await self.bot.say("", embed=embed)

    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def vc(self, ctx, *, consoles=""):
        """Link to Virtual Console Injects for 3DS/Wiiu."""
        injects = ("3ds", "wiiu", "wii u")
        consoleslist = []
        for x in consoles.split():
            if x in injects and x not in consoleslist:
                consoleslist.append(x)
        if not consoleslist:
            if ctx.message.channel.name.startswith(injects):
                consoleslist.append("None")
            else:
                await self.bot.say("Please specify a console; valid options are: 3ds, wiiu")
                return
        for x in consoleslist: 
            if self.check_console(x, ctx.message.channel.name, '3ds'):
                embed = discord.Embed(title="Virtual Console Injects for 3DS", color=discord.Color.blue())
                embed.set_author(name="Asdolo", url="https://gbatemp.net/members/asdolo.389539/")
                embed.set_thumbnail(url="https://i.imgur.com/rHa76XM.png")
                embed.url = "https://mega.nz/#!qnAE1YjC!q3FRHgIAVEo4nRI2IfANHJr-r7Sil3YpPYE4w8ZbUPY"
                embed.description = ("The recommended way to play old classics on your 3DS.\n"
                                 "Usage guide [here](http://3ds.eiphax.tech/nsui.html)")
                await self.bot.say("", embed=embed)
            if self.check_console(x, ctx.message.channel.name, ('wiiu', 'wii u')):
                embed1 = discord.Embed(title="Wii and GameCube games for WiiU", color=discord.Color.red())
                embed1.set_author(name="TeconMoon")
                embed1.set_thumbnail(url="https://gbatemp.net/data/avatars/m/300/300039.jpg")
                embed1.url = "https://gbatemp.net/threads/release-wiivc-injector-script-gc-wii-homebrew-support.483577/"
                embed1.description = "The recommended way to play Wii and gamecube games on your WiiU"
                await self.bot.say("", embed=embed1)
                embed2 = discord.Embed(title="Virtual Console Injects for WiiU", color=discord.Color.red())
                embed2.set_author(name="CatmanFan")
                embed2.set_thumbnail(url="https://gbatemp.net/data/avatars/m/398/398221.jpg")
                embed2.url = "https://gbatemp.net/threads/release-injectiine-wii-u-virtual-console-injector.491386/"
                embed2.description = "The recommended way to play old classics on your WiiU"
                await self.bot.say("", embed=embed2)

    # Embed to Chroma Ryu's godmode9 guide
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def dump(self):
        """How to dump/build CIAs and Files using GodMode9"""
        embed = discord.Embed(title="GodMode9 dump/build Guide", color=discord.Color(0x66FFFF))
        embed.set_author(name="Chroma Ryu", url="https://github.com/knight-ryu12/godmode9-layeredfs-usage/wiki/Godmode9-CIA-Dumping-and-Building")
        embed.set_thumbnail(url="https://i.imgur.com/U8NA9lx.png")
        embed.url = "https://github.com/knight-ryu12/godmode9-layeredfs-usage/wiki/Godmode9-CIA-Dumping-and-Building"
        embed.description = "How to dump/build CIAs and Files using GodMode9"
        await self.bot.say("", embed=embed)

    # Embed to Chroma Ryu's layeredfs guide
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def layeredfs(self):
        """How to use Luma 8.0+ LayeredFs"""
        embed = discord.Embed(title="LayeredFs Guide", color=discord.Color(0x66FFFF))
        embed.set_author(name="Chroma Ryu", url="https://github.com/knight-ryu12/godmode9-layeredfs-usage/wiki/Using-Luma3DS'-layeredfs-(Only-version-8.0-and-higher)")
        embed.set_thumbnail(url="https://i.imgur.com/U8NA9lx.png")
        embed.url = "https://github.com/knight-ryu12/godmode9-layeredfs-usage/wiki/Using-Luma3DS'-layeredfs-(Only-version-8.0-and-higher)"
        embed.description = "How to use Luma 8.0+ LayeredFs for ROM Hacking."
        await self.bot.say("", embed=embed)


    # Information about sighax
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def sighax(self):
        """Information about sighax"""
        embed = discord.Embed(title="Sighax Information", color=discord.Color(0x0000ff))
        embed.set_author(name="SciresM", url="https://www.reddit.com/r/3dshacks/comments/67f6as/psa_clearing_up_some_misconceptions_about_sighax/")
        embed.set_thumbnail(url="https://i.imgur.com/11ajkdJ.jpg")
        embed.url = "https://www.reddit.com/r/3dshacks/comments/67f6as/psa_clearing_up_some_misconceptions_about_sighax/"
        embed.description = "PSA About Sighax"
        await self.bot.say("", embed=embed)

    @commands.command(pass_context=True, name="7zip")
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def p7zip(self):
        """Download a .7z file extractor"""
        embed = discord.Embed(title="Download 7-Zip or The Unarchiver", color=discord.Color(0x0000ff))
        embed.description = ("To be able to extract .7z files, you will need an extractor that supports this format.\n"
                             "• Windows: [7-Zip](https://www.7-zip.org)\n"
                             "• Mac: [The Unarchiver](https://theunarchiver.com)")
        await self.bot.say("", embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def flashdrives(self):
        """Message on flash drives on the Wii U"""
        await self.simple_embed("""
                                Some flash drives work with the Wii U, some don't. If you have read or write errors, \
or games crash often, you might want to try a different flash drive or hard drive
                                """)

    #Information about pending Switch updates
    @commands.command(aliases=["nxupdate"])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def nsupdate(self):
        """Erase pending updates on Nintendo Switch"""
        await self.simple_embed("""
                                When an update is downloaded, but not installed, the console will not display the \
firmware version in System Settings.
                                
                                • To fix this, *power the console off* (hold the power button, follow on-screen prompts).\
***Hold*** Volume Down and Volume Up, then Power. When you see Maintenance Mode, you \
may reboot, and check System Settings.
                                
                                *To block automatic update downloads, enter 163.172.141.219 as your primary DNS and \
45.248.48.62 as your secondary DNS for your home network.*
                                 """, title="How to delete pending Switch Updates")

    @commands.command(aliases=["write"])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def sdlock(self):
        """Disable write protection on an SD Card"""
        embed = discord.Embed(title="Disable write protection on an SD Card")
        embed.description = cleandoc("""
                                     This switch on the SD Card should be facing upwards, as in this photo. Otherwise, \
your device will refuse to write to it.
                                     *If it is write locked, your console and other applications may behave unexpectedly.*
                                     """)
        embed.set_image(url="https://i.imgur.com/RvKjWcz.png")
        await self.bot.say("", embed=embed)

    #Creates tutorial command group
    @commands.group(pass_context=True)
    async def tutorial(self, ctx):
        """Links to one of multiple guides"""
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command('help'), *ctx.command.qualified_name.split())

    @tutorial.command()
    async def pokemon(self):
        """Displays different guides for Pokemon"""
        embed = discord.Embed(title="Possible guides for **Pokemon**:", color=discord.Color.red())
        embed.description = "**pkhex**|**pkhax**|**pkgen** Links to PKHeX tutorial\n**randomize** Links to layeredfs randomizing tutorial"
        await self.bot.say("", embed=embed)

    @tutorial.command(hidden=True, aliases=["pkhax", "pkgen"])
    async def pkhex(self):
        """Links to PKHeX tutorial"""
        embed = discord.Embed(title="PKHeX tutorial", color=discord.Color.red())
        embed.set_thumbnail(url="https://i.imgur.com/rr7Xf3E.jpg")
        embed.url = "https://3ds.eiphax.tech/pkhex.html"
        embed.description = "Basic tutorial for PKHeX"
        await self.bot.say("", embed=embed)

    @tutorial.command(hidden=True, )
    async def randomize(self):
        """Links to layeredfs randomizing tutorial"""
        embed = discord.Embed(title="Randomizing with LayeredFS", color=discord.Color.red())
        embed.set_thumbnail(url="https://i.imgur.com/rr7Xf3E.jpg")
        embed.url = "https://zetadesigns.github.io/randomizing-layeredfs.html"
        embed.description = "Basic tutorial for randomizing with LayeredFS"
        await self.bot.say("", embed=embed)

    @tutorial.command(aliases=["Animal_crossing"])
    async def acnl(self):
        """Links to AC:NL editing tutorial"""
        embed = discord.Embed(title="AC:NL editing tutorial", color=discord.Color.green())
        embed.set_thumbnail(url="https://i.imgur.com/3rVToMF.png")
        embed.url = "https://3ds.eiphax.tech/acnl.html"
        embed.description = "Basic tutorial for AC:NL editing"
        await self.bot.say("", embed=embed)

    @tutorial.command(aliases=["twilightmenu", "dsimenu++", "srloader", "twilight"])
    async def twlmenu(self):
        """Links to twlmenu tutorial"""
        embed = discord.Embed(title="TWiLightMenu++ tutorial", color=discord.Color.purple())
        embed.set_thumbnail(url="https://avatars3.githubusercontent.com/u/16110127?s=400&v=4")
        embed.url = "https://3ds.eiphax.tech/twlmenu.html"
        embed.description = "Basic tutorial for TWiLightMenu++"
        await self.bot.say("", embed=embed)

    @commands.command()
    async def tinydb(self):
        """Community-maintained homebrew database"""
        embed = discord.Embed(title="Tinydb", color=discord.Color.green())
        embed.set_author(name="DeadPhoenix")
        embed.set_thumbnail(url="https://files.frozenchen.me/kNJz8.png")
        embed.url = "http://tinydb.eiphax.tech"
        embed.description = "A Community-maintained homebrew database"
        await self.bot.say("", embed=embed)

    #Information about autoRCM
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def autorcm(self):
        """Guide and Warnings about AutoRCM"""
        embed = discord.Embed(title="Guide", color=discord.Color(0xCB0004))
        embed.set_author(name="NH Discord Server")
        embed.set_thumbnail(url="https://i.imgur.com/CVSu1zc.png")
        embed.url = "https://nh-server.github.io/switch-guide/extras/autorcm/"
        embed.description = "Guide and Warnings about AutoRCM"
        await self.bot.say("", embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def exfat(self):
        """exFAT on Switch: why not to use it"""
        await self.simple_embed("""
                                The recommended filesystem format for the Switch is FAT32. 
                                
                                While the Switch supports exFAT through an additional update from Nintendo, here are reasons not to use it:
                                
                                * This filesystem is prone to corruption.
                                * Nintendo does not use files larger than 4GB even while exFAT is used.
                                """
                                , title="exFAT on Switch: Why you shouldn't use it")
        
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def nxban(self):
        """Switch ban risk snippet"""
        await self.simple_embed("""
                                The Switch is a much more secure system than the 3DS, and Nintendo has upped their game when it comes to bans. 
                                One of the main reasons for this is that there are significantly more monitoring systems, \
some of which cannot be turned off.

                                Remember that you can only reduce your chances of getting banned; nothing is guaranteed and you could be banned \
at any time if you decide to hack your device. It will always be a cat and mouse game, until or unless there are big changes \
in the scene. 

                                Refer to <#465640445913858048> for a list of things to avoid doing to reduce your risks.
                                You cannot ask about unbanning your console here.
                                """, title="Switch Bans")

def setup(bot):
    bot.add_cog(Assistance(bot))
