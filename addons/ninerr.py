import discord
from discord import Color
from discord.ext import commands
from sys import argv

class NinErr:
    """
    Parses Nintendo 3DS error codes.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    errcodes = {
        '002-0102': ['System is banned by Nintendo. You cannot ask how to fix this issue here.', Color.dark_red()],
        '005-5602': ['Unable to connect to the eShop. This error is most likely the result of an incorrect region setting.\nMake sure your region is correctly set in System Settings. If you encounter this error after region-changing your system, make sure you followed all the steps properly.', Color.orange()],
        '005-5964': ['Your Nintendo Network ID has been banned from accessing the eShop.\nIf you think this was unwarranted, you will have to contact Nintendo Support to have it reversed.', Color.dark_red()],
        '007-2001': ['Usually the result after region-changing the system. New 3DS cannot fix this issue right now.', Color.red()],
        '007-2100': ['The connection to the Nintendo eShop timed out.\nThis may be due to an ongoing server maintenance, check <https://support.nintendo.com/networkstatus> to make sure the servers are operating normally. You may also encounter this error if you have a weak internet connection.', Color.orange()],
        '007-2404': ['An error occurred while attempting to connect to the Nintendo eShop.\nMake sure you are running the latest firmware, since this error will appear if you are trying to access the eShop on older versions.', Color.orange()],
        '007-2923': ['The Nintendo Servers are currently down for maintenance. Please try again later.', Color.gold()],
        '007-3102': ['Cannot find title on Nintendo eShop. Probably pulled.', Color.red()],
        '011-3021': ['Cannot find title on Nintendo eShop. Probably incorrect region, or never existed.', Color.red()],
        '022-2501': ['Attempting to use a Nintendo Network ID on one system when it is linked on another. This can be the result of using System Transfer, then restoring the source system\'s NAND and attempting to use services that require a Nintendo Network ID.', Color.orange()],
        '022-2613': ['Incorrect e-mail or password when trying to link an existing Nintendo Network ID. Make sure there are no typos, and the given e-mail is the correct one for the given ID.\nIf you forgot the password, reset it at <https://id.nintendo.net/account/forgotten-password>', Color.gold()],
        '022-2631': ['Nintendo Network ID deleted, or not usable on the current system. If you used System Transfer, the Nintendo Network ID will only work on the target system.', Color.red()],
        '022-2634': ['Nintendo Network ID is not correctly linked on the system. This can be a result of formatting the SysNAND using System Settings to unlink it from the EmuNAND.\n\n<steps on how to fix>\n\nTinyFormat is recommended for unlinking in the future.', Color.gold()],
        '022-2812': ['System is banned by Nintendo. You cannot ask how to fix this issue here.', Color.dark_red()],
    }

    def get_name(self, d, k):
        if k in d:
            return '{} ({})'.format(d[k], k)
        else:
            return '{}'.format(k)

    @commands.command(pass_context=True, name="ninerr")
    async def ninerr(self, ctx, err: str):
        """Parses Nintendo 3DS error codes."""
        if len(err) != 8 or err[3] != "-":
            await self.bot.say("Wrong format. Error codes use the format `XXX-YYYY`.")
            return
        embed = discord.Embed(title=err)
        embed.url = "http://www.nintendo.com/consumer/wfc/en_na/ds/results.jsp?error_code={}&system=3DS&locale=en_US".format(err)
        #result = "**{}**\n".format(err)
        if err not in self.errcodes:
            embed.description = "I don't know this one! Click the error code for details on Nintendo Support."
            embed.color = Color.dark_red()
        else:
            embed.description = self.errcodes[err][0]
            embed.color = self.errcodes[err][1]
        await self.bot.say("", embed=embed)

def setup(bot):
    bot.add_cog(NinErr(bot))
