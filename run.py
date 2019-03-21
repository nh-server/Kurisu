#!/usr/bin/env python3

# Kurisu by 916253 & ihaveamac
# license: Apache License 2.0
# https://github.com/916253/Kurisu

# import dependencies
import asyncio
import copy
import configparser
import datetime
import traceback
import json
import os

if os.environ.get('KURISU_TRACEMALLOC', '0') == '1':
    print('Using tracemalloc')
    import tracemalloc
    tracemalloc.start()

import discord
from discord.ext import commands


# sets working directory to bot's folder
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

# read config for token
config = configparser.ConfigParser()
config.read("config.ini")

os.makedirs("data", exist_ok=True)
os.makedirs("data/ninupdates", exist_ok=True)
# create warnsv2.json if it doesn't exist, and convert warns.json if needed
if not os.path.isfile("data/warnsv2.json"):
    if os.path.isfile("data/warns.json"):
        print("Converting warns.json to warnsv2 format")
        with open("data/warns.json", "r") as f:
            warns = json.load(f)
        warnsv2 = {}
        for user_id, info in warns.items():
            warnsv2[user_id] = {"name": info["name"], "warns": []}
            for w_idx in range(len(info["warns"])):
                warnsv2[user_id]["warns"].append(info["warns"][str(w_idx + 1)])
        with open("data/warnsv2.json", "w") as f:
            json.dump(warnsv2, f)
    else:
        with open("data/warnsv2.json", "w") as f:
            f.write("{}")

_filepaths = [
    "restrictions.json",
    "timemutes.json",
    "timenohelp.json",
    "staff.json",
    "helpers.json",
    "timebans.json",
    "softbans.json",
    "watch.json"
]

for fp in _filepaths:
    fp = "data/%s" %(fp)

    if not os.path.isfile(fp):
        with open(fp, "w") as inf:
            json.dump({}, inf)

bot = commands.Bot(command_prefix=['!', '.'], description="Kurisu, the bot for the Nintendo Homebrew Discord server!", pm_help=None)

bot.actions = []  # changes messages in mod-/server-logs
with open("data/watch.json", "r") as f:
    bot.watching = json.load(f)  # post user messages to messaage-logs

# http://stackoverflow.com/questions/3411771/multiple-character-replace-with-python
def escape_name(name):
    name = str(name)
    for c in "\\`*_<>#@:~":
        if c in name:
            name = name.replace(c, "\\" + c)
    return name.replace("@", "@\u200b")  # prevent mentions
bot.escape_name = escape_name

bot.pruning = False  # used to disable leave logs if pruning, maybe.

# mostly taken from https://github.com/Rapptz/discord.py/blob/async/discord/ext/commands/bot.py
@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.errors.CommandNotFound):
        pass  # ...don't need to know if commands don't exist
    if isinstance(error, commands.errors.CheckFailure):
        await bot.send_message(ctx.message.channel, "{} You don't have permission to use this command.".format(ctx.message.author.mention))
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        formatter = commands.formatter.HelpFormatter()
        await bot.send_message(ctx.message.channel, "{} You are missing required arguments.\n{}".format(ctx.message.author.mention, formatter.format_help_for(ctx, ctx.command)[0]))
    elif isinstance(error, commands.errors.CommandOnCooldown):
        try:
            await bot.delete_message(ctx.message)
        except discord.errors.NotFound:
            pass
        message = await bot.send_message(ctx.message.channel, "{} This command was used {:.2f}s ago and is on cooldown. Try again in {:.2f}s.".format(ctx.message.author.mention, error.cooldown.per - error.retry_after, error.retry_after))
        await asyncio.sleep(10)
        await bot.delete_message(message)
    else:
        ctx.command.reset_cooldown(ctx)
        if not hasattr(ctx.command, 'on_error'):
            await bot.send_message(ctx.message.channel, "An error occured while processing the `{}` command.".format(ctx.command.name))
        print('Ignoring exception in command {0.command} in {0.message.channel}'.format(ctx))
        mods_msg = "Exception occured in `{0.command}` in {0.message.channel.mention}".format(ctx)
        # traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        tb = traceback.format_exception(type(error), error, error.__traceback__)
        print(''.join(tb))
        await bot.send_message(bot.boterr_channel, mods_msg + '\n```' + ''.join(tb) + '\n```')

