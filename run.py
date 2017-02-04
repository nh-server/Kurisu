#!/usr/bin/env python3

# Kurisu by 916253 & ihaveamac
# license: Apache License 2.0
# https://github.com/916253/Kurisu

description = """
Kurisu, the bot for the 3DS Hacking Discord!
"""

# import dependencies
import os
from discord.ext import commands
import discord
import datetime, re
import json, asyncio
import copy
import configparser
import traceback
import sys
import os

# sets working directory to bot's folder
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

# read config for token
config = configparser.ConfigParser()
config.read("config.ini")

# create warns.json if it doesn't exist
if not os.path.isfile("warns.json"):
    with open("warns.json", "w") as f:
        f.write("{}")

# create restrictions.json if it doesn't exist
if not os.path.isfile("restrictions.json"):
    with open("restrictions.json", "w") as f:
        f.write("{}")

# create staff.json if it doesn't exist
if not os.path.isfile("staff.json"):
    with open("staff.json", "w") as f:
        f.write("{}")

# create helpers.json if it doesn't exist
if not os.path.isfile("helpers.json"):
    with open("helpers.json", "w") as f:
        f.write("{}")

# create timebans.json if it doesn't exist
if not os.path.isfile("timebans.json"):
    with open("timebans.json", "w") as f:
        f.write("{}")

# create watch.json if it doesn't exist
if not os.path.isfile("watch.json"):
    with open("watch.json", "w") as f:
        f.write("{}")

prefix = ['!', '.']
bot = commands.Bot(command_prefix=prefix, description=description, pm_help=None)

bot.actions = []  # changes messages in mod-/server-logs
with open("watch.json", "r") as f:
    bot.watching = json.load(f)  # post user messages to messaage-logs

# http://stackoverflow.com/questions/3411771/multiple-character-replace-with-python
chars = "\\`*_<>#@:"
def escape_name(name):
    name = str(name)
    for c in chars:
        if c in name:
            name = name.replace(c, "\\" + c)
    return name
bot.escape_name = escape_name

bot.pruning = False  # used to disable leave logs if pruning, maybe.

@bot.event
async def on_ready():
    # this bot should only ever be in one server anyway
    for server in bot.servers:
        print("{} has started! {} has {:,} members!".format(bot.user.name, server.name, server.member_count))
        bot.server = server
        # channels
        bot.welcome_channel = discord.utils.get(server.channels, name="welcome-and-rules")
        bot.announcements_channel = discord.utils.get(server.channels, name="announcements")
        bot.helpers_channel = discord.utils.get(server.channels, name="helpers")
        bot.mods_channel = discord.utils.get(server.channels, name="mods")
        bot.modlogs_channel = discord.utils.get(server.channels, name="mod-logs")
        bot.serverlogs_channel = discord.utils.get(server.channels, name="server-logs")
        bot.messagelogs_channel = discord.utils.get(server.channels, name="message-logs")
        # roles
        bot.staff_role = discord.utils.get(server.roles, name="Staff")
        bot.halfop_role = discord.utils.get(server.roles, name="HalfOP")
        bot.op_role = discord.utils.get(server.roles, name="OP")
        bot.superop_role = discord.utils.get(server.roles, name="SuperOP")
        bot.helpers_role = discord.utils.get(server.roles, name="Helpers")
        bot.onduty_role = discord.utils.get(server.roles, name="On-Duty")
        bot.verified_role = discord.utils.get(server.roles, name="Verified")
        bot.trusted_role = discord.utils.get(server.roles, name="Trusted")
        bot.probation_role = discord.utils.get(server.roles, name="Probation")
        bot.muted_role = discord.utils.get(server.roles, name="Muted")
        bot.nomemes_role = discord.utils.get(server.roles, name="No-Memes")
        bot.nohelp_role = discord.utils.get(server.roles, name="No-Help")
        bot.noembed_role = discord.utils.get(server.roles, name="No-Embed")
        bot.everyone_role = discord.utils.get(server.roles, name="@everyone")
        msg = "{} has started! {} has {:,} members!".format(bot.user.name, server.name, server.member_count)
        if len(failed_addons) != 0:
            msg += "\n\nSome addons failed to load:\n"
            for f in failed_addons:
                msg += "\n{}: `{}: {}`".format(*f)
        await bot.send_message(bot.helpers_channel, msg)
        break

# loads extensions
addons = [
    'addons.assistance',
    'addons.blah',
    'addons.ctrerr',
    'addons.events',
    'addons.extras',
    'addons.friendcode',
    'addons.kickban',
    'addons.load',
    'addons.lockdown',
    'addons.logs',
    'addons.loop',
    'addons.memes',
    'addons.helper_list',
    'addons.mod_staff',
    'addons.mod_warn',
    'addons.mod_watch',
    'addons.mod',
    'addons.ninerr',
    'addons.rules',
    'addons.xkcdparse',
]

failed_addons = []

for extension in addons:
    try:
        bot.load_extension(extension)
    except Exception as e:
        print('{} failed to load.\n{}: {}'.format(extension, type(e).__name__, e))
        failed_addons.append([extension, type(e).__name__, e])

# Execute
print('Bot directory: ', dir_path)
bot.run(config['Main']['token'])
