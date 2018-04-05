SYSTEM_BANNED = 'System is banned by Nintendo. You cannot ask how to fix this issue here.'

ctrwup = {
    # Nintendo 3DS
    '001-0502': 'Some sort of network error related to friend presence. "Allow Friends to see your online status" '
                'might fix this.',
    '001-0803': 'Could not communicate with authentication server.',
    '002-0102': SYSTEM_BANNED,
    '002-0119': 'System update required (outdated friends-module)',
    '002-0120': 'Title update required (outdated title version)',
    '002-0121': 'Local friend code SEED has invalid signature.\n'
                '\n'
                'This should not happen unless it is modified. The only use case for modifying this file is for '
                'system unbanning, so you cannot ask how to fix this issue here.',
    '003-1099': 'Access point could not be found with the given SSID.',
    '003-2001': 'DNS error. If using a custom DNS server, make sure the settings are correct.',
    '005-4800': 'HTTP Status 500 (Internal Error), unknown cause(?). eShop servers might have issues.',
    '005-5602': 'Unable to connect to the eShop. This error is most likely the result of an incorrect region '
                'setting.\n'
                'Make sure your region is correctly set in System Settings. If you encounter this error after '
                'region-changing your system, make sure you followed all the steps properly.',
    '005-5964': 'Your Nintendo Network ID has been banned from accessing the eShop.\n'
                'If you think this was unwarranted, you will have to contact Nintendo Support to have it reversed.',
    '005-7550': 'Replace SD card(?). Occurs on Nintendo eShop.',
    '006-0102': 'Unexpected error. Could probably happen trying to play an out-of-region title online?',
    '006-0332': 'Disconnected from the game server.',
    '006-0502': 'Could not connect to the server.\n'
                '\n'
                '• Check the [network status page](http://support.nintendo.com/networkstatus)\n'
                '• Move closer to your wireless router\n• Verify DNS settings. If "Auto-Obtain" doesn\'t work, try '
                'Google\'s Public DNS (8.8.8.8, 8.8.4.4) and try again.',
    '006-0612': 'Failed to join the session.',
    '007-0200': 'Could not access SD card.',
    '007-2001': 'Usually the result after region-changing the system. New 3DS cannot fix this issue right now.',
    '007-2100': 'The connection to the Nintendo eShop timed out.\n'
                'This may be due to an ongoing server maintenance, check <https://support.nintendo.com/networkstatus> '
                'to make sure the servers are operating normally. You may also encounter this error if you have a '
                'weak internet connection.',
    '007-2404': 'An error occurred while attempting to connect to the Nintendo eShop.\n'
                'Make sure you are running the latest firmware, since this error will appear if you are trying to '
                'access the eShop on older versions.',
    '007-2720': 'SSL error?',
    '007-2916': 'HTTP error, server is probably down. Try again later?',
    '007-2913': 'HTTP error, server is probably down. Try again later?',
    '007-2923': 'The Nintendo Servers are currently down for maintenance. Please try again later.',
    '007-3102': 'Cannot find title on Nintendo eShop. Probably pulled.',
    '007-6054': 'Occurs when ticket database is full (8192 tickets).',
    '009-1000': 'System update required. (friends module?)',
    '009-2916': 'NIM HTTP error, server is probably down. Try again later?',
    '009-2913': 'NIM HTTP error, server is probably down. Try again later?',
    '009-4079': 'Could not access SD card. General purpose error.',
    '009-4998': '"Local content is newer."\n'
                'The actual cause of this error is unknown.',
    '009-6106': '"AM error in NIM."\n'
                'Probably a bad ticket.',
    '009-8401': 'Update data corrupted. Delete and re-install.',
    '011-3021': 'Cannot find title on Nintendo eShop. Probably incorrect region, or never existed.',
    '011-3136': 'Nintendo eShop is currently unavailable. Try again later.',
    '012-1511': 'Certificate warning.',
    '014-0016': 'Both systems have the same movable.sed key. Format the target and try system transfer again.',
    '014-0062': 'Error during System Transfer. Move closer to the wireless router and keep trying.',
    '022-2452': 'Occurs when trying to use Nintendo eShop with UNITINFO patches enabled.',
    '022-2501': "Attempting to use a Nintendo Network ID on one system when it is linked on another. This can be the "
                "result of using System Transfer, then restoring the source system's NAND and attempting to use "
                "services that require a Nintendo Network ID.\n"
                "\n"
                "In a System Transfer, all Nintendo Network ID accounts associated with the system are transferred "
                "over, whether they are currently linked or not.",
    '022-2511': 'System update required (what causes this? noticed while opening Miiverse, probably not friends '
                'module)',
    '022-2613': 'Incorrect e-mail or password when trying to link an existing Nintendo Network ID. Make sure there '
                'are no typos, and the given e-mail is the correct one for the given ID.\n'
                'If you forgot the password, reset it at <https://id.nintendo.net/account/forgotten-password>',
    '022-2631': 'Nintendo Network ID deleted, or not usable on the current system. If you used System Transfer, '
                'the Nintendo Network ID will only work on the target system.',
    '022-2633': 'Nintendo Network ID temporarily locked due to too many incorrect password attempts. Try again later.',
    '022-2634': 'Nintendo Network ID is not correctly linked on the system. This can be a result of formatting the '
                'SysNAND using System Settings to unlink it from the EmuNAND.\n'
                '\n'
                'See [this part on 3DS Hacks Guide]'
                '(https://3ds.hacks.guide/godmode9-usage.html#removing-an-nnid-without-formatting-your-device) on '
                'removing the NNID without formatting.\n'
                '\n'
                'TinyFormat is recommended for unlinking in the future.',
    '022-2812': SYSTEM_BANNED,
    '028-0102': SYSTEM_BANNED,
    '032-1820': 'Browser error that asks whether you want to go on to a potentially dangerous website. Can be '
                'bypassed by touching "yes".',
    '090-0212': 'Game is banned from Pokémon Global Link. This is most likely as a result of using altered or illegal '
                'save data.',
    # Wii U
    # these all mean different things technically and maybe i should list them
    '102-2812': SYSTEM_BANNED,
    '102-2813': SYSTEM_BANNED,
    '102-2814': SYSTEM_BANNED,
    '102-2815': SYSTEM_BANNED,
    '150-1031': 'Disc could not be read. Either the disc is dirty, the lens is dirty, or the disc is unsupported ('
                'i.e. not a Wii or Wii U game).',
    '160-0101': '"Generic error". Can happen when formatting a system with CBHC.',
    '160-0102': 'Error in SLC/MLC or USB.',
    '160-0103': '"The system memory is corrupted (MLC)."',
    '160-0104': '"The system memory is corrupted (SLC)."',
    '160-0105': 'USB storage corrupted?',
    '160-2713': 'USB removed or lost power while the console was powered on.',
    '199-9999': 'Usually occurs when trying to run an unsigned title without signature patches, or something unknown('
                '?) is corrupted.',
}

hac = {
    # Switch
    '2007-1037': ('Could not detect an SD card.', None),
    '2001-0125': ('Executed svcCloseHandle on main-thread handle', None),
    '2002-6063': ('Attempted to read eMMC CID from browser?', None),
    '2005-0003': ('You are unable to download software.',
                  'http://en-americas-support.nintendo.com/app/answers/detail/a_id/22393'),
    '2110-3400': ('??? (temp)', 'http://en-americas-support.nintendo.com/app/answers/detail/a_id/22569/p/897'),
    '2162-0002': ('General userland crash', 'http://en-americas-support.nintendo.com/app/answers/detail/a_id/22596'),
    '2164-0020': ('Error starting software.',
                  'http://en-americas-support.nintendo.com/app/answers/detail/a_id/22539/p/897'),
    '2168-0000': ('Illegal opcode.', None),
    '2168-0001': ('Resource/Handle not available.', None),
    '2168-0002': ('Segmentation Fault.', None),
    '2168-0003': ('Memory access must be 4 bytes aligned.', None),
    '2811-5001': ('General connection error.',
                  'http://en-americas-support.nintendo.com/app/answers/detail/a_id/22392/p/897'),
}