# mostly taken from https://github.com/Rapptz/discord.py/blob/async/discord/client.py
@bot.event
async def on_error(event_method, *args, **kwargs):
    if isinstance(args[0], commands.errors.CommandNotFound):
        # for some reason runs despite the above
        return
    print('Ignoring exception in {}'.format(event_method))
    mods_msg = "Exception occured in {}".format(event_method)
    tb = traceback.format_exc()
    print(''.join(tb))
    mods_msg += '\n```' + ''.join(tb) + '\n```'
    mods_msg += '\nargs: `{}`\n\nkwargs: `{}`'.format(args, kwargs)
    await bot.send_message(bot.boterr_channel, mods_msg)
    print(args)
    print(kwargs)

bot.all_ready = False
bot._is_all_ready = asyncio.Event(loop=bot.loop)
async def wait_until_all_ready():
    """Wait until the entire bot is ready."""
    await bot._is_all_ready.wait()
bot.wait_until_all_ready = wait_until_all_ready

@bot.event
async def on_ready():
    # this bot should only ever be in one server anyway
    for server in bot.servers:
        bot.server = server
        if bot.all_ready:
            break

        print("{} has started! {} has {:,} members!".format(bot.user.name, server.name, server.member_count))

        # channels
        bot.welcome_channel = discord.utils.get(server.channels, name="welcome-and-rules")
        bot.announcements_channel = discord.utils.get(server.channels, name="announcements")
        bot.helpers_channel = discord.utils.get(server.channels, name="helpers")
        bot.offtopic_channel = discord.utils.get(server.channels, name="off-topic")
        bot.meta_channel = discord.utils.get(server.channels, name="meta")
        bot.voiceandmusic_channel = discord.utils.get(server.channels, name="voice-and-music")
        bot.elsewhere_channel = discord.utils.get(server.channels, name="elsewhere")
        bot.mods_channel = discord.utils.get(server.channels, name="mods")
        bot.modlogs_channel = discord.utils.get(server.channels, name="mod-logs")
        bot.modmail_channel = discord.utils.get(server.channels, name="mod-mail")
        bot.serverlogs_channel = discord.utils.get(server.channels, name="server-logs")
        bot.messagelogs_channel = discord.utils.get(server.channels, name="message-logs")
        bot.uploadlogs_channel = discord.utils.get(server.channels, name="upload-logs")
        bot.watchlogs_channel = discord.utils.get(server.channels, name="watch-logs")
        bot.botcmds_channel = discord.utils.get(server.channels, name="bot-cmds")
        bot.boterr_channel = discord.utils.get(server.channels, name="bot-err")
        bot.ass1_channel = discord.utils.get(server.channels, name="3ds-assistance-1")
        bot.ass2_channel = discord.utils.get(server.channels, name="3ds-assistance-2")
        bot.wiiuass_channel = discord.utils.get(server.channels, name="wiiu-assistance")
        bot.swass_channel = discord.utils.get(server.channels, name="switch-assistance")
        bot.hackinggeneral_channel = discord.utils.get(server.channels, name="hacking-general")
        bot.legacysystems_channel = discord.utils.get(server.channels, name="legacy-systems")

        # roles
        bot.staff_role = discord.utils.get(server.roles, name="Staff")
        bot.halfop_role = discord.utils.get(server.roles, name="HalfOP")
        bot.op_role = discord.utils.get(server.roles, name="OP")
        bot.superop_role = discord.utils.get(server.roles, name="SuperOP")
        bot.owner_role = discord.utils.get(server.roles, name="Owner")
        bot.helpers_role = discord.utils.get(server.roles, name="Helpers")
        bot.retired_role = discord.utils.get(server.roles, name="Retired Staff")
        bot.onduty3ds_role = discord.utils.get(server.roles, name="On-Duty 3DS")
        bot.ondutywiiu_role = discord.utils.get(server.roles, name="On-Duty Wii U")
        bot.ondutyswitch_role = discord.utils.get(server.roles, name="On-Duty Switch")
        bot.verified_role = discord.utils.get(server.roles, name="Verified")
        bot.trusted_role = discord.utils.get(server.roles, name="Trusted")
        bot.probation_role = discord.utils.get(server.roles, name="Probation")
        bot.muted_role = discord.utils.get(server.roles, name="Muted")
        bot.nomemes_role = discord.utils.get(server.roles, name="No-Memes")
        bot.nohelp_role = discord.utils.get(server.roles, name="No-Help")
        bot.noembed_role = discord.utils.get(server.roles, name="No-Embed")
        bot.elsewhere_role = discord.utils.get(server.roles, name="#elsewhere")
        bot.noelsewhere_role = discord.utils.get(server.roles, name="no-elsewhere")
        bot.art_role = discord.utils.get(server.roles, name="#art-discussion")
        bot.noart_role = discord.utils.get(server.roles, name="no-art")
        bot.smallhelp_role = discord.utils.get(server.roles, name="Small Help")
        bot.everyone_role = server.default_role

        #assistance channels
        bot.assistance_channels = (bot.ass1_channel, bot.ass2_channel, bot.wiiuass_channel, bot.swass_channel, bot.hackinggeneral_channel, bot.legacysystems_channel)

        # channels to exempt from most checks
        bot.whitelisted_channels = (bot.helpers_channel, bot.modmail_channel, bot.modlogs_channel, bot.mods_channel, bot.watchlogs_channel, bot.announcements_channel)

        bot.staff_ranks = {
            "HalfOP": bot.halfop_role,
            "OP": bot.op_role,
            "SuperOP": bot.superop_role,
            "Owner": bot.owner_role,
        }

        bot.helper_roles = {
            "3DS": bot.onduty3ds_role,
            "WiiU": bot.ondutywiiu_role,
            "Switch": bot.ondutyswitch_role,
        }

        # load timebans
        with open("data/timebans.json", "r") as f:
            timebans = json.load(f)
        bot.timebans = {}
        timebans_i = copy.copy(timebans)
        for user_id, timestamp in timebans_i.items():
            found = False
            for user in await bot.get_bans(server):
                if user.id == user_id:
                    bot.timebans[user_id] = [user, datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"), False]  # last variable is "notified", for <=30 minute notifications
                    found = True
                    break
            if not found:
                timebans.pop(user_id)  # somehow not in the banned list anymore so let's just remove it
        with open("data/timebans.json", "w") as f:
            json.dump(timebans, f)

        # load timemute
        with open("data/timemutes.json", "r") as f:
            timemutes = json.load(f)
        bot.timemutes = {}
        timemutes_i = copy.copy(timemutes)
        for user_id, timestamp in timemutes_i.items():
            bot.timemutes[user_id] = [datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"), False]  # last variable is "notified", for <=10 minute notifications

        # load timenohelp
        with open("data/timenohelp.json", "r") as f:
            timenohelp = json.load(f)
        bot.timenohelp = {}
        timenohelp_i = copy.copy(timenohelp)
        for user_id, timestamp in timenohelp_i.items():
            bot.timenohelp[user_id] = [datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"), False]  # last variable is "notified", for <=10 minute notifications

        bot.all_ready = True
        bot._is_all_ready.set()

        msg = "{} has started! {} has {:,} members!".format(bot.user.name, server.name, server.member_count)
        if len(failed_addons) != 0:
            msg += "\n\nSome addons failed to load:\n"
            for f in failed_addons:
                msg += "\n{}: `{}: {}`".format(*f)
        await bot.send_message(bot.helpers_channel, msg)

        # softban check
        with open("data/softbans.json", "r") as f:
            softbans = json.load(f)
        for member in server.members:
            if member.id in softbans:
                await bot.send_message(member, "This account has not been permitted to participate in {}. The reason is: {}".format(bot.server.name, softbans[member.id]["reason"]))
                bot.actions.append("sbk:" + member.id)
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
    # 'addons.bf',
    'addons.err',
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
    'addons.imgconvert',
    'addons.mod_staff',
    'addons.mod_warn',
    'addons.mod_watch',
    'addons.mod',
    'addons.nxerr',
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
if __name__ == "__main__":
    print('Bot directory: ', dir_path)
    bot.run(config['Main']['token'])
