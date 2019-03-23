channel_names = {
    # TODO: add more channel names
    # staff channel
    'staff': 'mods',
    # helpers channel
    'helpers': 'helpers',
    # moderator logs
    'moderator-logs': 'mod-logs',
    # server logs
    'server-logs': 'server-logs',
    # watch logs
    'user-watch-logs': 'watch-logs',
    # upload logs
    'user-upload-logs': 'upload-logs',
    # mod mail, only used for private_channels
    'mod-mail': 'mod-mail',
}

channel_alias_names = {y: x for x, y in channel_names.items()}

# alias name
startup_message_channel = 'helpers'

# real names
assistance_channels = {'3ds-assistance-1', '3ds-assistance-2', 'wiiu-assistance', 'switch-assistance',
                       'legacy-systems'}

# alias names
private_channels = {'staff', 'helpers', 'mod-logs', 'mod-mail'}

role_names = {
    # TODO: add more role names
    # helpers role
    'helpers-role': 'Helpers',
    # general staff role
    'staff-role': 'Staff',
    # staff levels
    'halfop-role': 'HalfOP',
    'op-role': 'OP',
    'superop-role': 'SuperOP',
    'owner-role': 'Owner',
}

staff_roles = {
    'halfop': 'halfop-role',
    'op': 'op-role',
    'superop': 'superop-role',
    'owner': 'owner-role',
}


