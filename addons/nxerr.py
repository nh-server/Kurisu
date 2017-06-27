import discord
import re
from discord.ext import commands

class NXErr:
    """
    Parses NX (Nintendo Switch) error codes.
    Uses http://switchbrew.org/index.php?title=Error_codes
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    # Modules
    modules = {
        1: 'Kernel',
        2: 'FS',
        3: 'NVIDIA',
        5: 'NCM',
        8: 'LR',
        9: 'RO service',
        10: 'CMIF (IPC command interface)',
        11: 'HIPC (IPC)',
        15: 'PM',
        16: 'NS',
        21: 'SM',
        22: 'RO userland',
        24: 'SDMMC',
        26: 'SPL',
        100: 'ETHC',
        105: 'Settings',
        110: 'NIFM',
        114: 'Display',
        116: 'NTC',
        117: 'FGM',
        120: 'PCIE',
        121: 'Friends',
        123: 'SSL',
        124: 'Account',
        126: 'Mii',
        129: 'Play Report',
        133: 'PCV',
        134: 'OMM',
        137: 'NIM',
        138: 'PSC',
        140: 'USB',
        143: 'BTM',
        147: 'ERPT',
        148: 'APM',
        154: 'NPNS',
        161: 'NFC',
        162: 'Userland assert',
        168: 'Userland crash',
        203: 'HID',
        206: 'Capture',
        651: 'TC',
        669: 'ARP',
        800: 'General web-applet',
        809: 'WifiWebAuthApplet',
        810: 'Whitelisted-applet',
        811: 'ShopN',
    }

    known_errcodes = {
        # 2162-0002
        0x4A2: 'Can be triggered by running [svcBreak](http://switchbrew.org/index.php?title=SVC). The svcBreak params have no affect on the value of the thrown error-code.',
        # 2168-0000
        0xA8: 'Userland ARM undefined instruction exception',
        # 2168-0001
        0x2A8: 'Userland ARM prefetch-abort due to PC set to non-executable region',
        # 2168-0002
        0x4A8: 'Userland ARM data abort. Also caused by abnormal process termination via [svcExitProcess](http://switchbrew.org/index.php?title=SVC). Note: directly jumping to nnMain()-retaddr from non-main-thread has the same result.',
        # 2168-0003
        0x6A8: 'Userland PC address not aligned to 4 bytes',

        0x20B: 'Size too big to fit to marshal.',
        0x20F: 'Pid not found',
        0x410: 'Title-id not found',
        0x615: 'Max sessions',
        0x816: 'Bad NRO magic',
        0xA05: '[NcaID](http://switchbrew.org/index.php?title=Content_Manager_services) not found. Returned when attempting to mount titles which exist that aren\'t *8XX titles, the same way *8XX titles are mounted.',
        0xC15: 'Invalid name (all zeroes)',
        0xC16: 'Bad NRR magic',
        0xE05: 'TitleId not found',
        0x1015: 'Permission denied',
        0x1805: 'Invalid StorageId',
        0x287C: 'Argument is NULL',
        0x2C7C: 'Argument is invalid',
        0x3C7C: 'Bad input buffer size',
        0x407C: 'Invalid input buffer',
        0x6609: 'Invalid memory state/permission',
        0x6A09: 'Invalid NRR',
        0x7802: 'The specified [NCA](http://switchbrew.org/index.php?title=NCA)-type doesn\'t exist for this title.',
        0xA209: 'Unaligned NRR address',
        0xA409: 'Bad NRR size',
        0xAA09: 'Bad NRR address',
        0xCA01: 'Invalid size',
        0xCC01: 'Invalid address (not page-aligned).',
        0xCE01: 'Address is NULL',
        0xD201: 'Handle-table full.',
        0xD401: 'Invalid memory state / invalid memory permissions.',
        0xD801: 'When trying to set executable permission on memory.',
        0xDC01: 'Stack address outside allowed range',
        0xDC05: 'Gamecard not inserted',
        0xE001: 'Invalid thread priority.',
        0xE201: 'Invalid processor id.',
        0xE401: 'Invalid handle.',
        0xE601: 'Syscall copy from user failed.',
        0xE801: 'ID1 outside valid range in svcGetInfo.',
        0xEA01: 'Time out? When you give 0 handles to svcWaitSynchronizationN.',
        0xEE01: 'When you give too many handles to svcWaitSynchronizationN.',
        0xF001: 'ID0 outside valid range in svcGetInfo.',
        0xF201: 'No such port',
        0xF601: 'Port remote dead',
        0xF801: 'Unhandled usermode exception',
        0xFA01: 'Wrong memory permission?',
        0x10601: 'Port max sessions exceeded',
        0x10801: 'Out of memory',
        0x11A0B: 'Went past maximum during marshalling.',
        0x17C05: 'Gamecard not initialized',
        0x1900B: 'IPC Query 0 failed.',
        0x1A80A: 'Bad magic (expected \'SFCO\')',
        0x1F405: 'Sdcard not inserted',
        0x1F610: 'Unexpected StorageId',
        0x25A0B: 'Remote process is dead',
        0x3D60B: 'IPC Query 1 failed.',
        0x3EA03: 'Invalid handle',
        0x3EE03: 'Invalid memory mirror',
        0x66932: '"Service is currently unavailable"',
        0x7D202: 'Process does not have RomFs ',
        0x7D402: 'Title-id not found',
        0x13B002: 'Gamecard not inserted',
        0x171402: 'Invalid gamecard handle.',
        0x196002: 'Out of memory',
        0x196202: 'Out of memory',
        0x1A4A02: 'Out of memory',
        0x235E02: 'NCA-path used with the wrong titleID.',
        0x250E02: '[Corrupted](http://switchbrew.org/index.php?title=NAX0) NAX0 header.',
        0x251002: 'Invalid [NAX0](http://switchbrew.org/index.php?title=NAX0) magicnum.',
        0x2EE202: 'Unknown media-id',
        0x2EE602: 'Path too long',
        0x2F5A02: 'Offset outside storage',
        0x313802: 'Operation not supported',
        0x320002: 'Permission denied',
        0x3CF089: 'Unknown/invalid libcurl error.',
    }

    known_errcode_ranges = {
        # NIM
        137: [
            [8001, 8096, 'libcurl error 1-96. Some of the libcurl errors in the error-table map to the above unknown-libcurl-error however.'],
        ]
    }

    def get_name(self, d, k):
        if k in d:
            return '{} ({})'.format(d[k], k)
        else:
            return '{}'.format(k)

    @commands.command(pass_context=True)
    async def serr(self, ctx, err: str):
        """
        Parses Nintendo Switch error codes according to http://switchbrew.org/index.php?title=Error_codes.

        Example:
          .serr 1A80A
          .serr 0xDC05
          .serr 2005-0110
        """
        if re.match('[0-9][0-9][0-9][0-9]\-[0-9][0-9][0-9][0-9]', err):
            module = int(err[0:4]) - 2000
            desc = int(err[5:9])
            errcode = (desc << 9) + module
        else:
            if err.startswith("0x"):
                err = err[2:]
            errcode = int(err, 16)
            module = errcode & 0x1FF
            desc = (errcode >> 9) & 0x3FFF
        str_errcode = '{:04}-{:04}'.format(module + 2000, desc)
        explanation = ''
        if errcode in self.known_errcodes:
            explanation += self.known_errcodes[errcode] + '\n\n'
        elif module in self.known_errcode_ranges:
            for errcode_range in self.known_errcode_ranges[module]:
                if desc >= errcode_range[0] and desc <= errcode_range[1]:
                    explanation += errcode_range[2] + '\n\n'
        explanation += 'Module: ' + self.get_name(self.modules, module)
        explanation += '\nDescription: {}'.format(desc)
        embed = discord.Embed(title='0x{:X} / {}'.format(errcode, str_errcode), description=explanation)
        await self.bot.say(embed=embed)

    @commands.command(pass_context=True)
    async def err2hex(self, ctx, err: str):
        if not re.match('[0-9][0-9][0-9][0-9]\-[0-9][0-9][0-9][0-9]', err):
            await self.bot.say('Does not follow XXXX-XXXX format')
        else:
            module = int(err[0:4]) - 2000
            desc = int(err[5:9])
            errcode = (desc << 9) + module
            await self.bot.say('0x{:X}'.format(errcode))

    @commands.command(pass_context=True)
    async def hex2err(self, ctx, err: str):
        if err.startswith("0x"):
            err = err[2:]
        err = int(err, 16)
        module = err & 0x1FF
        desc = (err >> 9) & 0x3FFF
        errcode = '{:04}-{:04}'.format(module + 2000, desc)
        await self.bot.say(errcode)


def setup(bot):
    bot.add_cog(NXErr(bot))
