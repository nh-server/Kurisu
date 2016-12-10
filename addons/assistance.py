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

    async def simple_embed(self, text, title=""):
        embed = discord.Embed(title=title)
        embed.description = text
        await self.bot.say("", embed=embed)

    @commands.command(pass_context=True, name="sr", hidden=True)
    async def staffreq(self, ctx, *, msg_request=""):
        """Request staff, with optional additional text. Helpers and Staff only."""
        helpers_role = discord.utils.get(ctx.message.server.roles, name="Helpers")
        staff_role = discord.utils.get(ctx.message.server.roles, name="Staff")
        author = ctx.message.author
        if (helpers_role not in author.roles) and (staff_role not in author.roles):
            msg = "{0} You cannot used this command at this time. Please ask individual staff members if you need help.".format(author.mention)
            await self.bot.say(msg)
            return
        # await self.bot.say("Request sent.")
        msg = "❗️ **Assistance requested**: {0} by {1} | {2}#{3} @here".format(ctx.message.channel.mention, author.mention, author.name, ctx.message.author.discriminator)
        if msg_request != "":
            # much \n
            msg += "\n✏️ __Additional text__: " + msg_request
        await self.bot.send_message(discord.utils.get(ctx.message.server.channels, name="mods"), msg)
        await self.bot.delete_message(ctx.message)
        await self.bot.send_message(author, "✅ Online staff has been notified of your request in {0}.".format(ctx.message.channel.mention))

    @commands.command()
    async def guide(self):
        """Links to Plailect's guide."""
        embed = discord.Embed(title="Guide", color=discord.Color.green())
        embed.set_author(name="Plailect", url="https://3ds.guide/")
        embed.set_thumbnail(url="https://3ds.guide/images/bio-photo.png")
        embed.url = "https://3ds.guide/"
        embed.description = "A complete guide to 3DS custom firmware, from stock to arm9loaderhax."
        await self.bot.say("", embed=embed)

    @commands.command()
    async def ez(self):
        """Links to ez3ds."""
        await self.simple_embed("Start here to discover how to hack your 3DS: https://ez3ds.xyz")

    # 9.6 xml command
    @commands.command()
    async def xmls(self):
        """Outputs XMLs for 3DS 9.6-crypto titles, for use with *hax 2.7+"""
        embed = discord.Embed(title="*hax 2.7 mmap XML repository for 9.6-crypto titles", color=discord.Color.green())
        embed.set_author(name="ihaveamac", url="https://github.com/ihaveamac", icon_url="https://avatars0.githubusercontent.com/u/590576?v=3&s=40")
        embed.description = "This enables 9.6+ digital titles to be used under *hax 2.7+, for tools such as save managers."
        embed.url = "https://github.com/ihaveamac/9.6-dbgen-xmls"
        embed.add_field(name="Automatic downloader", value="[@Ryuzaki-MrL](https://github.com/Ryuzaki-MrL) has a tool called [**Custom mmap XML Downloader**](https://gbatemp.net/threads/release-custom-mmap-xml-downloader.438878/), to make the setup process easy.")
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
        embed.url = "https://www.reddit.com/r/3dshacks/comments/4z4sc3/"
        embed.description = "How to use NTR CFW with Nitro Stream to Wirelessly Stream"
        embed.add_field(name="4 common fixes", value="• Are you connected to the Internet?\n• Is your antivirus program blocking the program?\n• Make sure you are not putting the port (:####) into the IP box of Nitro Stream.\n• Does your NTR menu say NTR CFW 3.4 Preview2?")
        await self.bot.say("", embed=embed)

    @commands.command()
    async def update(self):
        """Explains how to safely prepare for an update if you have arm9loaderhax installed"""
        await self.simple_embed("If you have arm9loaderhax and Luma3DS installed after following Plailect's guide, run Luma Updater to make sure it is on the latest Luma3DS normal version and then you can proceed to update your 3DS through system settings. \nNTR CFW works on the latest version; use this version of BootNTR: \n<https://github.com/astronautlevel2/BootNTR/releases>")

    @commands.command()
    async def otpless(self):
        """OTPLess notice"""
        await self.simple_embed("If your OTPless install succeeds (you don't brick) after you forcefully shutdown, and you never see the screens coming back up saying it was successful and asking you to shutdown, please report this here on [GitHub](https://github.com/AuroraWright/SafeA9LHInstaller/issues) or [GBAtemp](https://gbatemp.net/threads/safea9lhinstaller.419577/).")

    @commands.command()
    async def fw11x(self):
        """lists options on 11.x"""
        await self.simple_embed("For those between 11.0 and 11.2, here are your options for CFW: <https://pastebin.com/Q256JqWL>")

    # gateway h&s troubleshooting command
    @commands.command()
    async def gwhs(self):
        """Links to gateway health and safety inject troubleshooting"""
        await self.simple_embed("https://3ds.guide/troubleshooting#gw_fbi")

    # hardmodder pastebin list
    @commands.command()
    async def hmodders(self):
        """Links to approved hardmodder list"""
        await self.simple_embed("Don't want to hardmod yourself? Ask one of the installers on the server! <https://pastebin.com/chh0hHPk>")

    @commands.command()
    async def builds(self):
        """Links to astronautlevel's luma commit site."""
        await self.simple_embed("astronautlevel's Luma3DS commit builds can be found here: https://astronautlevel2.github.io/Luma3DS")

    @commands.command()
    async def logs(self):
        """Links to panopticon."""
        await self.simple_embed("Logs unavailable. Consider logging locally using <http://github.com/megumisonoda/panopticon>")

    @commands.command()
    async def fwlist(self):
        """Links to a list of documented serial numbers w/ versions they shipped with."""
        await self.simple_embed("A serial/firmware comparison can be found here: https://www.reddit.com/r/3dshacks/comments/5fv3xa/new_3dsxl2ds_firmware_by_serial_december_2016/")

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
    async def s4guide(self):
        """Links to a guide for Sm4sh 3ds mods."""
        await self.simple_embed("A guide to setting up mods for smash on your 3ds can be found here: https://github.com/KotuMF/Smash-3DS-Modding-Guide/wiki")

    @commands.command(pass_context=True, name="ez2")
    async def ez2(self, ctx, model: str, major: int, minor: int, revision: int, nver: int, region: str, ):
        """Gives you the direct link to your version's page.\nExample: !ez2 Old 11 0 0 33 E"""
        await self.simple_embed("https://ez3ds.xyz/checkfw?model={0}&major={1}&minor={2}&revision={3}&nver={4}&region={5}".format(model, major, minor, revision, nver, region))

    @commands.command()
    async def lid(self):
        """Warns not to close the lid"""
        await self.simple_embed("Do not **EVER** close the N3DS lid when on 2.1, otherwise, you **WILL BRICK**.")

    @commands.command()
    async def downgrade(self):
        """Downgrade help"""
        await self.simple_embed("Downgrade methods on 11.0 or above\nDSiWare Downgrade: <https://3ds.guide/dsiware-downgrade>\nHardmod: <http://pastebin.com/chh0hHPk> or <https://gbatemp.net/threads/tutorial-noob-friendly-nand-dumping-2ds-3ds-3ds-xl-n3ds-n3ds-xl.414498/>\nDowngrade Methods on 10.7 or below:\nFollow Plailect's guide here: <https://3ds.guide/get-started>")

def setup(bot):
    bot.add_cog(Assistance(bot))
