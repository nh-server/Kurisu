import discord
from discord.ext import commands
from sys import argv

class CTRErr:
    """
    Parses CTR error codes.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

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
      101: 'Archive not mounted/mount-point not found (fs)',
      105: 'Request timed out (http)',
      106: 'Invalid signature/CIA? (AM)',
      120: 'Title/object not found? (fs)',
      141: 'Gamecard not inserted? (fs)',
      190: 'Failed to write file. Partition is full.',
      230: 'Invalid open-flags / permissions? (fs)',
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

    def get_name(self, d, k):
        if k in d:
            return '{} ({})'.format(d[k], k)
        else:
            return '{}'.format(k)

    @commands.command(pass_context=True, name="err")
    async def err(self, ctx, err: str):
        """Parses CTR error codes. 0x prefix is not required. \n Example: .err 0xD960D02B"""
        err = err.strip()
        if err.startswith("0x"):
            err = err[2:]
        rc = int(err, 16)
        desc  = rc & 0x3FF
        mod   = (rc >> 10) & 0xFF
        summ  = (rc >> 21) & 0x3F
        level = (rc >> 27) & 0x1F

        # garbage
        result  = '\n__**Module**__: '
        result += self.get_name(self.modules, mod)
        result += '\n__**Description**__: '
        result += self.get_name(self.descriptions, desc)
        result += '\n__**Summary**__: '
        result += self.get_name(self.summaries, summ)
        result += '\n__**Level**__: '
        result += self.get_name(self.levels, level)
        await self.bot.say(result)

def setup(bot):
    bot.add_cog(CTRErr(bot))
