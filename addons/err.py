import binascii
import discord
import re
from discord.ext import commands
from discord import Color
from sys import argv

class Err:
    """
    Parses CTR error codes.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    # CTR Error Codes
    summaries = {
        0: 'Success',
        1: 'Nothing happened',
        2: 'Would block',
        3: 'Out of resource',
        4: 'Not found',
        5: 'Invalid state',
        6: 'Not supported',
        7: 'Invalid argument',
        8: 'Wrong argument',
        9: 'Canceled',
        10: 'Status changed',
        11: 'Internal',
        63: 'Invalid result value'
    }

    levels = {
        0: "Success",
        1: "Info",

        25: "Status",
        26: "Temporary",
        27: "Permanent",
        28: "Usage",
        29: "Reinitialize",
        30: "Reset",
        31: "Fatal"
    }

    modules = {
        0: 'Common',
        1: 'Kernel',
        2: 'Util',
        3: 'File server',
        4: 'Loader server',
        5: 'TCB',
        6: 'OS',
        7: 'DBG',
        8: 'DMNT',
        9: 'PDN',
        10: 'GSP',
        11: 'I2C',
        12: 'GPIO',
        13: 'DD',
        14: 'CODEC',
        15: 'SPI',
        16: 'PXI',
        17: 'FS',
        18: 'DI',
        19: 'HID',
        20: 'CAM',
        21: 'PI',
        22: 'PM',
        23: 'PM_LOW',
        24: 'FSI',
        25: 'SRV',
        26: 'NDM',
        27: 'NWM',
        28: 'SOC',
        29: 'LDR',
        30: 'ACC',
        31: 'RomFS',
        32: 'AM',
        33: 'HIO',
        34: 'Updater',
        35: 'MIC',
        36: 'FND',
        37: 'MP',
        38: 'MPWL',
        39: 'AC',
        40: 'HTTP',
        41: 'DSP',
        42: 'SND',
        43: 'DLP',
        44: 'HIO_LOW',
        45: 'CSND',
        46: 'SSL',
        47: 'AM_LOW',
        48: 'NEX',
        49: 'Friends',
        50: 'RDT',
        51: 'Applet',
        52: 'NIM',
        53: 'PTM',
        54: 'MIDI',
        55: 'MC',
        56: 'SWC',
        57: 'FatFS',
        58: 'NGC',
        59: 'CARD',
        60: 'CARDNOR',
        61: 'SDMC',
        62: 'BOSS',
        63: 'DBM',
        64: 'Config',
        65: 'PS',
        66: 'CEC',
        67: 'IR',
        68: 'UDS',
        69: 'PL',
        70: 'CUP',
        71: 'Gyroscope',
        72: 'MCU',
        73: 'NS',
        74: 'News',
        75: 'RO',
        76: 'GD',
        77: 'Card SPI',
        78: 'EC',
        79: 'Web Browser',
        80: 'Test',
        81: 'ENC',
        82: 'PIA',
        83: 'ACT',
        84: 'VCTL',
        85: 'OLV',
        86: 'NEIA',
        87: 'NPNS',
        90: 'AVD',
        91: 'L2B',
        92: 'MVD',
        93: 'NFC',
        94: 'UART',
        95: 'SPM',
        96: 'QTM',
        97: 'NFP (amiibo)',
        254: 'Application',
        255: 'Invalid result value'
    }

    descriptions = {
        0: 'Success',
        2: 'Invalid memory permissions (kernel)',
        4: 'Invalid ticket version (AM)',
        5: 'Invalid string length. This error is returned when service name length is greater than 8 or zero. (srv)',
        6: 'Access denied. This error is returned when you request a service that you don\'t have access to. (srv)',
        7: 'String size does not match string contents. This error is returned when service name contains an unexpected null byte. (srv)',
        8: 'Camera already in use/busy (qtm).',
        10: 'Not enough memory (os)',
        26: 'Session closed by remote (os)',
        37: 'Invalid NCCH? (AM)',
        39: 'Invalid title version (AM)',
        43: 'Database doesn\'t exist/failed to open (AM)',
        44: 'Trying to uninstall system-app (AM)',
        47: 'Invalid command header (OS)',
        335: '(No permission? Seemed to appear when JKSM was being used without its XML.)',
        101: 'Archive not mounted/mount-point not found (fs)',
        105: 'Request timed out (http)',
        106: 'Invalid signature/CIA? (AM)',
        120: 'Title/object not found? (fs)',
        141: 'Gamecard not inserted? (fs)',
        190: 'Failed to write file. Partition is full.',
        230: 'Invalid open-flags / permissions? (fs)',
        250: 'FAT operation denied (fs?)',
        271: 'Invalid configuration (mvd).',
        391: 'NCCH hash-check failed? (fs)',
        392: 'RSA/AES-MAC verification failed? (fs)',
        393: 'Invalid database? (AM)',
        395: 'RomFS/Savedata hash-check failed? (fs)',
        630: 'Command not allowed / missing permissions? (fs)',
        702: 'Invalid path? (fs)',
        761: 'Incorrect read-size for ExeFS? (fs)',
        1000: 'Invalid selection',
        1001: 'Too large',
        1002: 'Not authorized',
        1003: 'Already done',
        1004: 'Invalid size',
        1005: 'Invalid enum value',
        1006: 'Invalid combination',
        1007: 'No data',
        1008: 'Busy',
        1009: 'Misaligned address',
        1010: 'Misaligned size',
        1011: 'Out of memory',
        1012: 'Not implemented',
        1013: 'Invalid address',
        1014: 'Invalid pointer',
        1015: 'Invalid handle',
        1016: 'Not initialized',
        1017: 'Already initialized',
        1018: 'Not found',
        1019: 'Cancel requested',
        1020: 'Already exists',
        1021: 'Out of range',
        1022: 'Timeout',
        1023: 'Invalid result value'
    }

    # Nintendo Error Codes
    errcodes = {
        # Nintendo 3DS
        '001-0803': 'Could not communicate with authentication server.',
        '002-0102': 'System is banned by Nintendo. You cannot ask how to fix this issue here.',
        '002-0119': 'System update required (outdated friends-module)',
        '002-0120': 'Title update required (outdated title version)',
        '002-0121': 'Local friend code SEED has invalid signature.\n\nThis should not happen unless it is modified. The only use case for modifying this file is for system unbanning, so you cannot ask how to fix this issue here.',
        '003-2001': 'DNS error. If using a custom DNS server, make sure the settings are correct.',
        '005-4800': 'HTTP Status 500 (Internal Error), unknown cause(?). eShop servers might have issues.',
        '005-5602': 'Unable to connect to the eShop. This error is most likely the result of an incorrect region setting.\nMake sure your region is correctly set in System Settings. If you encounter this error after region-changing your system, make sure you followed all the steps properly.',
        '005-5964': 'Your Nintendo Network ID has been banned from accessing the eShop.\nIf you think this was unwarranted, you will have to contact Nintendo Support to have it reversed.',
        '005-7550': 'Replace SD card(?). Occurs on Nintendo eShop.',
        '006-0102': 'Unexpected error. Could probably happen trying to play an out-of-region title online?',
        '006-0332': 'Disconnected from the game server.',
        '006-0502': 'Could not connect to the server.\n\n• Check the [network status page](http://support.nintendo.com/networkstatus)\n• Move closer to your wireless router\n• Verify DNS settings. If "Auto-Obtain" doesn\'t work, try Google\'s Public DNS (8.8.8.8, 8.8.4.4) and try again.',
        '006-0612': 'Failed to join the session.',
        '007-2001': 'Usually the result after region-changing the system. New 3DS cannot fix this issue right now.',
        '007-2100': 'The connection to the Nintendo eShop timed out.\nThis may be due to an ongoing server maintenance, check <https://support.nintendo.com/networkstatus> to make sure the servers are operating normally. You may also encounter this error if you have a weak internet connection.',
        '007-2404': 'An error occurred while attempting to connect to the Nintendo eShop.\nMake sure you are running the latest firmware, since this error will appear if you are trying to access the eShop on older versions.',
        '007-2720': 'SSL error?',
        '007-2923': 'The Nintendo Servers are currently down for maintenance. Please try again later.',
        '007-3102': 'Cannot find title on Nintendo eShop. Probably pulled.',
        '009-1000': 'System update required. (friends module?)',
        '009-2913': 'HTTP error',
        '009-4998': '"Local content is newer."\nThe actual cause of this error is unknown.',
        '009-6106': '"AM error in NIM."\nThe actual cause of this error is unknown.',
        '009-8401': 'Update data corrupted. Delete and re-install.',
        '011-3021': 'Cannot find title on Nintendo eShop. Probably incorrect region, or never existed.',
        '011-3136': 'Nintendo eShop is currently unavailable. Try again later.',
        '012-1511': 'Certificate warning.',
        '014-0062': 'Error during System Transfer. Move closer to the wireless router and keep trying.',
        '022-2452': 'Occurs when trying to use Nintendo eShop with UNITINFO patches enabled.',
        '022-2501': 'Attempting to use a Nintendo Network ID on one system when it is linked on another. This can be the result of using System Transfer, then restoring the source system\'s NAND and attempting to use services that require a Nintendo Network ID.\n\nIn a System Transfer, all Nintendo Network ID accounts associated with the system are transferred over, whether they are currently linked or not.',
        '022-2511': 'System update required (what causes this? noticed while opening Miiverse, probably not friends module)',
        '022-2613': 'Incorrect e-mail or password when trying to link an existing Nintendo Network ID. Make sure there are no typos, and the given e-mail is the correct one for the given ID.\nIf you forgot the password, reset it at <https://id.nintendo.net/account/forgotten-password>',
        '022-2631': 'Nintendo Network ID deleted, or not usable on the current system. If you used System Transfer, the Nintendo Network ID will only work on the target system.',
        '022-2634': 'Nintendo Network ID is not correctly linked on the system. This can be a result of formatting the SysNAND using System Settings to unlink it from the EmuNAND.\n\n<steps on how to fix>\n\nTinyFormat is recommended for unlinking in the future.',
        '022-2812': 'System is banned by Nintendo. You cannot ask how to fix this issue here.',
        '032-1820': 'Browser error that asks whether you want to go on to a potentially dangerous website. Can be bypassed by touching "yes".',
        '090-0212': 'Game is banned from Pokémon Global Link. This is most likely as a result of using altered or illegal save data.',
        # Wii U
        '160-0102': 'Error in SLC/MLC or USB.',
        '160-0103': '"The system memory is corrupted (MLC)."',
        '160-0104': '"The system memory is corrupted (SLC)."',
        '160-0105': 'USB storage corrupted?',
        '199-9999': 'Usually occurs when trying to run an unsigned title without signature patches, or something unknown(?) is corrupted.',
    }

    switch_errcodes = {
        # Switch
        '007-1037': ['Could not detect an SD card.', None],
        '2001-0125': ['Executed svcCloseHandle on main-thread handle (No known support page)', None],
        '2002-6063': ['Attempted to read eMMC CID from browser? (No known support page)', None],
        '2005-0003': ['You are unable to download software.', 'http://en-americas-support.nintendo.com/app/answers/detail/a_id/22393'],
        '2110-3400': ['??? (temp)', 'http://en-americas-support.nintendo.com/app/answers/detail/a_id/22569/p/897'],
        '2162-0002': ['General userland crash', 'http://en-americas-support.nintendo.com/app/answers/detail/a_id/22596'],
        '2164-0020': ['Error starting software.', 'http://en-americas-support.nintendo.com/app/answers/detail/a_id/22539/p/897'],
        '2168-0000': ['Illegal opcode. (No known support page)', None],
        '2168-0001': ['Resource/Handle not available. (No known support page)', None],
        '2168-0002': ['Segmentation Fault. (No known support page)', None],
        '2168-0003': ['Memory access must be 4 bytes aligned. (No known support page)', None],
        '2811-5001': ['General connection error.', 'http://en-americas-support.nintendo.com/app/answers/detail/a_id/22392/p/897'],
    }

    def get_name(self, d, k):
        if k in d:
            return '{} ({})'.format(d[k], k)
        else:
            return '{}'.format(k)

    async def aaaa(self, rc):
        # i know this is shit that's the point
        if rc == 3735928559:
            await self.bot.say(binascii.unhexlify(hex(3273891394255502812531345138727304541163813328167758675079724534358388)[2:]).decode('utf-8'))
        elif rc == 3735927486:
            await self.bot.say(binascii.unhexlify(hex(271463605137058211622646033881424078611212374995688473904058753630453734836388633396349994515442859649191631764050721993573)[2:]).decode('utf-8'))
        elif rc == 2343432205:
            await self.bot.say(binascii.unhexlify(hex(43563598107828907579305977861310806718428700278286708)[2:]).decode('utf-8'))

    @commands.command(pass_context=True)
    async def err(self, ctx, err: str):
        """
        Parses Nintendo and CTR error codes, with a fancy embed. 0x prefix is not required.

        Example:
          .err 0xD960D02B
          .err 022-2634
        """
        if re.match('[0-1][0-9][0-9]\-[0-9][0-9][0-9][0-9]', err):
            embed = discord.Embed(title=err + (": Nintendo 3DS" if err[0] == "0" else ": Wii U"))
            embed.url = "http://www.nintendo.com/consumer/wfc/en_na/ds/results.jsp?error_code={}&system={}&locale=en_US".format(err, "3DS" if err[0] == "0" else "Wiiu")
            if err not in self.errcodes:
                embed.description = "I don't know this one! Click the error code for details on Nintendo Support.\n\nIf you keep getting this issue and Nintendo Support does not help, or know how to fix it, you should report relevant details to <@78465448093417472> so it can be added to the bot."
            else:
                embed.description = self.errcodes[err]
                embed.color = (Color(0xCE181E) if err[0] == "0" else Color(0x009AC7))
        # 0xE60012
        # Switch Error Codes (w/ website)
        # Switch Error Codes (w/o website)
        elif re.match('[0-9][0-9][0-9][0-9]\-[0-9][0-9][0-9][0-9]', err):
            embed = discord.Embed(title=err + ": Nintendo Switch")
            embed.url = "http://en-americas-support.nintendo.com/app/answers/landing/p/897"
            embed.color = Color(0xE60012)
            if re.match('2110\-1[0-9][0-9][0-9]', err):
                embed.url = "http://en-americas-support.nintendo.com/app/answers/detail/a_id/22594"
                embed.description = "General connection error."
            elif re.match('2110\-29[0-9][0-9]', err):
                embed.url = "http://en-americas-support.nintendo.com/app/answers/detail/a_id/22277/p/897"
                embed.description = "General connection error."
            elif re.match('2110\-2[0-8][0-9][0-9]', err):
                embed.url = "http://en-americas-support.nintendo.com/app/answers/detail/a_id/22263/p/897"
                embed.description = "General connection error."
            else:
                if err in self.switch_errcodes:
                    embed.url = self.switch_errcodes[err][1]
                    embed.description = self.switch_errcodes[err][0]
                else:
                    embed.color = embed.Empty
                    embed.description = "I don't know this one! Click the error code for details on Nintendo Support.\n\nIf you keep getting this issue and Nintendo Support does not help, and know how to fix it, you should report relevant details to <@78465448093417472> so it can be added to the bot."
        else:
            err = err.strip()
            if err.startswith("0x"):
                err = err[2:]
            rc = int(err, 16)
            await self.aaaa(rc)
            desc = rc & 0x3FF
            mod = (rc >> 10) & 0xFF
            summ = (rc >> 21) & 0x3F
            level = (rc >> 27) & 0x1F

            # garbage
            embed = discord.Embed(title="0x{:X}".format(rc))
            embed.add_field(name="Module", value=self.get_name(self.modules, mod), inline=False)
            embed.add_field(name="Description", value=self.get_name(self.descriptions, desc), inline=False)
            embed.add_field(name="Summary", value=self.get_name(self.summaries, summ), inline=False)
            embed.add_field(name="Level", value=self.get_name(self.levels, level), inline=False)
        await self.bot.say("", embed=embed)

    @commands.command(pass_context=True, hidden=True)
    async def ninerr(self, ctx):
        await self.bot.say("Merged with " + ctx.prefix + "err, use that instead")

def setup(bot):
    bot.add_cog(Err(bot))
