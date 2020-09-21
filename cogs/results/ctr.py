import re

from .types import Module, ResultCode, UNKNOWN_MODULE, NO_RESULTS_FOUND

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

kernel = Module('kernel', {
    2: ResultCode('Invalid memory permissions.')
})

am = Module('am', {
    4: ResultCode('Invalid ticket version.'),
    32: ResultCode('Empty CIA.'),
    37: ResultCode('Invalid NCCH.'),
    39: ResultCode('Invalid title version.'),
    43: ResultCode('Database doesn\'t exist, or it failed to open.'),
    44: ResultCode('Trying to uninstall system-app.'),
    106: ResultCode('Invalid signature/CIA.'),
    393: ResultCode('Invalid database.')
})

util = Module('util', {
    102: ResultCode('This console is permanently banned by Nintendo.')
})

os = Module('os', {
    10: ResultCode('Not enough memory.'),
    26: ResultCode('Session closed by remote.'),
    47: ResultCode('Invalid command header.')
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

# regex for result code format "0XX-YYYY"
RE = re.compile(r'0\d{2}\-\d{4}')

CONSOLE_NAME = 'Nintendo 2DS/3DS'
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

