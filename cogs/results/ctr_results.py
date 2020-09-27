import re

from .types import Module, ResultInfo, UNKNOWN_MODULE, UNKNOWN_ERROR, NO_RESULTS_FOUND

"""
This file contains all currently known 2DS/3DS result and error codes (hexadecimal).
There may be inaccuracies here; we'll do our best to correct them
when we find out more about them.

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
those fields in the ResultInfo class are re-used for other similar purposes.

To add a module so the code understands it, simply add a new module number
to the 'modules' dictionary, with a Module variable as the value. If the module
has no known error codes, simply add a dummy Module instead (see the dict for
more info). See the various module variables for a more in-depth example
 on how to make one.

Once you've added a module, or you want to add a new result code to an existing
module, add a new description value (for 3DS it's the 4 digit number after the dash)
as the key, and a ResultInfo variable with a text description of the error or result.
You can also add a second string to the ResultInfo to designate a support URL if
one exists. Not all results or errors have support webpages.

Simple example of adding a module with a sample result code:
test = Module('test', {
    5: ResultInfo('test', 'https://example.com')
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

common = Module('common', {
    0: ResultInfo('Success'),
    1000: ResultInfo('Invalid selection'),
    1001: ResultInfo('Too large'),
    1002: ResultInfo('Not authorized'),
    1003: ResultInfo('Already done'),
    1004: ResultInfo('Invalid size'),
    1005: ResultInfo('Invalid enum value'),
    1006: ResultInfo('Invalid combination'),
    1007: ResultInfo('No data'),
    1008: ResultInfo('Busy'),
    1009: ResultInfo('Misaligned address'),
    1010: ResultInfo('Misaligned size'),
    1011: ResultInfo('Out of memory'),
    1012: ResultInfo('Not implemented'),
    1013: ResultInfo('Invalid address'),
    1014: ResultInfo('Invalid pointer'),
    1015: ResultInfo('Invalid handle'),
    1016: ResultInfo('Not initialized'),
    1017: ResultInfo('Already initialized'),
    1018: ResultInfo('Not found'),
    1019: ResultInfo('Cancel requested'),
    1020: ResultInfo('Already exists'),
    1021: ResultInfo('Out of range'),
    1022: ResultInfo('Timeout'),
    1023: ResultInfo('Invalid result value')
})

kernel = Module('kernel', {
    2: ResultInfo('Invalid memory permissions.')
})

os = Module('os', {
    10: ResultInfo('Not enough memory.'),
    26: ResultInfo('Session closed by remote.'),
    47: ResultInfo('Invalid command header.')
})

fs = Module('fs', {
    101: ResultInfo('Archive not mounted or mount-point not found.'),
    120: ResultInfo('Title or object not found.'),
    141: ResultInfo('Gamecard not inserted.'),
    230: ResultInfo('Invalid open flags or permissions.'),
    391: ResultInfo('NCCH hash check failed.'),
    302: ResultInfo('RSA or AES-MAC verification failed.'),
    395: ResultInfo('RomFS or Savedata hash check failed.'),
    630: ResultInfo('Command not allowed, or missing permissions.'),
    702: ResultInfo('Invalid path.'),
    761: ResultInfo('Incorrect ExeFS read size.'),
    (100, 179): ResultInfo('[Media] not found.'),
    (180, 199): ResultInfo('Exists already.'),
    (200, 219): ResultInfo('Not enough space.'),
    (220, 229): ResultInfo('Invalidated archive.'),
    (230, 339): ResultInfo('Unacceptable or write protected.'),
    (360, 389): ResultInfo('Bad format.'),
    (390, 399): ResultInfo('Verification failure.'),
    (600, 629): ResultInfo('Out of resources.'),
    (630, 660): ResultInfo('Access denied.'),
    (700, 729): ResultInfo('Invalid argument.'),
    (730, 749): ResultInfo('Not initialized.'),
    (750, 759): ResultInfo('Already initialized.'),
    (760, 779): ResultInfo('Not supported.')
})

srv = Module('srv', {
    5: ResultInfo('Invalid string length (service name length is zero or longer than 8 chars).'),
    6: ResultInfo('Access to service denied (requested a service the application does not have access to).'),
    7: ResultInfo('String size does not match contents (service name contains unexpected null byte).')
})

nwm = Module('nwm', {
    2: ResultInfo('This error usually indicates the wifi chipset in the console is dying or dead.')
})

am = Module('am', {
    4: ResultInfo('Invalid ticket version.'),
    32: ResultInfo('Empty CIA.'),
    37: ResultInfo('Invalid NCCH.'),
    39: ResultInfo('Invalid title version.'),
    43: ResultInfo('Database doesn\'t exist, or it failed to open.'),
    44: ResultInfo('Trying to uninstall system-app.'),
    106: ResultInfo('Invalid signature/CIA.'),
    393: ResultInfo('Invalid database.'),
})

http = Module('http', {
    105: ResultInfo('Request timed out.')
})

mvd = Module('mvd', {
    271: ResultInfo('Invalid configuration.')
})

qtm = Module('qtm', {
    8: ResultInfo('Camera is already in use or busy.')
})

# This is largely a dummy module, but FBI errors often get passed through the bot
# which return incorrect error strings. Since there's not really a feasible way to figure out the
# application which is throwing the error, this is the best compromise without giving the user
# false information.
application = Module('application-specific error', {
    (0, 9999): ResultInfo('The application raised an error. Please consult the application\'s source code or ask the author for assistance with it.')
})

# We have some modules partially documented, those that aren't have dummy Modules.
modules = {
    0: common,
    1: kernel,
    2: Module('util'),
    3: Module('file server'),
    4: Module('loader server'),
    5: Module('tcb'),
    6: os,
    7: Module('dbg'),
    8: Module('dmnt'),
    9: Module('pdn'),
    10: Module('gsp'),
    11: Module('i2c'),
    12: Module('gpio'),
    13: Module('dd'),
    14: Module('codec'),
    15: Module('spi'),
    16: Module('pxi'),
    17: fs,
    18: Module('di'),
    19: Module('hid'),
    20: Module('cam'),
    21: Module('pi'),
    22: Module('pm'),
    23: Module('pm_low'),
    24: Module('fsi'),
    25: srv,
    26: Module('ndm'),
    27: nwm,
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
    90: Module('avd'),
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
    0: 'Success',
    1: 'Info',
    25: 'Status',
    26: 'Temporary',
    27: 'Permanent',
    28: 'Usage',
    29: 'Reinitialize',
    30: 'Reset',
    31: 'Fatal'
}

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

# Would be provided for consistency
# but is_valid in here has its own logic.
# RE = None

CONSOLE_NAME = 'Nintendo 2DS/3DS'

# Suggested color to use if displaying information through a Discord bot's embed
COLOR = 0xCE181E


def is_valid(error: str):
    err_int = None
    if error.startswith('0x'):
        err_int = int(error, 16)
    if err_int is not None:
        module = (err_int >> 10) & 0xFF
        return (err_int & 0x80000000) and (module < 100 or module != 254)
    return False


def hexinfo(error: str):
    error.strip()
    err = int(error[2:], 16)
    desc = err & 0x3FF
    mod = (err >> 10) & 0xFF
    summary = (err >> 21) & 0x3F
    level = (err >> 27) & 0x1F
    return mod, summary, level, desc


def construct_result(mod, summary, level, desc):
    if mod in modules:
        in_common_range = desc in common.data
        if not modules[mod].data:
            if not in_common_range:
                return CONSOLE_NAME, modules[mod].name, NO_RESULTS_FOUND, COLOR
            else:
                ret = ResultInfo()  # Make a blank result that gets filled in below
        else:
            ret = modules[mod].get_error(desc)

        if in_common_range:
            ret.description = common.data[desc].description
        ret.level = levels[level] if level in levels else None
        ret.summary = summaries[summary] if summary in summaries else None
        return CONSOLE_NAME, modules[mod].name, ret, COLOR
    return CONSOLE_NAME, None, UNKNOWN_MODULE, COLOR


def get(error: str):
    mod, summary, level, desc = hexinfo(error)
    return construct_result(mod, summary, level, desc)
