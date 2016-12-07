#Importing libraries
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
        await self.bot.say("The recommended guide for setting up a hacked 3DS is here: https://3ds.guide/")

    @commands.command()
    async def ez(self):
        """Links to ez3ds."""
        await self.bot.say("Start here to discover how to hack your 3DS: https://ez3ds.xyz")

    # 9.6 xml command
    @commands.command()
    async def xmls(self):
        """Outputs XMLs for 3DS 9.6-crypto titles, for use with *hax 2.7+"""
        await self.bot.say("https://github.com/ihaveamac/9.6-dbgen-xmls")

    # dsp dumper command
    @commands.command()
    async def dsp(self):
        """Links to dsp dumper"""
        await self.bot.say("https://github.com/Cruel/DspDump/releases/latest")

    @commands.command()
    async def ntrstream(self):
        """Links to ntr streaming guide"""
        await self.bot.say("Guide: <http://bit.ly/2fMiKzi>\n4 Common fixes:\n- Are you connected to the internet?\n- Is your antivirus program blocking the program?\n- Make sure you are not putting the port (:####) into the IP box of Nitro Stream.\n- Does your NTR menu say NTR CFW 3.4 Preview2? ")

    @commands.command()
    async def update(self):
        """Explains how to safely prepare for an update if you have arm9loaderhax installed"""
        await self.bot.say("If you have arm9loaderhax and Luma3DS installed after following Plailect's guide, run luma updater to make sure it is on the latest Luma3DS normal version and then you can proceed to update your 3DS through system settings. \nNTR CFW works on the latest version; use this version of BootNTR: \n<https://github.com/astronautlevel2/BootNTR/releases>")

    @commands.command()
    async def otpless(self):
        """OTPLess notice"""
        await self.bot.say("```\nIf your OTPless install succeeds (you don't brick) after you forcefully shutdown, and you never see the screens coming back up saying it was successful and asking you to shutdown, please report this here on GitHub or GBATemp.\n```")

    @commands.command()
    async def fw11x(self):
        """lists options on 11.x"""
        await self.bot.say("For those between 11.0 and 11.2, here are your options for CFW: <http://pastebin.com/raw/dYjVED7z>")

    # gateway h&s troubleshooting command
    @commands.command()
    async def gwhs(self):
        """Links to gateway health and safety inject troubleshooting"""
        await self.bot.say("https://3ds.guide/troubleshooting#gw_fbi")

    # hardmodder pastebin list
    @commands.command()
    async def hmodders(self):
        """Links to approved hardmodder list"""
        await self.bot.say("Don't want to hardmod yourself? Ask one of the installers on the server! <https://pastebin.com/chh0hHPk>")

    @commands.command()
    async def builds(self):
        """Links to astronautlevel's luma commit site."""
        await self.bot.say("astronautlevel's Luma3DS commit builds can be found here: https://astronautlevel2.github.io/Luma3DS")

    @commands.command()
    async def logs(self):
        """Links to panopticon."""
        await self.bot.say("Logs unavailable. Consider logging locally using <http://github.com/megumisonoda/panopticon>")

    @commands.command()
    async def fwlist(self):
        """Links to a list of documented serial numbers w/ versions they shipped with."""
        await self.bot.say("A serial/firmware comparison can be found here: https://www.reddit.com/r/3dshacks/comments/5fv3xa/new_3dsxl2ds_firmware_by_serial_december_2016/")

    # Links to 9.2 ctrtransfer guide
    @commands.command()
    async def ctr92(self):
        """Links to ctrtransfer guide"""
        await self.bot.say("https://3ds.guide/9.2.0-ctrtransfer")

    @commands.command()
    async def s4guide(self):
        """Links to a guide for Sm4sh 3ds mods."""
        await self.bot.say("A guide to setting up mods for smash on your 3ds can be found here: https://github.com/KotuMF/Smash-3DS-Modding-Guide/wiki")

    @commands.command(pass_context=True, name="ez2")
    async def ez2(self, ctx, model: str, major: int, minor: int, revision: int, nver: int, region: str, ):
        """Gives you the direct link to your version's page.\nExample: !ez2 Old 11 0 0 33 E"""
        await self.bot.say("https://ez3ds.xyz/checkfw?model={0}&major={1}&minor={2}&revision={3}&nver={4}&region={5}".format(model, major, minor, revision, nver, region))
        
    @commands.command()
    async def lid(self):
        """Warns not to close the lid"""
        await self.bot.say("Do not **EVER** close the N3DS lid when on 2.1, otherwise, you **WILL BRICK**.")

    @commands.command()
    async def downgrade(self):
        """Downgrade help"""
        await self.bot.say("Downgrade methods on 11.0 or above\nDSiWare Downgrade: https://3ds.guide/dsiware-downgrade\nHardmod: http://pastebin.com/chh0hHPk or https://gbatemp.net/threads/tutorial-noob-friendly-nand-dumping-2ds-3ds-3ds-xl-n3ds-n3ds-xl.414498/\nDowngrade Methods on 10.7 or below:\nsysDowngrader: https://github.com/Plailect/sysDowngrader/releases/tag/1.0.4")
        
def setup(bot):
    bot.add_cog(Assistance(bot))
