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

os.makedirs("data", exist_ok=True)
# create warns.json if it doesn't exist
if not os.path.isfile("data/warns.json"):
    with open("data/warns.json", "w") as f:
        f.write("{}")

# create restrictions.json if it doesn't exist
if not os.path.isfile("data/restrictions.json"):
    with open("data/restrictions.json", "w") as f:
        f.write("{}")

# create staff.json if it doesn't exist
if not os.path.isfile("data/staff.json"):
    with open("data/staff.json", "w") as f:
        f.write("{}")

# create helpers.json if it doesn't exist
if not os.path.isfile("data/helpers.json"):
    with open("data/helpers.json", "w") as f:
        f.write("{}")

# create timebans.json if it doesn't exist
if not os.path.isfile("data/timebans.json"):
    with open("data/timebans.json", "w") as f:
        f.write("{}")

# create softbans.json if it doesn't exist
if not os.path.isfile("data/softbans.json"):
    with open("data/softbans.json", "w") as f:
        f.write("{}")

# create watch.json if it doesn't exist
if not os.path.isfile("data/watch.json"):
    with open("data/watch.json", "w") as f:
        f.write("{}")

prefix = ['!', '.']
bot = commands.Bot(command_prefix=prefix, description=description, pm_help=None)

bot.actions = []  # changes messages in mod-/server-logs
with open("data/watch.json", "r") as f:
    bot.watching = json.load(f)  # post user messages to messaage-logs

# http://stackoverflow.com/questions/3411771/multiple-character-replace-with-python
chars = "\\`*_<>#@:~"
def escape_name(name):
    name = str(name)
    for c in chars:
        if c in name:
            name = name.replace(c, "\\" + c)
    return name.replace("@", "@\u200b")  # prevent mentions
bot.escape_name = escape_name

bot.pruning = False  # used to disable leave logs if pruning, maybe.

# mostly taken from https://github.com/Rapptz/discord.py/blob/async/discord/ext/commands/bot.py
@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        pass  # ...don't need to know if commands don't exist
    if isinstance(error, discord.ext.commands.errors.CheckFailure):
        await bot.send_message(ctx.message.channel, "{} You don't have permission to use this command.".format(ctx.message.author.mention))
    elif isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        formatter = commands.formatter.HelpFormatter()
        await bot.send_message(ctx.message.channel, "{} You are missing required arguments.\n{}".format(ctx.message.author.mention, formatter.format_help_for(ctx, ctx.command)[0]))
    else:
        await bot.send_message(ctx.message.channel, "An error occured while processing the `{}` command.".format(ctx.command.name))
        print('Ignoring exception in command {}'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

bot.all_ready = False

@bot.event
async def on_ready():
    if bot.all_ready:
        return
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
        bot.owner_role = discord.utils.get(server.roles, name="Owner")
        bot.helpers_role = discord.utils.get(server.roles, name="Helpers")
        bot.onduty3ds_role = discord.utils.get(server.roles, name="On-Duty 3DS")
        bot.ondutywiiu_role = discord.utils.get(server.roles, name="On-Duty Wii U")
        bot.verified_role = discord.utils.get(server.roles, name="Verified")
        bot.trusted_role = discord.utils.get(server.roles, name="Trusted")
        bot.probation_role = discord.utils.get(server.roles, name="Probation")
        bot.muted_role = discord.utils.get(server.roles, name="Muted")
        bot.nomemes_role = discord.utils.get(server.roles, name="No-Memes")
        bot.nohelp_role = discord.utils.get(server.roles, name="No-Help")
        bot.noembed_role = discord.utils.get(server.roles, name="No-Embed")
        bot.elsewhere_role = discord.utils.get(server.roles, name="#elsewhere")
        bot.everyone_role = server.default_role

        bot.staff_ranks = {
            "HalfOP": bot.halfop_role,
            "OP": bot.op_role,
            "SuperOP": bot.superop_role,
            "Owner": bot.owner_role,
        }

        bot.helper_roles = {
            "3DS": bot.onduty3ds_role,
            "WiiU": bot.ondutywiiu_role,
        }

        msg = "{} has started! {} has {:,} members!".format(bot.user.name, server.name, server.member_count)
        if len(failed_addons) != 0:
            msg += "\n\nSome addons failed to load:\n"
            for f in failed_addons:
                msg += "\n{}: `{}: {}`".format(*f)
        await bot.send_message(bot.helpers_channel, msg)
        bot.all_ready = True

        # softban check
        with open("data/softbans.json", "r") as f:
            softbans = json.load(f)
        for member in server.members:
            if member.id in softbans:
                await bot.send_message(member, "This account has not been permitted to participate in {}. The reason is: {}".format(bot.server.name, softbans[member.id]["reason"]))
                bot.actions.append("sbk:"+member.id)
                await bot.kick(member)
                msg = "🚨 **Attempted join**: {} is soft-banned by <@{}> | {}#{}".format(member.mention, softbans[member.id]["issuer_id"], bot.escape_name(member.name), member.discriminator)
                embed = discord.Embed(color=discord.Color.red())
                embed.description = softbans[member.id]["reason"]
                await bot.send_message(bot.serverlogs_channel, msg, embed=embed)
                return
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
