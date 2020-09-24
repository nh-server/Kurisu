import re

from .types import Module, ResultCode, UNKNOWN_MODULE, NO_RESULTS_FOUND

"""
This file contains all currently known 2DS/3DS result and error codes. 
There may be inaccuracies here; we'll do our best to correct them 
when we find out more about them. It is also worth noting that apparently Nintendo
loved to use random modules for some of these error codes, due to the reporting
modules not making much sense (e.g., kernel reporting an internet authentication
 server error...).

A result code is a 32-bit integer returned when calling various commands in the
3DS's operating system, Horizon. Its breaks down like so:

 Bits | Description
-------------------
00-09 | Description
10-17 | Module
21-26 | Summary
27-31 | Level

Description: A value indicating exactly what happened.
Module: A value indicating who raised the error or returned the result.
Summary: A value indicating a shorter description of what happened.
Level: A value indicating the severity of the issue (fatal, temporary, etc.).

The 3DS makes it simple by providing all of these values directly. Other
consoles, such as the Wii U and Switch do not provide summaries or levels, so
those fields in the ResultCode class are re-used for other similar purposes.

To add a module so the code understands it, simply add a new module number
to the 'modules' dictionary, with a Module variable as the value. If the module
has no known error codes, simply add a dummy Module instead (see the dict for
more info). See the various module variables for a more in-depth example
 on how to make one.

Once you've added a module, or you want to add a new result code to an existing
module, add a new description value (for 3DS it's the 4 digit number after the dash)
as the key, and a ResultCode variable with a text description of the error or result.
You can also add a second string to the ResultCode to designate a support URL if
one exists. Not all results or errors have support webpages.

Simple example of adding a module with a sample result code:
test = Module('test', {
    5: ResultCode('test', 'https://example.com')
})

modules = {
    9999: test
}

Sources used to compile these results and information:
https://www.3dbrew.org/wiki/Error_codes
Kurisu's previous err.py module

TODO: Add a number of result codes that were in the previous result code Kurisu
used. They were left out for the sake of getting this initial code done faster.
"""

fssrv = Module('file server', {
    1099: ResultCode('Access point with given SSID not found.', 'https://en-americas-support.nintendo.com/app/answers/detail/a_id/4249/kw/003-1099'),
    2001: ResultCode('DNS error. If you\'re using a custom DNS server, make sure the settings are correct.')
})

srv = Module('srv', {
    5: ResultCode('Invalid string length (service name length is zero or longer than 8 chars).'),
    6: ResultCode('Access to service denied (requested a service the application does not have access to).'),
    7: ResultCode('String size does not match contents (service name contains unexpected null byte).')
})

fs = Module('fs', {
    101: ResultCode('Archive not mounted or mount-point not found.'),
    120: ResultCode('Title or object not found.'),
    141: ResultCode('Gamecard not inserted.'),
    230: ResultCode('Invalid open flags or permissions.'),
    391: ResultCode('NCCH hash check failed.'),
    302: ResultCode('RSA or AES-MAC verification failed.'),
    395: ResultCode('RomFS or Savedata hash check failed.'),
    630: ResultCode('Command not allowed, or missing permissions.'),
    702: ResultCode('Invalid path.'),
    761: ResultCode('Incorrect ExeFS read size.'),
    (100, 179): ResultCode('[Media] not found.'),
    (180, 199): ResultCode('Exists already.'),
    (200, 219): ResultCode('Not enough space.'),
    (220, 229): ResultCode('Invalidated archive.'),
    (230, 339): ResultCode('Unacceptable or write protected.'),
    (360, 389): ResultCode('Bad format.'),
    (390, 399): ResultCode('Verification failure.'),
    (600, 629): ResultCode('Out of resources.'),
    (630, 660): ResultCode('Access denied.'),
    (700, 729): ResultCode('Invalid argument.'),
    (730, 749): ResultCode('Not initialized.'),
    (750, 759): ResultCode('Already initialized.'),
    (760, 779): ResultCode('Not supported.')
})

common = Module('common', {
    0: ResultCode('Success'),
    1000: ResultCode('Invalid selection'),
    1001: ResultCode('Too large'),
    1002: ResultCode('Not authorized'),
    1003: ResultCode('Already done'),
    1004: ResultCode('Invalid size'),
    1005: ResultCode('Invalid enum value'),
    1006: ResultCode('Invalid combination'),
    1007: ResultCode('No data'),
    1008: ResultCode('Busy'),
    1009: ResultCode('Misaligned address'),
    1010: ResultCode('Misaligned size'),
    1011: ResultCode('Out of memory'),
    1012: ResultCode('Not implemented'),
    1013: ResultCode('Invalid address'),
    1014: ResultCode('Invalid pointer'),
    1015: ResultCode('Invalid handle'),
    1016: ResultCode('Not initialized'),
    1017: ResultCode('Already initialized'),
    1018: ResultCode('Not found'),
    1019: ResultCode('Cancel requested'),
    1020: ResultCode('Already exists'),
    1021: ResultCode('Out of range'),
    1022: ResultCode('Timeout'),
    1023: ResultCode('Invalid result value')
})

