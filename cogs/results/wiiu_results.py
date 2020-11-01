import re

from .types import Module, ResultInfo, ConsoleErrorInfo, ConsoleErrorField

"""
This file contains all currently known Wii U result and error codes.
There may be inaccuracies here; we'll do our best to correct them
when we find out more about them.

A result code is a 32-bit integer returned when calling various commands in the
Wii U's operating system, Cafe OS. Its breaks down like so:

 Bits | Description
-------------------
00-03 | Level
04-12 | Module
13-31 | Description

Level: A value indicating the severity of the issue (fatal, temporary, etc.).
Module: A value indicating who raised the error or returned the result.
Description: A value indicating exactly what happened.

Alternatively, legacy results break down to: 

 Bits | Description
-------------------
00-02 | Unused
03-04 | Signature
05-11 | Module
12-13 | Unused
14-17 | Level
18-21 | Summary
22-32 | Description

Signature: A check to see if its legacy (although there's collisions with non legacy modules)
Summary: A value indicating a shorter description of what happened.

Unlike the 3DS, the Wii U does not provide a 'summary' field in non legacy result codes.

To add a module so the code understands it, simply add a new module number
to the 'modules' dictionary, with a Module variable as the value. If the module
has no known error codes, simply add a dummy Module instead (see the dict for
more info). See the various module variables for a more in-depth example
 on how to make one.

Once you've added a module, or you want to add a new result code to an existing
module, add a new description value (for Switch it's the final set of 4 digits after any dashes)
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

Sources used to compile this list of modules and result parsing:
https://github.com/devkitPro/wut/blob/b2e6bc52d0d5afa9eb9df21b52d2a61851935f39/include/nn/result.h#L67
"""
modules = {
    0: Module('common'),
    1: Module('ipc'),
    2: Module('boss'),
    3: Module('acp'),
    4: Module('ios'),
    5: Module('nim'),
    6: Module('pdm'),
    7: Module('act'),
    8: Module('ngc'),
    9: Module('eca'),
    10: Module('nup'),
    11: Module('ndm'),
    12: Module('fp'),
    13: Module('ac'),
    14: Module('conntest'),
    15: Module('drmapp'),
    16: Module('telnet'),
    17: Module('olv'),
    18: Module('vctl'),
    19: Module('neia'),
    20: Module('spm'),
    125: Module('test')
}

legacy_modules = {
    0: Module('common'),
    1: Module('kernel'),
    2: Module('util'),
    3: Module('file server'),
    4: Module('loader server'),
    5: Module('tcb'),
    6: Module('os'),
    7: Module('dbg'),
    8: Module('dmnt'),
    9: Module('pdn'),
    10: Module('cx'),
    11: Module('i2c'),
    12: Module('gpio'),
    13: Module('dd'),
    14: Module('codec'),
    15: Module('spi'),
    16: Module('pxi'),
    17: Module('fs'),
    18: Module('di'),
    19: Module('hid'),
    20: Module('camera'),
    21: Module('pi'),
    22: Module('pm'),
    23: Module('pmlow'),
    24: Module('fsi'),
    25: Module('srv'),
    26: Module('ndm'),
    27: Module('nwm'),
    28: Module('socket'),
    29: Module('ldr'),
    30: Module('acc'),
    31: Module('romfs'),
    32: Module('am'),
    33: Module('hio'),
    34: Module('updater'),
    35: Module('mic'),
    36: Module('fnd'),
    37: Module('mp'),
    38: Module('mpwl'),
    39: Module('ac'),
    40: Module('http'),
    41: Module('dsp'),
    42: Module('snd'),
    43: Module('dlp'),
    44: Module('hiolow'),
    45: Module('csnd'),
    46: Module('ssl'),
    47: Module('amlow'),
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
    64: Module('cfg'),
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
    77: Module('cardspi'),
    78: Module('ec'),
    79: Module('webbrs'),
    80: Module('test'),
    81: Module('enc'),
    82: Module('pia'),
    510: Module('application')
}

levels = {
    0: 'Success',
    1: 'End', # -7
    5: 'Status', # -3
    6: 'Usage', # -2
    7: 'Fatal' # -1
}

legacy_levels = {
    1: 'Info',
    9: 'Temporary', # -7
    10: 'Permanent', # -6
    11: 'Reinit', # -5
    12: 'Reset' # -4
}

legacy_summary = {
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
    11: 'Internal'
}

SIGNATURE_IS_LEGACY = 3


CONSOLE_NAME = 'Nintendo Wii U'

# Suggested color to use if displaying information through a Discord bot's embed
COLOR = 0x009AC7


def is_valid(error: str):
    err_int = None
    try:
        err_int = int(error, 16)
    except ValueError:
        return False
    return True if err_int.bit_length() <= 32 else False


def construct_result(ret, mod, summary, level, desc, is_legacy):
    module = (legacy_modules if is_legacy else modules).get(mod, Module(''))
    common = (legacy_modules if is_legacy else modules)[0]
    ret.add_field(ConsoleErrorField('Module', message_str = module.name, supplementary_value = mod))
    if is_legacy:
        ret.extra_description = "Legacy result"
    if is_legacy and summary is not None:
        ret.add_field(ConsoleErrorField('Summary', message_str = legacy_summary.get(summary, ''), supplementary_value = summary))
    ret.add_field(ConsoleErrorField('Level', message_str = (legacy_levels if is_legacy else levels).get(level, ''), supplementary_value = level))
    description = module.get_error(desc)
    if description is None:
        description = common.get_error(desc)
        if description is None:
            ret.add_field(ConsoleErrorField('Description', supplementary_value = desc))
        else:
            ret.add_field(ConsoleErrorField('Description', message_str = description.description, supplementary_value = desc))
    else:
        ret.add_field(ConsoleErrorField('Description', message_str = description.description, supplementary_value = desc))

    return ret


def get(error: str):
    level = None
    err_int = int(error, 16)
    # is this really how it is to check legacy?
    # based on wut's result.h it is.
    # but also causes collisions non legacy result modules!!
    if ((err_int >> 3) & 0x3) == SIGNATURE_IS_LEGACY:
        mod = (err_int >> 5) & 0x7F
        level = (err_int >> 14) & 0xF
        summary = (err_int >> 18) & 0xF
        desc = (err_int >> 22) & 0x3FF
        is_legacy = True
    else:
        level = err_int & 0x7
        mod = (err_int >> 3) & 0x1FF
        desc = (err_int >> 12) & 0xFFFFF
        summary = None
        is_legacy = False

    ret = ConsoleErrorInfo(error, CONSOLE_NAME, COLOR)
    return construct_result(ret, mod, summary, level, desc, is_legacy)

