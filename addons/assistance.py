import discord
from discord.ext import commands
from sys import argv

class Assistance:
    """
    Commands that will mostly be used in #help-and-questions.
    """
    def __init__(self, bot):
        self.bot = bot
        self.systems = systems = ("3ds", "wiiu", "wii u")
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    async def simple_embed(self, text, title="", color=discord.Color.default()):
        embed = discord.Embed(title=title, color=color)
        embed.description = text
        await self.bot.say("", embed=embed)

    def check_console(self, message, channel, consoles):
        message = message.lower()
        if not (channel.startswith(self.systems) or message.startswith(self.systems)):
            message = "auto"
        if message.startswith(consoles):
            return True
        elif channel.startswith(consoles) and not message.startswith(self.systems):
            return True
        elif message.startswith(self.systems):
            return False
        elif message.startswith('auto'):
            return True

    @commands.command(pass_context=True, aliases=["sr", "Sr", "sR", "SR"], hidden=True)
    async def staffreq(self, ctx, *, msg_request=""):
        """Request staff, with optional additional text. Helpers, Staff, Verified only."""
        author = ctx.message.author
        if (self.bot.helpers_role not in author.roles) and (self.bot.staff_role not in author.roles) and (self.bot.verified_role not in author.roles) and (self.bot.trusted_role not in author.roles):
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
            await self.bot.send_message(author, "✅ Online staff has been notified of your request in {0}.".format(ctx.message.channel.mention), embed=(embed if msg_request != "" else None))
        except discord.errors.Forbidden:
            pass

    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def guide(self, ctx, *, console=""):
        """Links to Plailect's or FlimFlam69's guide."""
        if self.check_console(console, ctx.message.channel.name, '3ds'):
            embed = discord.Embed(title="Guide", color=discord.Color(0xCE181E))
            embed.set_author(name="Plailect", url="https://3ds.hacks.guide/")
            embed.set_thumbnail(url="https://3ds.hacks.guide/images/bio-photo.png")
            embed.url = "https://3ds.hacks.guide/"
            embed.description = "A complete guide to 3DS custom firmware, from stock to boot9strap."
            await self.bot.say("", embed=embed)
        if self.check_console(console, ctx.message.channel.name, ('wiiu', 'wii u')):
            embed = discord.Embed(title="Guide", color=discord.Color(0x009AC7))
            embed.set_author(name="FlimFlam69 & Plailect", url="https://wiiu.hacks.guide/")
            embed.set_thumbnail(url="http://i.imgur.com/CpF12I4.png")
            embed.url = "https://wiiu.hacks.guide/"
            embed.description = "FlimFlam69 and Plailect's Wii U custom firmware + coldboothax guide"
            await self.bot.say("", embed=embed)

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
        embed.add_field(name="4 common fixes", value="• Are you connected to the Internet?\n• Is your antivirus program blocking the program?\n• Make sure you typed the IP correctly.\n• Make sure you are on the latest preview for NTR 3.6.")
        await self.bot.say("", embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def update(self):
        """Explains how to safely prepare for an update if you have boot9strap installed"""
        await self.simple_embed("**Is it safe to update to 11.6?** \n\n **Luma3DS >=8.0** \n You can update to 11.6 safely. Run Luma updater to get the latest Luma3DS version \n\n **Luma3DS 7.1** \n Follow the [B9S upgrade guide](https://3ds.hacks.guide/updating-b9s) \n\n **Luma3DS <=7.0.5** \n Follow the [a9lh-to-b9s guide](https://3ds.hacks.guide/a9lh-to-b9s) \n\n **To find out your Luma3DS version, hold select on bootup and look at the top left corner of the top screen**")

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
        await self.simple_embed("Don't want to hardmod yourself? Ask one of the installers on the server! <http://pastebin.com/wNr42PtH>")

    # Link to Astronautlevel's Luma3ds builds site
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def builds(self):
        """Links to astronautlevel's luma commit site."""
        await self.simple_embed("Astronautlevel's Luma3DS commit builds can be found here: https://astronautlevel2.github.io/Luma3DS \n(Warning: most builds here are meant for developers and are untested, use at your own risk!)")

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
    async def s4sel(self):
        """Links to a tool for Smash 4 mods"""
        await self.simple_embed("To install mods for Smash, [Smash Selector](https://gbatemp.net/threads/release-smash-selector.431245/) is recommended. Instructions for use can be found on the page.")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def brick(self):
        """Warns about 2.1 dangers"""
        await self.simple_embed("While on 2.1, **NEVER** shut the N3DS lid, update any model, format a 2DS or attempt to play a game on a cartridge. Doing any of these things *will* brick your system.", color=discord.Color.red())

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def inoriquest(self):
        """Tells user to be descriptive"""
        await self.simple_embed("> Reminder: if you would like someone to help you, please be as descriptive as possible, of your situation, things you have done, as little as they may seem, aswell as assisting materials. Asking to ask wont expedite your process, and may delay assistance.")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def inoriwarn(self):
        """Warns users to keep the channels on-topic - Staff & Helper Declaration Only"""
        await self.simple_embed(" **Please keep the channels clean and on-topic, further derailing will result in intervention.  A staff or helper will be the quickest route to resolution; you can contact available staff by private messaging the Mod-mail bot.** A full list of staff and helpers can be found in #welcome-and-rules if you don't know who they are.")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def vguides(self):
        """Information about video guides relating to custom firmware"""
        embed = discord.Embed(title="Why you should not use video guides", color=discord.Color.dark_orange())
        embed.description = "\"Video guides\" for custom firmware and arm9loaderhax/boot9strap are not recommended for use. Their contents generally become outdated very quickly for them to be of any use, and they are harder to update unlike a written guide.\n\nWhen this happens, video guides become more complicated than current methods, having users do certain tasks which may not be required anymore.\n\nThere is also a risk of the uploader spreading misinformation or including potentially harmful files, sometimes unintentionally. Using other people's files to install arm9loaderhax can cause serious issues and even brick your system."
        embed.add_field(name="Recommended", value="The recommended thing to do is to use [Plailect's written complete guide for boot9strap](https://3ds.hacks.guide). It is the most up to date one and is recommended for everyone.")
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

    @commands.command(aliases=["stock115","stock"])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def stock114(self):
        """Advisory for consoles on stock 11.4+ firmware"""
        embed = discord.Embed(title="Running stock (unmodified) 11.4+ firmware?", color=discord.Color.dark_orange())
        embed.description = "You have 4 possible options for installing CFW:\n- [NTRBoot](https://3ds.hacks.guide/ntrboot) which requires a compatible NDS flashcart and maybe an additional DS(i) or hacked 3DS console depending on the flashcart\n- [DSiWare](https://3ds.hacks.guide/installing-boot9strap-\(dsiware\)) which involves system transferring from a hacked 3DS to an unhacked 3DS\n- [Seedminer](https://marenthyu.github.io/3dsSeedMinerGuide/) which involves a cheap dsiware game and an adequately powerful PC (or a friend/helper with one)\n- [Hardmod](https://3ds.hacks.guide/installing-boot9strap-\(hardmod\)) which requires soldering **Not for beginners!**\n **Downgrading is impossible on 11.4+!**"
        await self.bot.say("", embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def hbl(self):
        """Get homebrew launcher working on 11.4+ firmware"""
        await self.simple_embed("If you are looking to get access to the homebrew launcher on your unhacked 11.4+ 3DS (Not CFW or CIA installation!), then you will need an exploit like ninjhax, stickerhax, freakyhax or oot3dhax. \nPlease note that stickerhax and oot3dhax require prior access to the homebrew launcher to install the hack on them (Or you can use a powersaves with oot3d)\n\nIf you want access to homebrew on 11.4+, it is recommended that you rather install CFW, as a NTRBoot compatible DS flashcart costs a lot less than a copy of Freakyforms Deluxe, Cubic Ninja, Paper Mario Sticker Star or Ocarina of Time 3D.")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def readguide(self):
        """Read the guide please"""
        await self.simple_embed("Asking something that is on the guide will make everyone lose time, so please read and re-read the guide steps 2 or 3 times before coming here.", title="Please read the guide")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def bigsd(self):
        """SD bigger than 32GB"""
        await self.simple_embed("If you want to change your SD card to one bigger than 32GB then you'll have to format it to FAT32.\nYou can do this with the tool of your preference.\nFormatter examples:\n- [guiformat - Windows](http://www.ridgecrop.demon.co.uk/index.htm?guiformat.htm)\n- [gparted - Linux](http://gparted.org/download.php)\n- [Disk Utility - macOS](https://support.apple.com/guide/disk-utility/format-a-disk-for-windows-computers-dskutl1010) (Always choose \"MS-DOS (FAT)\" regardless of size, not ExFAT.)", title="Big SD cards")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def sderrors(self):
        """Sd Error Guide"""
        await self.simple_embed("Guide For Checking SD Card For Errors\n- [H2testw Guide - Windows](https://3ds.hacks.guide/h2testw-(windows\))\n- [F3 Guide - Linux](https://3ds.hacks.guide/f3-(linux\))\n- [F3X Guide - Mac](https://3ds.hacks.guide/f3x-(mac\))", title="SD Card Errors")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def notbricked(self):
        """Missing boot.firm"""
        await self.simple_embed("If your power LED turns on and off after you installed b9s, you are not bricked and are just missing a file called boot.firm in the root of your SD card.\nTo fix this you should:\n1.Check you inserted the SD card in your console\n2.Place/replace the file, downloading it from https://github.com/AuroraWright/Luma3DS/releases\nChecking your SD for errors or corruption:\n\tWindows: https://3ds.hacks.guide/h2testw-(windows)#\n\tLinux: https://3ds.hacks.guide/f3-(linux)#\n\tMac: https://3ds.hacks.guide/f3x-(mac)#", title="No. You are not bricked")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def emureco(self):
        """Recommendation about EmuNAND"""
        await self.simple_embed("If you want to set up an EmuNAND the first thing to know is that you probably don't need it; if you don't know what an EmuNAND is, you don't need one.", title="EmuNAND Recommendation")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def failedupdate(self):
        """Notice about failed update on Wii U"""
        await self.simple_embed("A failed update in Download Management does not mean there is an update and the system is trying to download it. This means your blocking method (DNS etc.) is working and the system can't check for an update.", color=discord.Color(0x009AC7))

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def ctrmount(self):
        """Failed to mount CTRNAND error"""
        await self.simple_embed("While following the guide, after installing boot9strap, if you get an error that says \"Failed to mount CTRNAND\", just continue on with the guide.")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def emptysd(self):
        """What to do if you delete all your SD card contents"""
        await self.simple_embed("If you have lost the contents of your SD card with CFW, you will need in SD root:\n-Homebrew launcher executable [here](https://smealum.github.io/ninjhax2/boot.3dsx)\n-`boot.firm` from [luma3ds latest release 7z](https://github.com/AuroraWright/Luma3DS/releases/latest)\nThen repeat the [finalizing setup](https://3ds.hacks.guide/finalizing-setup) page.", color=discord.Color.red())

    # Luma downloadlinks
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def luma(self, lumaversion=""):
        """Downloadlinks for luma versions"""
        if lumaversion != "":
            await self.simple_embed("Luma v{}\nhttps://github.com/AuroraWright/Luma3DS/releases/tag/v{}".format(lumaversion, lumaversion), color=discord.Color.blue())
        else:
            await self.simple_embed("Download links for the most common Luma3DS releases: \n[Latest Luma](https://github.com/AuroraWright/Luma3DS/releases/latest)\n[Luma v7.0.5](https://github.com/AuroraWright/Luma3DS/releases/tag/v7.0.5)\n[Luma v7.1](https://github.com/AuroraWright/Luma3DS/releases/tag/v7.1)", color=discord.Color.blue())

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
        """Download link for 3DS homebrew launcher, boot.3dsx"""
        await self.simple_embed("The 3DS Homebrew Launcher, [boot.3dsx](https://github.com/fincs/new-hbmenu/releases/download/v2.0.0/boot.3dsx)")

    # Intructions for deleting home menu Extdata
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def homext(self):
        """Deleting home menu extdata"""
        await self.simple_embed("1. Navigate to the following folder on your SD card: `/Nintendo 3DS/(32 Character ID)/(32 Character ID)/extdata/00000000/`\n2. Delete the corresponding folder for your region:\n  USA: `0000008f`\n   EUR: `00000098`\n   JPN: `00000082`\n   KOR: `000000A9`", title="How to clear Home Menu extdata")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def deltheme(self):
        """Deleting home menu theme data"""
        await self.simple_embed("1. Navigate to the following folder on your SD card: `/Nintendo 3DS/(32 Character ID)/(32 Character ID)/extdata/00000000/`\n2. Delete the corresponding folder for your region:\n  USA: `000002cd`\n   EUR: `000002ce`\n   JPN: `000002cc`", title="How to delete Home Menu Theme Data")

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
        await self.simple_embed("If you are receiving a \"PM init failed\" error when attempting to launch safehax and are not on 11.3, use [this version of safehax.](https://github.com/TiniVi/safehax/releases/tag/r19)")

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
    async def vc(self, ctx, *, console=""):
        """Link to Virtual Console Injects for 3DS/Wiiu."""
        if self.check_console(console, ctx.message.channel.name, '3ds'):
            embed = discord.Embed(title="Virtual Console Injects for 3DS", color=discord.Color.blue())
            embed.set_author(name="Asdolo", url="https://gbatemp.net/members/asdolo.389539/")
            embed.set_thumbnail(url="https://i.imgur.com/rHa76XM.png")
            embed.url = "https://gbatemp.net/search/40920047/?q=injector&t=post&o=date&g=1&c[title_only]=1&c[user][0]=389539"
            embed.description = "The recommended way to play old classics on your 3DS"
            await self.bot.say("", embed=embed)
        if self.check_console(console, ctx.message.channel.name, ('wiiu', 'wii u')):
            embed = discord.Embed(title="Virtual Console Injects for Wiiu", color=discord.Color.blue())
            embed.set_author(name="NicoAICP", url="https://gbatemp.net/members/nicoaicp.404553/")
            embed.set_thumbnail(url="https://i.imgur.com/OsXqiOv.png")
            embed.url = "https://gbatemp.net/threads/release-ultimate-vc-injector-for-wiiu.486781/"
            embed.description = "The recommended way to play old classics on your Wiiu"
            await self.bot.say("", embed=embed)

    # Embed to Chroma Ryu's godmode9 guide
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def dump(self):
        """How to dump/build CIAs using GodMode9"""
        embed = discord.Embed(title="GodMode9 dump/build Guide", color=discord.Color(0x66FFFF))
        embed.set_author(name="Chroma Ryu", url="https://github.com/knight-ryu12/godmode9-layeredfs-usage/wiki/Godmode9-CIA-Dumping-and-Building")
        embed.set_thumbnail(url="https://i.imgur.com/U8NA9lx.png")
        embed.url = "https://github.com/knight-ryu12/godmode9-layeredfs-usage/wiki/Godmode9-CIA-Dumping-and-Building"
        embed.description = "How to dump/build CIAs using GodMode9"
        await self.bot.say("", embed=embed)

    # Embed to Chroma Ryu's layeredfs guide
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def layeredfs(self):
        """How to use Luma 8.0+ LayeredFs"""
        embed = discord.Embed(title="LayeredFs Guide", color=discord.Color(0x66FFFF))
        embed.set_author(name="Chroma Ryu", url="https://github.com/knight-ryu12/godmode9-layeredfs-usage/wiki/Using-Luma3DS'-layeredfs-(Only-version-8.0-and-higer)")
        embed.set_thumbnail(url="https://i.imgur.com/U8NA9lx.png")
        embed.url = "https://github.com/knight-ryu12/godmode9-layeredfs-usage/wiki/Using-Luma3DS'-layeredfs-(Only-version-8.0-and-higer)"
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
        """Download 7zip"""
        embed = discord.Embed(title="Download 7zip", color=discord.Color(0x0000ff))
        embed.set_thumbnail(url="http://i.imgur.com/cX1fuf6.png")
        embed.url = "http://www.7-zip.org/download.html"
        embed.description = "To be able to extract .7z files you need 7zip installed, get it here."
        await self.bot.say("", embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def flashdrives(self):
        """Message on flash drives on the Wii U"""
        await self.simple_embed("Some flash drives work with the Wii U, some don't. If you have read or write errors, or games crash often, you might want to try a different flash drive or hard drive")

def setup(bot):
    bot.add_cog(Assistance(bot))
