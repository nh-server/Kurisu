import re

from .types import Module, ResultCode, UNKNOWN_MODULE, NO_RESULTS_FOUND

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

Unlike the 3DS, the Wii U does not provide a 'summary'
field in result codes, so some artistic license was taken here to repurpose those
fields in our ResultCode class to add additional information from sources
such as the NintendoClients wiki.

Currently our Wii U result code parsing does not understand hexadecimal
values. It is planned in the future to add support for these.

To add a module so the code understands it, simply add a new module number
to the 'modules' dictionary, with a Module variable as the value. If the module
has no known error codes, simply add a dummy Module instead (see the dict for
more info). See the various module variables for a more in-depth example
 on how to make one.

Once you've added a module, or you want to add a new result code to an existing
module, add a new description value (for Switch it's the final set of 4 digits after any dashes)
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

Sources used to compile this list of results:
https://github.com/Kinnay/NintendoClients/wiki/Wii-U-Error-Codes
https://github.com/devkitPro/wut/blob/master/include/nn/result.h#L67
"""

fp = Module('fp (friends)', {
    0: ResultCode('Success.'),
    1: ResultCode('Session closed.'),
    10: ResultCode('Programming error.'),
    11: ResultCode('Not initialized.'),
    12: ResultCode('Already initialized.'),
    13: ResultCode('Invalid argument.'),
    14: ResultCode('Busy.'),
    15: ResultCode('Network clock is invalid.'),
    16: ResultCode('Not permitted.'),
    100: ResultCode('Undefined error.'),
    101: ResultCode('Reserved error 01.'),
    102: ResultCode('Unknown error.'),
    103: ResultCode('Not implemented.'),
    104: ResultCode('Invalid pointer.'),
    105: ResultCode('Operation aborted.'),
    106: ResultCode('Exception occurred.'),
    107: ResultCode('Access denied.'),
    108: ResultCode('Invalid handle.'),
    109: ResultCode('Invalid index.'),
    110: ResultCode('Out of memory.'),
    111: ResultCode('Invalid argument.'),
    112: ResultCode('Timeout.'),
    113: ResultCode('Initialization failure.'),
    114: ResultCode('Call initiation failure.'),
    115: ResultCode('Registration error.'),
    116: ResultCode('Buffer overflow.'),
    117: ResultCode('Invalid lock state.'),
    200: ResultCode('Undefined.'),
    201: ResultCode('Invalid signature.'),
    202: ResultCode('Incorrect version.'),
    300: ResultCode('Undefined.'),
    301: ResultCode('Connection failure.'),
    302: ResultCode('Not authenticated.'),
    303: ResultCode('Invalid username.'),
    304: ResultCode('Invalid password.'),
    305: ResultCode('Username already exists.'),
    306: ResultCode('Account is disabled.'),
    307: ResultCode('Account is expired.'),
    308: ResultCode('Concurrent login denied.'),
    309: ResultCode('Encryption failure.'),
    310: ResultCode('Invalid PID.'),
    311: ResultCode('Max connections reached.'),
    312: ResultCode('Invalid GID.'),
    313: ResultCode('Invalid thread ID.'),
    314: ResultCode('Invalid operation in live environment.'),
    315: ResultCode('Duplicate entry.'),
    316: ResultCode('Control script failure.'),
    317: ResultCode('Class not found.'),
    318: ResultCode('Reserved 18.'),
    319: ResultCode('Reserved 19.'),
    320: ResultCode('DDL mismatch.'),
    321: ResultCode('Reserved 21.'),
    322: ResultCode('Reserved 22.'),
    400: ResultCode('Undefined error.'),
    401: ResultCode('Exception occurred.'),
    402: ResultCode('Type error.'),
    403: ResultCode('Index error.'),
    404: ResultCode('Invalid reference.'),
    405: ResultCode('Call failure.'),
    406: ResultCode('Memory error.'),
    407: ResultCode('Operation error.'),
    408: ResultCode('Conversion error.'),
    409: ResultCode('Validation error.'),
    500: ResultCode('Undefined error.'),
    501: ResultCode('Unknown error.'),
    502: ResultCode('Connection failure.'),
    503: ResultCode('Invalid URL.'),
    504: ResultCode('Invalid key.'),
    505: ResultCode('Invalid URL type.'),
    506: ResultCode('Duplicate endpoint.'),
    507: ResultCode('I/O error.'),
    508: ResultCode('Timeout.'),
    509: ResultCode('Connection reset.'),
    510: ResultCode('Incorrect remote authentication.'),
    511: ResultCode('Server request error.'),
    512: ResultCode('Decompression failure.'),
    513: ResultCode('Congested end-point.'),
    514: ResultCode('Reserved 14.'),
    515: ResultCode('Reserved 15.'),
    516: ResultCode('Reserved 16.'),
    517: ResultCode('Reserved 17.'),
    518: ResultCode('Socket send warning.'),
    519: ResultCode('Unsupported NAT.'),
    520: ResultCode('DNS error.'),
    521: ResultCode('Proxy error.'),
    522: ResultCode('Data remaining.'),
    523: ResultCode('No buffer.'),
    524: ResultCode('Not found.'),
    600: ResultCode('Undefined error.'),
    700: ResultCode('Undefined error.'),
    701: ResultCode('Reserved 1.'),
    702: ResultCode('Not initialized.'),
    703: ResultCode('Already initialized.'),
    704: ResultCode('Not connected.'),
    705: ResultCode('Connected.'),
    706: ResultCode('Initialization failure.'),
    707: ResultCode('Out of memory.'),
    708: ResultCode('RMC failed.'),
    709: ResultCode('Invalid argument.'),
    710: ResultCode('Reserved 10.'),
    711: ResultCode('Invalid principal ID.'),
    712: ResultCode('Reserved 12.'),
    713: ResultCode('Reserved 13.'),
    714: ResultCode('Reserved 14.'),
    715: ResultCode('Reserved 15.'),
    716: ResultCode('Reserved 16.'),
    717: ResultCode('Reserved 17.'),
    718: ResultCode('Reserved 18.'),
    719: ResultCode('Reserved 19.'),
    720: ResultCode('File I/O error.'),
    721: ResultCode('P2P internet prohibited.'),
    722: ResultCode('Unknown error.'),
    723: ResultCode('Invalid state.'),
    724: ResultCode('Reservd 24.'),
    725: ResultCode('Adding a friend is prohibited.'),
    726: ResultCode('Reserved 26.'),
    727: ResultCode('Invalid account.'),
    728: ResultCode('Blacklisted by me.'),
    729: ResultCode('Reserved 29.'),
    730: ResultCode('Friend already added.'),
    731: ResultCode('Friend list limit exceeded.'),
    732: ResultCode('Requests limit exceeded.'),
    733: ResultCode('Invalid message ID.'),
    734: ResultCode('Message is not mine.'),
    735: ResultCode('Message is not for me.'),
    736: ResultCode('Friend request blocked.'),
    737: ResultCode('Not in my friend list.'),
    738: ResultCode('Friend listed by me.'),
    739: ResultCode('Not in my blackist.'),
    740: ResultCode('Incompatible account.'),
    741: ResultCode('Block setting change not allowed.'),
    742: ResultCode('Size limit exceeded.'),
    743: ResultCode('Operation not allowed.'),
    744: ResultCode('Not a network account.'),
    745: ResultCode('Notification not found.'),
    746: ResultCode('Preference not initialized.'),
    747: ResultCode('Friend request not allowed.'),
    800: ResultCode('Undefined error.'),
    801: ResultCode('Account library error.'),
    802: ResultCode('Token parse error.'),
    803: ResultCode('Reserved 3.'),
    804: ResultCode('Reserved 4.'),
    805: ResultCode('Reserved 5.'),
    806: ResultCode('Token expired.'),
    807: ResultCode('Validation failed.'),
    808: ResultCode('Invalid parameters.'),
    809: ResultCode('Principal ID unmatched.'),
    810: ResultCode('Reserved 10.'),
    811: ResultCode('Under maintenance.'),
    812: ResultCode('Unsupported version.'),
    813: ResultCode('Unknown error.')
}, 
{
    (100, 199): 'Core',
    (200, 299): 'DDL',
    (300, 399): 'Rendezvous',
    (400, 499): 'Python Core',
    (500, 599): 'Transport',
    (600, 699): 'DO Core',
    (700, 799): 'FPD',
    (800, 899): 'Authentication',
    (1100, 1199): 'Ranking',
    (1200, 1299): 'Data Store',
    (1500, 1599): 'Service Item',
    (1800, 1899): 'Matchmaking Referee',
    (1900, 1999): 'Subscriber',
    (2000, 2099): 'Ranking2',
})

act = Module('act (accounts)', {
    0: ResultCode('Success.'),
    1: ResultCode('Mail address not confirmed.'),
    500: ResultCode('Library error.'),
    501: ResultCode('Not initialized.'),
    502: ResultCode('Already initialized.'),
    511: ResultCode('Busy.'),
    591: ResultCode('Not implemented.'),
    592: ResultCode('Deprecated.'),
    593: ResultCode('Development only.'),
    600: ResultCode('Invalid argument.'),
    601: ResultCode('Invalid pointer.'),
    602: ResultCode('Out of range.'),
    603: ResultCode('Invalid size.'),
    604: ResultCode('Invalid format.'),
    605: ResultCode('Invalid handle.'),
    606: ResultCode('Invalid value.'),
    700: ResultCode('Internal error.'),
    701: ResultCode('End of stream.'),
    710: ResultCode('File error.'),
    711: ResultCode('File not found.'),
    712: ResultCode('File version mismatch.'),
    713: ResultCode('File I/O error.'),
    714: ResultCode('File type mismatch.'),
    730: ResultCode('Out of resources.'),
    731: ResultCode('Buffer is insufficient.'),
    740: ResultCode('Out of memory.'),
    741: ResultCode('Out of global heap.'),
    742: ResultCode('Out of cross-process heap.'),
    744: ResultCode('Out of MXML heap.'),
    800: ResultCode('Generic error.'),
    801: ResultCode('Open error.'),
    802: ResultCode('Read sys-config error.'),
    810: ResultCode('Generic error.'),
    811: ResultCode('Open error.'),
    812: ResultCode('Get info error.'),
    820: ResultCode('Generic error.'),
    821: ResultCode('Initialization failure.'),
    822: ResultCode('Get country code failure.'),
    823: ResultCode('Get language code failure.'),
    850: ResultCode('Generic error.'),
    900: ResultCode('Generic error.'),
    901: ResultCode('Open error.'),
    1000: ResultCode('Management error.'),
    1001: ResultCode('Not found.'),
    1002: ResultCode('Slots full.'),
    1011: ResultCode('Not loaded.'),
    1012: ResultCode('Already loaded.'),
    1013: ResultCode('Locked.'),
    1021: ResultCode('Not a network account.'),
    1022: ResultCode('Not a local account.'),
    1023: ResultCode('Not committed.'),
    1101: ResultCode('Network clock is invalid.'),
    2000: ResultCode('Authentication error.'),
    # TODO: 2001-2644 (there aren't really that many errors)
    2643: ResultCode('Authentication is required.'),
    2651: ResultCode('Confirmation code is expired.'),
    2661: ResultCode('Mail address is not validated.'),
    2662: ResultCode('Excessive mail send requests.'),
    2670: ResultCode('Generic error.'),
    2671: ResultCode('General failure.'),
    2672: ResultCode('Declined.'),
    2673: ResultCode('Blacklisted.'),
    2674: ResultCode('Invalid credit card number.'),
    2675: ResultCode('Invalid credit card date.'),
    2676: ResultCode('Invalid credit card PIN.'),
    2677: ResultCode('Invalid postal code.'),
    2678: ResultCode('Invalid location.'),
    2679: ResultCode('Card is expired.'),
    2680: ResultCode('Credit card number is wrong.'),
    2681: ResultCode('PIN is wrong.'),
    
    2800: ResultCode('Banned.', is_ban=True),
    2801: ResultCode('Account is banned.', is_ban=True),
    2802: ResultCode('Account is banned from all services.', is_ban=True),
    2803: ResultCode('Account is banned from a particular game.', is_ban=True),
    2804: ResultCode('Account is banned from Nintendo\'s online service.', is_ban=True),
    2805: ResultCode('Account is banned from independent services.', is_ban=True),
    2811: ResultCode('Console is banned.', is_ban=True),
    2812: ResultCode('Console is banned from all services.', is_ban=True),
    2813: ResultCode('Console is banned from a particular game.', is_ban=True),
    2814: ResultCode('Console is banned from Nintendo\'s online service.', is_ban=True),
    2815: ResultCode('Console is banned from independent services.', is_ban=True),
    2816: ResultCode('Console is banned for an unknown duration, due to using modified/hacked files in online games like Splatoon.', is_ban=True),
    2821: ResultCode('Account is temporarily banned.', is_ban=True),
    2822: ResultCode('Account is temporarily banned from all services.', is_ban=True),
    2823: ResultCode('Account is temporarily banned from a particular game.', is_ban=True),
    2824: ResultCode('Account is temporarily banned from Nintendo\'s online service.', is_ban=True),
    2825: ResultCode('Acccount is temporarily banned from independent services.', is_ban=True),
    2831: ResultCode('Console is temporarily banned.', is_ban=True),
    2832: ResultCode('Console is temporarily banned from all services.', is_ban=True),
    2833: ResultCode('Console is temporarily banned from a particular game.', is_ban=True),
    2834: ResultCode('Console is temporarily banned from Nintendo\'s online service.', is_ban=True),
    2835: ResultCode('Console is temporarily banned from independent services.', is_ban=True),
    2880: ResultCode('Service is not provided.'),
    2881: ResultCode('Service is currently under maintenance.'),
    2882: ResultCode('Service is closed.'),
    2883: ResultCode('Nintendo Network is closed.'),
    2884: ResultCode('Service is not provided in this country.'),
    2900: ResultCode('Restriction error.'),
    2901: ResultCode('Restricted by age.'),
    2910: ResultCode('Restricted by parental controls.'),
    2911: ResultCode('In-game internet communication/chat is restricted.'),
    2931: ResultCode('Internal server error.'),
    2932: ResultCode('Unknown server error.'),
    2998: ResultCode('Unauthenticated after salvage.'),
    2999: ResultCode('Unknown authentication failure.'),
    
},
{
    (0, 499): 'Internal',
    (500, 599): 'Status changed',
    (600, 699): 'Invalid argument',
    (700, 709): 'Internal error',
    (710, 729): 'File error',
    (730, 799): 'Out of resources',
    (800, 809): 'UC',
    (810, 819): 'MCP',
    (820, 849): 'ISO',
    (850, 899): 'MXML',
    (900, 999): 'IOS',
    (1000, 1099): 'Account',
    (2100, 2199): 'HTTP',
    (2500, 2599): 'Account',
    (2670, 2699): 'Credit Card',
    (2800, 2835): 'Banned',
    (2880, 2899): 'Not available', # not provided/under maintenance/no longer in service
})

nex = Module('nex (game servers)', {
    102: ResultCode('The reason for the error is unknown.'),
    103: ResultCode('The operation is currently not implemented.'),
    104: ResultCode('The operation specifies or accesses an invalid pointer.'),
    105: ResultCode('The operation was aborted.'),
    106: ResultCode('The operation raised an exception.'),
    107: ResultCode('An attempt was made to access data in an incorrect manner. This may be due to inadequate permission or the data, file, etc. not existing.'),
    108: ResultCode('The operation specifies or accesses an invalid DOHandle.'),
    109: ResultCode('The operation specifies or accesses an invalid index.'),
    110: ResultCode('The system could not allocate or access enough memory or disk space to perform the specified operation.'),
    111: ResultCode('Invalid argument were passed with the operation. The argument(s) may be out of range or invalid.'),
    112: ResultCode('The operation did not complete within the specified timeout for that operation.'),
    113: ResultCode('Initialization of the component failed.'),
    114: ResultCode('The call failed to initialize.'),
    115: ResultCode('An error occurred during registration.'),
    116: ResultCode('The buffer is too large to be sent.'),
    117: ResultCode('Invalid lock state.'),
    118: ResultCode('Invalid sequence.'),
    301: ResultCode('Connection was unable to be established, either with the Rendez-Vous back end or a Peer.'),
    302: ResultCode('The Principal could not be authenticated by the Authentication Service.'),
    303: ResultCode('The Principal tried to log in with an invalid user name, i.e. the user name does not exist in the database.'),
    304: ResultCode('The Principal either tried to log in with an invalid password for the provided user name or tried to join a Gathering with an invalid password.'),
    305: ResultCode('The provided user name already exists in the database. All usernames must be unique.'),
    306: ResultCode('The Principal\'s account still exists in the database but the account has been disabled.', is_ban=True),
    307: ResultCode('The Principal\'s account still exists in the database but the account has expired.'),
    308: ResultCode('The Principal does not have the Capabilities to perform concurrent log ins, i.e. at any given time only one log-in may be maintained.'),
    309: ResultCode('Data encryption failed.'),
    310: ResultCode('The operation specifies or accesses an invalid PrincipalID.'),
    311: ResultCode('Maximum connnection number is reached.'),
    312: ResultCode('Invalid GID.'),
    313: ResultCode('Invalid Control script ID.'),
    314: ResultCode('Invalid operation in live/production environment.'),
    315: ResultCode('Duplicate entry.'),
    346: ResultCode('NNID is permanently banned.', is_ban=True),
    501: ResultCode('The reason for the error is unknown.'),
    502: ResultCode('Network connection was unable to be established.'),
    503: ResultCode('The URL contained in the StationURL is invalid. The syntax may be incorrect.'),
    504: ResultCode('The key used to authenticate a given station is invalid. The secure transport layer uses secret-key based cryptography to ensure the integrity and confidentiality of data sent across the network.'),
    505: ResultCode('The specified transport type is invalid.'),
    506: ResultCode('The Station is already connected via another EndPoint.'),
    507: ResultCode('The data could not be sent across the network. This could be due to an invalid message, packet, or buffer.'),
    508: ResultCode('The operation did not complete within the specified timeout for that operation.'),
    509: ResultCode('The network connection was reset.'),
    510: ResultCode('The destination Station did not authenticate itself properly.'),
    511: ResultCode('3rd-party server or device answered with an error code according to protocol used e.g. HTTP error code.'),
},
{
    (100, 199):'Core',
    (200, 299):'DDL',
    (300, 399):'Rendezvous',
    (400, 499):'Python Core',
    (500, 599):'Transport',
    (600, 699):'DO Core',
    (700, 799):'FPD',
    (800, 899):'Authentication',
    (1100, 1199): 'Ranking',
    (1200, 1299): 'Data Store',
    (1500, 1599): 'Service Item',
    (1800, 1899): 'Matchmaking Referee',
    (1900, 1999): 'Subscriber',
    (2000, 2099): 'Ranking2',
})

eshop_api = Module('eshop(api)', {
    3190: ResultCode('Wishlist is full.')
})

eshop_web = Module('eshop (web)', {
    9000: ResultCode('Close application (Connection timeout issue?).'),
    9001: ResultCode('Retriable.'),
    9002: ResultCode('Online services are undergoing maintenance.'),
    9003: ResultCode('The online services are discontinued and thus are no longer available.'),
    9100: ResultCode('Invalid template.')
})

unknown2 = Module('unknown (browser?)', {
    1037: ResultCode('Incorrect permissions for the default index.html file which prevents the Internet Browser from reading it.', '[To fix it, follow these steps.](https://wiiu.hacks.guide/#/fix-errcode-112-1037)'),
})

olv = Module('olv (miiverse)', {
    1009: ResultCode('Console is permanently banned from Miiverse.', is_ban=True),
    5004: ResultCode('The Miiverse service has been discontinued.')
})

eshop_unk = Module('eShop (unknown)', {
    9622: ResultCode('Error when attempting to add funds. Check that the payment method is correct or try again later.')
})

fs = Module('fs', {
    1031: ResultCode('The disc could not be read or is unsupported (i.e. not a Wii or Wii U game). Try cleaning the disc or lens if it is a supported title.'),
    2031: ResultCode('The disc could not be read or is unsupported (i.e. not a Wii or Wii U game). Try cleaning the disc or lens if it is a supported title.')
})

syserr = Module('system error', {
    101: ResultCode('Generic error. Can happen when formatting a console that has CBHC installed.'),
    102: ResultCode('Error in SLC/MLC or USB.'),
    103: ResultCode('The MLC system memory is corrupted.'),
    104: ResultCode('The SLC system memory is corrupted.'),
    105: ResultCode('The USB storage is corrupted.'),
})

unknown = Module('unknown/misc.', {
    9999: ResultCode('Usually indicates an invalid signature, ticket, or corrupted data. Typically happens when running an unsigned program without CFW/signature patches.')
})

# We have some modules partially documented, those that aren't have dummy Modules.
modules = {
    101: fp,
    102: act,
    103: Module('ac (internet connection)'),
    104: Module('boss(spotpass)'),
    105: Module('nim (title installation'),
    106: nex,
    107: eshop_api,
    111: eshop_web,
    112: unknown2,
    115: olv,
    118: Module('pia (peer-to-peer)'),
    124: Module('ec (e-commerce)'),
    126: eshop_unk,
    150: fs,
    151: Module('kpad (wiimote)'),
    155: Module('save'),
    160: syserr,
    165: Module('vpad (gamepad)'),
    166: Module('aoc (dlc)'),
    187: Module('nfp (amiibo'),
    199: unknown
}

# TODO: Add support for levels from hex inputs.
levels = {
    0: 'Success.',
    -1: 'Fatal.',
    -2: 'Usage.',
    -3: 'Status.',
    -7: 'End.'
}

# regex for Wii U result code format "1XX-YYYY"
RE = re.compile(r'1\d{2}\-\d{4}')

CONSOLE_NAME = 'Nintendo Wii U'

# Suggested color to use if displaying information through a Discord bot's embed
COLOR = 0x009AC7

def is_valid(error):
    err_int = None
    if error.startswith('0x'):
        err_int = int(error, 16)
    if err_int:
        module = (err_int & 0x1FF0) >> 4
        return (err_int & 0x80000000) and module >= 100
    return RE.match(error)

def hex2err(error):
    error = int(error)
    level = (error & 0xF) | 0xFFFFFFF8
    mod = (error & 0x1FF0) >> 4
    desc = (error & 0xFFFFE000) >> 13
    code = f'{module:03}-{desc:04}'
    return code

def get(error):
    if error.startswith('0x'):
        error = int(error)
        level = (error & 0xF) | 0xFFFFFFF8
        print(level)
        mod = (error & 0x1FF0) >> 4
        desc = (error & 0xFFFFE000) >> 13
    else:
        level = None
        mod = int(error[0:3])
        desc = int(error[4:])
    if mod in modules:
        if not modules[mod].data:
            return CONSOLE_NAME, modules[mod].name, NO_RESULTS_FOUND, COLOR
        ret = modules[mod].get_error(desc)
        ret.code = desc
        ret.level = modules[mod].get_level(desc)
        return CONSOLE_NAME, modules[mod].name, ret, COLOR

    return CONSOLE_NAME, None, UNKNOWN_MODULE, COLOR

