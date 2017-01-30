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
        embed.url = "https://www.reddit.com/r/3dshacks/comments/4z4sc3/"
        embed.description = "How to use NTR CFW with Nitro Stream to Wirelessly Stream"
        embed.add_field(name="4 common fixes", value="• Are you connected to the Internet?\n• Is your antivirus program blocking the program?\n• Make sure you are not putting the port (:####) into the IP box of Nitro Stream.\n• Does your NTR menu say NTR CFW 3.4 Preview2?")
        await self.bot.say("", embed=embed)

    @commands.command()
    async def update(self):
        """Explains how to safely prepare for an update if you have arm9loaderhax installed"""
        await self.simple_embed("If you have arm9loaderhax and Luma3DS installed after following Plailect's guide, run Luma Updater to make sure it is on the latest Luma3DS normal version and then you can proceed to update your 3DS through system settings. \nNTR CFW works on the latest version; use this version of BootNTR: \n<https://github.com/astronautlevel2/BootNTR/releases>")

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
    async def brick(self):
        """Warns not to close the lid"""
        await self.simple_embed("**NEVER** shut the N3DS lid, **UPDATE** or **FORMAT** while on 2.1. The last two apply regardless of system model. Doing any of these things will cause serious system instability or outright brick your system.", color=discord.Color.red())

    @commands.command()
    async def downgrade(self):
        """Downgrade help"""
        await self.simple_embed("DSiWare Downgrade: <https://3ds.guide/dsiware-downgrade>\nHardmod: <http://pastebin.com/chh0hHPk> or <https://gbatemp.net/threads/tutorial-noob-friendly-nand-dumping-2ds-3ds-3ds-xl-n3ds-n3ds-xl.414498/>\nDowngrade Methods on 10.7 or below:\nFollow Plailect's guide here: <https://3ds.guide/get-started>", title="Downgrade methods on 11.0 or above")

    @commands.command()
    async def vguides(self):
        """Information about video guides relating to custom firmware"""
        embed = discord.Embed(title="Why you should not use video guides", color=discord.Color.dark_orange())
        embed.description = "\"Video guides\" for custom firmware and arm9loaderhax are not recommended for use. Their contents generally become outdated very quickly for them to be of any use, and they are harder to update unlike a written guide.\n\nWhen this happens, video guides become more complicated than current methods, having users do certain tasks which may not be required anymore.\n\nThere is also a risk of the uploader spreading misinformation or including potentially harmful files, sometimes unintentionally. Using other people's files to install arm9loaderhax can cause serious issues and even brick your system."
        embed.add_field(name="Recommended", value="The recommended thing to do is to use [Plailect's written complete guide for arm9loaderhax](https://3ds.guide). It is the most up to date one and is recommended for everyone.")
        await self.bot.say("", embed=embed)

def setup(bot):
    bot.add_cog(Assistance(bot))
