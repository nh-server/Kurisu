import discord
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
        '002-0102': 'System is banned by Nintendo. You cannot ask how to fix this issue here.',
        '007-2001': 'Usually the result after region-changing the system. New 3DS cannot fix this issue right now.',
        '007-3102': 'Cannot find title on Nintendo eShop. Probably pulled.',
        '011-3021': 'Cannot find title on Nintendo eShop. Probably incorrect region, or never existed.',
        '022-2613': 'Incorrect e-mail or password when trying to link an existing Nintendo Network ID. Make sure there are no typos, and the given e-mail is the correct one for the given ID.\nIf you forgot the password, reset it at <https://id.nintendo.net/account/forgotten-password>',
        '022-2631': 'Nintendo Network ID deleted, or not usable on the current system. If you used System Transfer, the Nintendo Network ID will only work on the target system.',
        '022-2634': 'Nintendo Network ID is not correctly linked on the system. This can be a result of formatting the SysNAND using System Settings to unlink it from the EmuNAND.\n\n<steps on how to fix>\n\nTinyFormat is recommended for unlinking in the future.',
        '022-2812': 'System is banned by Nintendo. You cannot ask how to fix this issue here.',
    }

    def get_name(self, d, k):
        if k in d:
            return '{} ({})'.format(d[k], k)
        else:
            return '{}'.format(k)

    @commands.command(pass_context=True, name="ninerr")
    async def ninerr(self, ctx, err: str):
        """Parses Nintendo 3DS error codes."""
        result = "**{}**\n".format(err)
        if err not in self.errcodes:
            result += "I don't know this one! Try this page: <http://www.nintendo.com/consumer/wfc/en_na/ds/results.jsp?error_code={}&system=3DS&locale=en_US>".format(err)
        else:
            result += self.errcodes[err]
        await self.bot.say(result)

def setup(bot):
    bot.add_cog(NinErr(bot))
