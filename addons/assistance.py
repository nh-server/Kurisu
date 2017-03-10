import discord
from discord.ext import commands
from sys import argv

class Assistance:
    """
    Commands that will mostly be used in #help-and-questions.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    async def simple_embed(self, text, title="", color=discord.Color.default()):
        embed = discord.Embed(title=title, color=color)
        embed.description = text
        await self.bot.say("", embed=embed)

    @commands.command(pass_context=True, name="sr", hidden=True)
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
        await self.bot.send_message(author, "✅ Online staff has been notified of your request in {0}.".format(ctx.message.channel.mention), embed=(embed if msg_request != "" else None))

    @commands.command(pass_context=True)
    async def guide(self, ctx, *, console="auto"):
        """Links to Plailect's or FlimFlam69's guide."""
        console == console.lower()
        if console == "3ds" or (console == "auto" and "wiiu" not in ctx.message.channel.name):
            embed = discord.Embed(title="Guide", color=discord.Color(0xCE181E))
            embed.set_author(name="Plailect", url="https://3ds.guide/")
            embed.set_thumbnail(url="https://3ds.guide/images/bio-photo.png")
            embed.url = "https://3ds.guide/"
            embed.description = "A complete guide to 3DS custom firmware, from stock to arm9loaderhax."
            await self.bot.say("", embed=embed)
        if (console == "wiiu" or console == "wii u") or (console == "auto" and "3ds" not in ctx.message.channel.name):
            embed = discord.Embed(title="Guide", color=discord.Color(0x009AC7))
            embed.set_author(name="FlimFlam69", url="https://github.com/FlimFlam69/WiiUTutorial/wiki")
            embed.set_thumbnail(url="http://i.imgur.com/86Hm0kM.png")
            embed.url = "https://github.com/FlimFlam69/WiiUTutorial/wiki"
            embed.description = "FlimFlam69's 5.5.1 IOSU + Kernel Exploit Guide"
            await self.bot.say("", embed=embed)

    #Embed to Soundhax Download Website
    @commands.command()
    async def soundhax(self):
        """Links to Soundhax Website"""
        embed = discord.Embed(title="Soundhax", color=discord.Color.blue())
        embed.set_author(name="Ned Williamson", url="http://soundhax.com/")
        embed.set_thumbnail(url="http://i.imgur.com/lYf0jan.png")
        embed.url = "http://soundhax.com"
        embed.description = "Free 3DS Primary Entrypoint >= 11.3"
        await self.bot.say("", embed=embed)

    # 9.6 xml command
    @commands.command()
    async def xmls(self):
        """Outputs XMLs for 3DS 9.6-crypto titles, for use with *hax 2.7+"""
        embed = discord.Embed(title="*hax 2.7 mmap XML repository for 9.6-crypto titles", color=discord.Color.green())
        embed.set_author(name="ihaveamac", url="https://github.com/ihaveamac", icon_url="https://avatars0.githubusercontent.com/u/590576?v=3&s=40")
        embed.description = "This is no longer necessary. Use *hax 2.8."
        embed.url = "https://github.com/ihaveamac/9.6-dbgen-xmls"
        await self.bot.say("", embed=embed)

    # dsp dumper command
    @commands.command()
    async def dsp(self):
        """Links to DspDump."""
        embed = discord.Embed(title="DspDump", color=discord.Color.green())
        embed.set_author(name="Cruel", url="https://github.com/Cruel", icon_url="https://avatars0.githubusercontent.com/u/383999?v=3&s=40")
        embed.description = "Dump 3DS's DSP component to SD for homebrew audio."
        embed.set_thumbnail(url="https://raw.githubusercontent.com/Cruel/DspDump/master/icon.png")
        embed.url = "https://github.com/Cruel/DspDump/releases/latest"
        await self.bot.say("", embed=embed)

    @commands.command()
    async def ntrstream(self):
        """Links to ntr streaming guide"""
        embed = discord.Embed(title="NTR Streaming Guide", color=discord.Color.blue())
        embed.url = "https://gbatemp.net/threads/tutorial-3ds-screen-recording-without-a-capture-card-ntr-cfw-method.423445/"
        embed.description = "How to use NTR CFW with Nitro Stream to Wirelessly Stream"
        embed.add_field(name="4 common fixes", value="• Are you connected to the Internet?\n• Is your antivirus program blocking the program?\n• Make sure you are not putting the port (:####) into the IP box of Nitro Stream.\n• Does your NTR menu say NTR CFW 3.4 Preview2?")
        await self.bot.say("", embed=embed)

    @commands.command()
    async def update(self):
        """Explains how to safely prepare for an update if you have arm9loaderhax installed"""
        await self.simple_embed("If you have arm9loaderhax and Luma3DS installed after following Plailect's guide, run Luma Updater to make sure it is on the latest Luma3DS normal version and then you can proceed to update your 3DS through system settings. \nNTR CFW works on the latest version; use this version of BootNTR: \n<https://github.com/Nanquitas/BootNTR/releases>")

    # gateway h&s troubleshooting command
    @commands.command()
    async def gwhs(self):
        """Links to gateway health and safety inject troubleshooting"""
        await self.bot.say("https://3ds.guide/troubleshooting#gw_fbi")

    # hardmodder pastebin list
    @commands.command()
    async def hmodders(self):
        """Links to approved hardmodder list"""
        await self.simple_embed("Don't want to hardmod yourself? Ask one of the installers on the server! <http://pastebin.com/wNr42PtH>")

    @commands.command()
    async def builds(self):
        """Links to astronautlevel's luma commit site."""
        await self.simple_embed("Astronautlevel's Luma3DS commit builds can be found here: https://astronautlevel2.github.io/Luma3DS \n(Warning: most builds here are meant for developers and are untested, use at your own risk!)")

    # Links to 9.2 ctrtransfer guide
    @commands.command()
    async def ctr92(self):
        """Links to ctrtransfer guide"""
        #await self.simple_embed("https://3ds.guide/9.2.0-ctrtransfer")
        embed = discord.Embed(title="Guide - 9.2.0 ctrtransfer", color=discord.Color.orange())
        embed.set_author(name="Plailect", url="https://3ds.guide/")
        embed.set_thumbnail(url="https://3ds.guide/images/bio-photo.png")
        embed.url = "https://3ds.guide/9.2.0-ctrtransfer"
        embed.description = "How to do the 9.2.0-20 ctrtransfer"
        await self.bot.say("", embed=embed)

    @commands.command()
    async def sdpayload(self):
        """Information about required files for SafeA9LHInstaller"""
        await self.bot.say("http://i.imgur.com/im9474T.png")

    @commands.command()
    async def s4sel(self):
        """Links to a tool for Smash 4 mods"""
        await self.simple_embed("To install mods for Smash, [Smash Selector](https://gbatemp.net/threads/release-smash-selector.431245/) is reccomended. Instructions for use can be found on the page.")

    @commands.command()
    async def brick(self):
        """Warns about 2.1 dangers"""
        await self.simple_embed("While on 2.1, **NEVER** shut the N3DS lid, update any model, format a 2DS or attempt to play a game on a cartridge. Doing any of these things *will* brick your system.", color=discord.Color.red())

    @commands.command()
    async def inoriquest(self):
        """Tells user to be descriptive"""
        await self.simple_embed("> Reminder: if you would like someone to help you, please be as descriptive as possible, of your situation, things you have done, as little as they may seem, aswell as assisting materials. Asking to ask wont expedite your process, and may delay assistance.")

    @commands.command()
    async def vguides(self):
        """Information about video guides relating to custom firmware"""
        embed = discord.Embed(title="Why you should not use video guides", color=discord.Color.dark_orange())
        embed.description = "\"Video guides\" for custom firmware and arm9loaderhax are not recommended for use. Their contents generally become outdated very quickly for them to be of any use, and they are harder to update unlike a written guide.\n\nWhen this happens, video guides become more complicated than current methods, having users do certain tasks which may not be required anymore.\n\nThere is also a risk of the uploader spreading misinformation or including potentially harmful files, sometimes unintentionally. Using other people's files to install arm9loaderhax can cause serious issues and even brick your system."
        embed.add_field(name="Recommended", value="The recommended thing to do is to use [Plailect's written complete guide for arm9loaderhax](https://3ds.guide). It is the most up to date one and is recommended for everyone.")
        await self.bot.say("", embed=embed)

    @commands.command()
    async def ip(self):
        """How to check your IP"""
        await self.simple_embed("1. FBI\n2. Remote Install\n3. Recieve URLs over the network", title="Check your 3DSs IP")

    @commands.command()
    async def ip2(self):
        """Homebrew way to know your IP"""
        await self.simple_embed("1. Open Homebrew Launcher\n2. Press Y", title="Check your 3DSs IP")

    @commands.command()
    async def nobak(self):
        """Help if you have no NAND backup"""
        await self.simple_embed("After you finish configuring Luma, perform a [9.2.0 ctrtransfer](https://3ds.guide/9.2.0-ctrtransfer.html). Once completed, continue with section VI of [Installing arm9loaderhax](https://3ds.guide/installing-arm9loaderhax).", title="If you have no NAND backup:")

    @commands.command()
    async def stock113(self):
        """Advisory for consoles on stock 11.3 firmware"""
        embed = discord.Embed(title="Running stock (unmodified) 11.3 firmware?", color=discord.Color.dark_orange())
        embed.description = "If your 3DS is running stock 11.3 firmware, you **will not be able** to do any of the following:\n• Downgrade (even with a hardmod)\n• Install A9LH/CFW\n• Install CIAs\n• Use NTR"
        embed.add_field(name="What you can do", value="You will only be able to access the homebrew launcher and use homebrew apps through soundhax.")
        await self.bot.say("", embed=embed)

    @commands.command()
    async def hbl113(self):
        """Get homebrew launcher working on 11.3"""
        await self.simple_embed("If you are encountering errors while trying to access the homebrew launcher on a New 3DS with Luma3DS installed, you should disable the 'Clock + L2' option in the Luma3DS configuration menu (accessed by holding select while booting).")

    @commands.command()
    async def readguide(self):
        """Read the guide please"""
        await self.simple_embed("Asking something that is on the guide will make everyone lose time, so please read and re-read the guide steps 2 or 3 times before coming here.", title="Please read the guide")

    @commands.command()
    async def bigsd(self):
        """SD bigger than 32GB"""
        await self.simple_embed("If you want to change your SD card to one bigger than 32GB then you'll have to format it to FAT32.\nYou can do this with the tool of your preference.\nFormatter examples:\n- [guiformat - Windows](http://www.ridgecrop.demon.co.uk/index.htm?guiformat.htm)\n- [gparted - Linux](http://gparted.org/download.php)", title="Big SD cards")

    @commands.command()
    async def sderrors(self):
        """Sd Error Guide"""
        await self.simple_embed("Guide For Checking SD Card For Errors\n- [H2testw Guide - Windows](https://3ds.guide/h2testw-(windows\))\n- [F3 Guide - Linux](https://3ds.guide/f3-(linux\))\n- [F3X Guide - Mac](https://3ds.guide/f3x-(mac\))", title="SD Card Errors")

    @commands.command()
    async def notbricked(self):
        """Missing arm9loaderhax.bin"""
        await self.simple_embed("If your power LED turns on and off after you installed a9lh, you are not bricked and are just missing a file called arm9loaderhax.bin in the root of your SD card.\nTo fix this you should:\n1.Check you inserted the SD card in your console\n2.Place/replace the file, downloading it from https://github.com/AuroraWright/Luma3DS/releases\nChecking your SD for errors or corruption:\n\tWindows: https://3ds.guide/h2testw-(windows)\n\tLinux: https://3ds.guide/f3-(linux)\n\tMac: https://3ds.guide/f3x-(mac)", title="No. You are not bricked")

    @commands.command()
    async def emureco(self):
        """Recommendation about EmuNAND"""
        await self.simple_embed("If you want to set up an EmuNAND the first thing to know is that you probably don't need it; if you don't know what an EmuNAND is, you don't need one.", title="EmuNAND Recommendation")

    @commands.command()
    async def failedupdate(self):
        """Notice about failed update on Wii U"""
        await self.simple_embed("A failed update in Download Management does not mean there is an update and the system is trying to download it. This means your blocking method (DNS etc.) is working and the system can't check for an update.", color=discord.Color(0x009AC7))

    @commands.command()
    async def netinfo(self):
        """Network Maintenance Information / Operational Status"""
        await self.bot.say("https://www.nintendo.co.jp/netinfo/en_US/index.html")

    @commands.command()
    async def ctrmount(self):
        """Failed to mount CTRNAND error"""
        await self.simple_embed("While following the guide, after installing arm9loaderhax, if you get an error that says \"Failed to mount CTRNAND\", just continue on with the guide.")

    @commands.command()
    async def emptysd(self):
        """What to do if you delete all your SD card contents"""
        await self.simple_embed("If you have lost the contents of your SD card with CFW, repeat sections I, III, V and VI of [Installing arm9loaderhax](https://3ds.guide/installing-arm9loaderhax). You can skip copying arm9loaderhax.bin and configuring Luma with the SD card out.", color=discord.Color.red())

    @commands.command()
    async def twl(self):
        """Information on how to fix a broken TWL Partition"""
        embed = discord.Embed(title="Fix broken TWL", color=discord.Color(0xA2BAE0))
        embed.set_author(name="Plailect", url="https://3ds.guide/troubleshooting#twl_broken")
        embed.set_thumbnail(url="https://3ds.guide/images/bio-photo.png")
        embed.url = "https://3ds.guide/troubleshooting#twl_broken"
        embed.description = "Intructions on how to fix a broken TWL after doing the guide"
        await self.bot.say("", embed=embed)

    @commands.command()
    async def redscr(self):
        """Help with homebrew red screen"""
        await self.simple_embed("A red screen indicates that there is no boot.3dsx on root.\nIf you have a starter folder on root, place the contents of the starter folder on root.\nIf not, redownload the Homebrew Starter Kit and place the contents of the starter folder inside the .zip on root.", title="If you get a red screen trying to open the Homebrew Launcher")

    @commands.command()
    async def homext(self):
        """Deleting home menu extdata"""
        await self.simple_embed("1. Navigate to the following folder on your SD card: `/Nintendo 3DS/(32 Character ID)/(32 Character ID)/extdata/00000000/`\n2. Delete the corresponding folder for your region:\n  USA: `0000008f`\n   EUR: `00000098`\n   JPN: `00000082`\n   KOR: `000000A9`", title="How to clear Home Menu extdata")

def setup(bot):
    bot.add_cog(Assistance(bot))
