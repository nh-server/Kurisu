#!/usr/bin/env python3

# Kurisu by 916253 & ihaveamac
# license: Apache License 2.0
# https://github.com/916253/Kurisu

description = """
A bot being slowly written to replace Saber as Saber is no longer actively developed.
"""

# import dependencies
from discord.ext import commands
import discord
import datetime, re
import json, asyncio
import copy
import configparser
import logging
import traceback
import sys
import os
from collections import Counter

# read config for token
config = configparser.ConfigParser()
config.read("config.ini")

prefix = ['.']
bot = commands.Bot(command_prefix=prefix, description=description, pm_help=None)

@bot.event
async def on_ready():
    # this bot should only ever be in one server anyway
    for server in bot.servers:
        await bot.send_message(discord.utils.get(server.channels, name="mods"), "{} has started!".format(bot.user.name))
        break

# outputs all messages to a log file
logger = logging.getLogger('discord')
logger.setLevel(logging.ERROR)
handler = logging.FileHandler(filename='numberbot_output.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# loads extensions
addons = [
    'addons.memes',
    'addons.rules',
    'addons.assistance',
    'addons.mod',
    'addons.logs',
    'addons.load',
    'addons.ctrerr',
    'addons.ninerr',
]

for extension in addons:
    try:
        bot.load_extension(extension)
    except Exception as e:
        print('The addon failed to load! {}\n{}: {}'.format(extension, type(e).__name__, e))

# Execute
bot.run(config['Main']['token'])