i2c = Module('i2c', {
    3021: ResultCode('Cannot find title on Nintendo eShop (incorrect region, or never existed?).'),
    3136: ResultCode('Nintendo eShop is currently unavailable. Try again later.'),
    6901: ResultCode('This console is permanently banned by Nintendo (displayed in Japanese for some reason).', is_ban=True)
})

kernel = Module('kernel', {
    2: ResultCode('Invalid memory permissions.')
})

codec = Module('codec', {
    16: ResultCode('Both consoles have the same movable.sed key. Format the target console and system transfer again.'),
    62: ResultCode('An error occurred during system transfer. Move closer to the wireless router and try again.')
})

am = Module('am', {
    4: ResultCode('Invalid ticket version.'),
    32: ResultCode('Empty CIA.'),
    37: ResultCode('Invalid NCCH.'),
    39: ResultCode('Invalid title version.'),
    43: ResultCode('Database doesn\'t exist, or it failed to open.'),
    44: ResultCode('Trying to uninstall system-app.'),
    106: ResultCode('Invalid signature/CIA.'),
    393: ResultCode('Invalid database.'),
    1820: ResultCode('Displayed when the browser asks if you want to go to to a potentially dangerous website. Press \'yes\' to continue if you feel it is safe.')
})

gpio = Module('gpio', {
    1511: ResultCode('Certificate warning.')
})

pm = Module('pm', {
    2452: ResultCode('Tried to access the eShop with UNITINFO patch enabled. Turn it off in Luma\'s options.'),
    2501: ResultCode('NNID is already linked to another system. This can be the result of using System Transfer (where all NNIDs associated with the system are moved, whether they are currently linked or not), restoring the source console\'s NAND, and then attempting to use applications which require an NNID.'),
    2511: ResultCode('System update required (displayed by Miiverse?).'),
    2613: ResultCode('Incorrect email or password when attempting to link an existing NNID. Can also happen if the NNID is already linked to another system, or if you attempt to download an application from the eShop without a linked NNID on the console.', 'https://en-americas-support.nintendo.com/app/answers/detail/a_id/4314/kw/022-2613'),
    2631: ResultCode('The NNID you are attempting to use has been deleted, or is unusable due to a System Transfer. A transferred NNID will only work on the target system.', 'https://en-americas-support.nintendo.com/app/answers/detail/a_id/4285/kw/022-2631'),
    2633: ResultCode('NNID is temporarily locked due to too many incorrect password attempts. Try again later.'),
    2634: ResultCode('NNID is not correctly linked on this console.', '[To fix it, follow these steps.](https://3ds.hacks.guide/godmode9-usage#removing-an-nnid-without-formatting-your-device)'),
    2812: ResultCode('This console is permanently banned by Nintendo for playing Pokémon Sun & Moon online before the release date illegally.', is_ban=True),
    2815: ResultCode('This console is banned from accessing Miiverse by Nintendo.'),
    5515: ResultCode('Network timeout.'),
})

util = Module('util', {
    102: ResultCode('This console is permanently banned by Nintendo.', is_ban=True),
    107: ResultCode('This console is temporarily (?) banned by Nintendo.', is_ban=True),
    119: ResultCode('System update is required. This is typically shown when the friends module is outdated.'),
    120: ResultCode('Game or title update is required. This is typically shown when the title you\'re trying to launch is outdated.'),
    121: ResultCode('Local friend code SEED has invalid signature. This should only happen if it has been modified.', is_ban=True),
    123: ResultCode('This console is permanently banned by Nintendo.', is_ban=True)
})

os = Module('os', {
    10: ResultCode('Not enough memory.'),
    26: ResultCode('Session closed by remote.'),
    47: ResultCode('Invalid command header.')
})

pdn = Module('pdn', {
    1000: ResultCode('System update required (friends module?).'),
    2913: ResultCode('NIM HTTP error, so the server is probably down. Try again later.'),
    2916: ResultCode('NIM HTTP error, so the server is probably down. Try again later.'),
    2920: ResultCode('Title has an invalid ticket. Delete the title and/or its ticket in FBI and install it again from a legitimate source like the Nintendo eShop, or from your game cartridges if using cart dumps.'),
    4079: ResultCode('Unable to access SD card.'),
    4998: ResultCode('Local content is newer. Unknown what causes this.'),
    6106: ResultCode('AM error in NIM. Bad ticket is likely.'),
    8401: ResultCode('The update data is corrupted. Delete it and reinstall.')
})

http = Module('http', {
    105: ResultCode('Request timed out.')
})

mvd = Module('mvd', {
    271: ResultCode('Invalid configuration.')
})

qtm = Module('qtm', {
    8: ResultCode('Camera is already in use or busy.')
})

avd = Module('avd', {
    212: ResultCode('Game is permanently banned from Pokémon Global Link for using altered or illegal save data.', is_ban=True)
})

