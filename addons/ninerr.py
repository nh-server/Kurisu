import discord
import re
from discord import Color
from discord.ext import commands
from sys import argv

class NinErr:
    """
    Parses Nintendo 3DS / Wii U error codes.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    errcodes = {
        # Nintendo 3DS
        '001-0803': 'Could not communicate with authentication server.',
        '002-0102': 'System is banned by Nintendo. You cannot ask how to fix this issue here.',
        '002-0119': 'System update required (outdated friends-module)',
        '002-0120': 'Title update required (outdated title version)',
        '002-0121': 'Local friend code SEED has invalid signature.\n\nThis should not happen unless it is modified. The only use case for modifying this file is for system unbanning, so you cannot ask how to fix this issue here.',
        '005-4800': 'HTTP Status 500 (Internal Error), unknown cause(?). eShop servers might have issues.',
        '005-5602': 'Unable to connect to the eShop. This error is most likely the result of an incorrect region setting.\nMake sure your region is correctly set in System Settings. If you encounter this error after region-changing your system, make sure you followed all the steps properly.',
        '005-5964': 'Your Nintendo Network ID has been banned from accessing the eShop.\nIf you think this was unwarranted, you will have to contact Nintendo Support to have it reversed.',
        '006-0102': 'Unexpected error. Could probably happen trying to play an out-of-region title online?',
        '006-0332': 'Disconnected from the game server.',
        '006-0502': 'Could not connect to the server.\n\n• Check the [network status page](http://support.nintendo.com/networkstatus)\n• Move closer to your wireless router\n• Verify DNS settings. If "Auto-Obtain" doesn\'t work, try Google\'s Public DNS (8.8.8.8, 8.8.4.4) and try again.',
        '006-0612': 'Failed to join the session.',
        '007-2001': 'Usually the result after region-changing the system. New 3DS cannot fix this issue right now.',
        '007-2100': 'The connection to the Nintendo eShop timed out.\nThis may be due to an ongoing server maintenance, check <https://support.nintendo.com/networkstatus> to make sure the servers are operating normally. You may also encounter this error if you have a weak internet connection.',
        '007-2404': 'An error occurred while attempting to connect to the Nintendo eShop.\nMake sure you are running the latest firmware, since this error will appear if you are trying to access the eShop on older versions.',
        '007-2923': 'The Nintendo Servers are currently down for maintenance. Please try again later.',
        '007-3102': 'Cannot find title on Nintendo eShop. Probably pulled.',
        '009-6106': '"AM error in NIM."\nThe actual cause of this error is unknown.',
        '009-8401': 'Update data corrupted. Delete and re-install.',
        '011-3021': 'Cannot find title on Nintendo eShop. Probably incorrect region, or never existed.',
        '011-3136': 'Nintendo eShop is currently unavailable. Try again later.',
        '022-2452': 'Occurs when trying to use Nintendo eShop with UNITINFO patches enabled.',
        '022-2501': 'Attempting to use a Nintendo Network ID on one system when it is linked on another. This can be the result of using System Transfer, then restoring the source system\'s NAND and attempting to use services that require a Nintendo Network ID.\n\nIn a System Transfer, all Nintendo Network ID accounts associated with the system are transferred over, whether they are currently linked or not.',
        '022-2613': 'Incorrect e-mail or password when trying to link an existing Nintendo Network ID. Make sure there are no typos, and the given e-mail is the correct one for the given ID.\nIf you forgot the password, reset it at <https://id.nintendo.net/account/forgotten-password>',
        '022-2631': 'Nintendo Network ID deleted, or not usable on the current system. If you used System Transfer, the Nintendo Network ID will only work on the target system.',
        '022-2634': 'Nintendo Network ID is not correctly linked on the system. This can be a result of formatting the SysNAND using System Settings to unlink it from the EmuNAND.\n\n<steps on how to fix>\n\nTinyFormat is recommended for unlinking in the future.',
        '022-2812': 'System is banned by Nintendo. You cannot ask how to fix this issue here.',
        '090-0212': 'Game is banned from Pokémon Global Link. This is most likely as a result of using altered or illegal save data.',
        # Wii U
        '199-9999': 'Usually occurs when trying to run an unsigned title without signature patches, or something unknown(?) is corrupted.',
    }

    @commands.command(pass_context=True, name="ninerr")
    async def ninerr(self, ctx, errcode: str):
        """Parses Nintendo 3DS error codes."""
        err = errcode[0:8]
        if re.match('[0-1][0-9][0-9]\-[0-9][0-9][0-9][0-9]', err) == None:
            await self.bot.say("Wrong format. Error codes use the format `###-####`.")
            return
        embed = discord.Embed(title=err + (": Nintendo 3DS" if err[0] == "0" else ": Wii U"))
        embed.url = "http://www.nintendo.com/consumer/wfc/en_na/ds/results.jsp?error_code={}&system={}&locale=en_US".format(err, "3DS" if err[0] == "0" else "Wiiu")
        if err not in self.errcodes:
            embed.description = "I don't know this one! Click the error code for details on Nintendo Support.\n\nIf you keep getting this issue and Nintendo Support does not help, or know how to fix it, you should report relevant details to <@78465448093417472> so it can be added to the bot."
        else:
            embed.description = self.errcodes[err]
            embed.color = (Color.dark_red() if err[0] == "0" else Color.blue())
        await self.bot.say("", embed=embed)

def setup(bot):
    bot.add_cog(NinErr(bot))