# This is largely a dummy module, but FBI errors often get passed through the bot
# which return incorrect error strings. Since there's not really a feasible way to figure out the
# application which is throwing the error, this is the best compromise without giving the user
# false information.
application = Module('application-specific error', { 
    (0, 9999): ResultCode('The application raised an error. Please consult the application\'s source code or ask the author for assistance with it.')
})

# We have some modules partially documented, those that aren't have dummy Modules.
modules = {
    0: common,
    1: kernel,
    2: util,
    3: fssrv,
    4: Module('loader server'),
    6: os,
    7: Module('dbg'),
    8: Module('dmnt'),
    9: pdn,
    10: Module('gsp'),
    11: i2c,
    12: gpio,
    13: Module('dd'),
    14: codec,
    15: Module('spi'),
    16: Module('pxi'),
    17: fs,
    18: Module('di'),
    19: Module('hid'),
    20: Module('cam'),
    21: Module('pi'),
    22: pm,
    23: Module('pm_low'),
    24: Module('fsi'),
    25: srv,
    26: Module('ndm'),
    27: Module('nwm'),
    28: Module('soc'),
    29: Module('ldr'),
    30: Module('acc'),
    31: Module('romfs'),
    32: am,
    33: Module('hio'),
    34: Module('updater'),
    35: Module('mic'),
    36: Module('fnd'),
    37: Module('mp'),
    38: Module('mpwl'),
    39: Module('ac'),
    40: http,
    41: Module('dsp'),
    42: Module('snd'),
    43: Module('dlp'),
    44: Module('hio_low'),
    45: Module('csnd'),
    46: Module('ssl'),
    47: Module('am_low'),
    48: Module('nex'),
    49: Module('friends'),
    50: Module('rdt'),
    51: Module('applet'),
    52: Module('nim'),
    53: Module('ptm'),
    54: Module('midi'),
    55: Module('mc'),
    56: Module('swc'),
    57: Module('fatfs'),
    58: Module('ngc'),
    59: Module('card'),
    60: Module('cardnor'),
    61: Module('sdmc'),
    62: Module('boss'),
    63: Module('dbm'),
    64: Module('config'),
    65: Module('ps'),
    66: Module('cec'),
    67: Module('ir'),
    68: Module('uds'),
    69: Module('pl'),
    70: Module('cup'),
    71: Module('gyroscope'),
    72: Module('mcu'),
    73: Module('ns'),
    74: Module('news'),
    75: Module('ro'),
    76: Module('gd'),
    77: Module('card spi'),
    78: Module('ec'),
    79: Module('web browser'),
    80: Module('test'),
    81: Module('enc'),
    82: Module('pia'),
    83: Module('act'),
    84: Module('vctl'),
    85: Module('olv'),
    86: Module('neia'),
    87: Module('npns'),
    90: avd,
    91: Module('l2b'),
    92: mvd,
    93: Module('nfc'),
    94: Module('uart'),
    95: Module('spm'),
    96: qtm,
    97: Module('nfp'),
    254: application,
}

levels = {
    0:'Success',
    1:'Info',
    25:'Status',
    26:'Temporary',
    27:'Permanent',
    28:'Usage',
    29:'Reinitialize',
    30:'Reset',
    31:'Fatal'
}

summaries = {
    0:'Success',
    1:'Nothing happened',
    2:'Would block',
    3:'Out of resource',
    4:'Not found',
    5:'Invalid state',
    6:'Not supported',
    7:'Invalid argument',
    8:'Wrong argument',
    9:'Canceled',
    10:'Status changed',
    11:'Internal',
    63:'Invalid result value'
}

# regex for 3DS result code format "0XX-YYYY"
RE = re.compile(r'0\d{2}\-\d{4}')

CONSOLE_NAME = 'Nintendo 2DS/3DS'

# Suggested color to use if displaying information through a Discord bot's embed
COLOR = 0xCE181E

def is_valid(error):
    err_int = None
    if error.startswith('0x'):
        err_int = int(error, 16)
    if err_int:
        return err_int & 0x80000000
    return RE.match(error)

def get(error):
    level = None
    summary = None
    # TODO: can level and summary be derived from a
    # human-readable string? Probably not...
    if error.startswith("0x"):
        error.strip()
        err = int(error[2:], 16)
        desc = err & 0x3FF
        mod = (err >> 10) & 0xFF
        summary = (err >> 21) & 0x3F
        level = (err >> 27) & 0x1F
    else:
        mod = int(error[0:3])
        desc = int(error[4:])

    if mod in modules:
        if not modules[mod].data:
            return CONSOLE_NAME, modules[mod].name, NO_RESULTS_FOUND, COLOR
        ret = modules[mod].get_error(desc)
        ret.code = desc
        # Result codes in range 1000-1023 are common to all modules.
        if 1000 <= desc <= 1023:
            ret.description = common.data[desc].description
        ret.level = levels[level] if level in levels else None
        ret.summary = summaries[summary] if summary in summaries else None
        return CONSOLE_NAME, modules[mod].name, ret, COLOR

    return CONSOLE_NAME, None, UNKNOWN_MODULE, COLOR

