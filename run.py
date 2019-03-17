#!/usr/bin/env python3

# Kurisu by 916253 & ihaveamac
# license: Apache License 2.0
# https://github.com/916253/Kurisu

# import dependencies
import asyncio
import configparser
import traceback
import sqlite3
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

bot = commands.Bot(command_prefix=['!', '.'], description="Kurisu, the bot for the Nintendo Homebrew Discord Server!")
bot.help_command.dm_help = None
bot.actions = []  # changes messages in mod-/server-logs

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
async def on_command_error(ctx, error):

    if isinstance(error, commands.errors.CommandNotFound):
        return
    if isinstance(error, commands.errors.NoPrivateMessage):
        await ctx.send("This command is not available in DMs")
        return

    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send_help(ctx.command)
        return
    elif isinstance(error, commands.errors.BadArgument):
        await ctx.send(error)
    elif isinstance(error, commands.CommandOnCooldown):
        try:
            await ctx.message.delete()
        except discord.errors.NotFound:
            return
        message = await ctx.send("{} This command was used {:.2f}s ago and is on cooldown. Try again in {:.2f}s.".format(ctx.author.mention, error.cooldown.per - error.retry_after, error.retry_after))
        await asyncio.sleep(10)
        await ctx.message.delete()
    else:
        ctx.command.reset_cooldown(ctx)
        if not hasattr(ctx.command, 'on_error'):
            await ctx.send("An error occured while processing the `{}` command.".format(ctx.command.name))
        print('Ignoring exception in command {0.command} in {0.message.channel}'.format(ctx))
        mods_msg = "Exception occured in `{0.command}` in {0.message.channel.mention}".format(ctx)
        # traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        tb = traceback.format_exception(type(error), error, error.__traceback__)
        print(''.join(tb))
        await bot.boterr_channel.send(mods_msg + '\n```' + ''.join(tb) + '\n```')

# mostly taken from https://github.com/Rapptz/discord.py/blob/async/discord/client.py
@bot.event
async def on_error(event_method, *args, **kwargs):
    if isinstance(args, commands.errors.CommandNotFound):
        # for some reason runs despite the above
        return
    print('Ignoring exception in {}'.format(event_method))
    mods_msg = "Exception occured in {}".format(event_method)
    tb = traceback.format_exc()
    print(''.join(tb))
    mods_msg += '\n```' + ''.join(tb) + '\n```'
    mods_msg += '\nargs: `{}`\n\nkwargs: `{}`'.format(args, kwargs)
    await bot.boterr_channel.send(mods_msg)
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
    # this bot should only ever be in one guild anyway
    for guild in bot.guilds:
        bot.guild = guild
        if bot.all_ready:
            break

        print("{} has started! {} has {:,} members!".format(bot.user.name, guild.name, guild.member_count))

        # channels
        bot.welcome_channel = discord.utils.get(guild.channels, name="welcome-and-rules")
        bot.announcements_channel = discord.utils.get(guild.channels, name="announcements")
        bot.helpers_channel = discord.utils.get(guild.channels, name="helpers")
        bot.offtopic_channel = discord.utils.get(guild.channels, name="off-topic")
        bot.meta_channel = discord.utils.get(guild.channels, name="meta")
        bot.voiceandmusic_channel = discord.utils.get(guild.channels, name="voice-and-music")
        bot.elsewhere_channel = discord.utils.get(guild.channels, name="elsewhere")
        bot.mods_channel = discord.utils.get(guild.channels, name="mods")
        bot.modlogs_channel = discord.utils.get(guild.channels, name="mod-logs")
        bot.modmail_channel = discord.utils.get(guild.channels, name="mod-mail")
        bot.serverlogs_channel = discord.utils.get(guild.channels, name="server-logs")
        bot.messagelogs_channel = discord.utils.get(guild.channels, name="message-logs")
        bot.uploadlogs_channel = discord.utils.get(guild.channels, name="upload-logs")
        bot.watchlogs_channel = discord.utils.get(guild.channels, name="watch-logs")
        bot.botcmds_channel = discord.utils.get(guild.channels, name="bot-cmds")
        bot.boterr_channel = discord.utils.get(guild.channels, name="bot-err")
        bot.ass1_channel = discord.utils.get(guild.channels, name="3ds-assistance-1")
        bot.ass2_channel = discord.utils.get(guild.channels, name="3ds-assistance-2")
        bot.wiiuass_channel = discord.utils.get(guild.channels, name="wiiu-assistance")
        bot.swass_channel = discord.utils.get(guild.channels, name="switch-assistance")
        bot.hackinggeneral_channel = discord.utils.get(guild.channels, name="hacking-general")
        bot.legacysystems_channel = discord.utils.get(guild.channels, name="legacy-systems")

        # roles
        bot.staff_role = discord.utils.get(guild.roles, name="Staff")
        bot.halfop_role = discord.utils.get(guild.roles, name="HalfOP")
        bot.op_role = discord.utils.get(guild.roles, name="OP")
        bot.superop_role = discord.utils.get(guild.roles, name="SuperOP")
        bot.owner_role = discord.utils.get(guild.roles, name="Owner")
        bot.helpers_role = discord.utils.get(guild.roles, name="Helpers")
        bot.retired_role = discord.utils.get(guild.roles, name="Retired Staff")
        bot.onduty3ds_role = discord.utils.get(guild.roles, name="On-Duty 3DS")
        bot.ondutywiiu_role = discord.utils.get(guild.roles, name="On-Duty Wii U")
        bot.ondutyswitch_role = discord.utils.get(guild.roles, name="On-Duty Switch")
        bot.verified_role = discord.utils.get(guild.roles, name="Verified")
        bot.trusted_role = discord.utils.get(guild.roles, name="Trusted")
        bot.probation_role = discord.utils.get(guild.roles, name="Probation")
        bot.muted_role = discord.utils.get(guild.roles, name="Muted")
        bot.nomemes_role = discord.utils.get(guild.roles, name="No-Memes")
        bot.nohelp_role = discord.utils.get(guild.roles, name="No-Help")
        bot.noembed_role = discord.utils.get(guild.roles, name="No-Embed")
        bot.elsewhere_role = discord.utils.get(guild.roles, name="#elsewhere")
        bot.noelsewhere_role = discord.utils.get(guild.roles, name="no-elsewhere")
        bot.smallhelp_role = discord.utils.get(guild.roles, name="Small Help")
        bot.everyone_role = guild.default_role

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


        print('Loading kurisu.sqlite')
        bot.conn = sqlite3.connect('data/kurisu.sqlite')
        bot.c = bot.conn.cursor()

        bot.all_ready = True
        bot._is_all_ready.set()

        msg = "{} has started! {} has {:,} members!".format(bot.user.name, guild.name, guild.member_count)
        if len(failed_cogs) != 0:
            msg += "\n\nSome cogs failed to load:\n"
            for f in failed_cogs:
                msg += "\n{}: `{}: {}`".format(*f)
        await bot.helpers_channel.send(msg)

        # softban check
        softbans = bot.c.execute('SELECT * FROM softbans').fetchall()
        for member in guild.members:
            for softban in softbans:
                if member.id == softban[0]:
                    await member.send("This account has not been permitted to participate in {}. The reason is: {}".format(bot.guild.name, softban[3]))
                    bot.actions.append("sbk:" + str(member.id))
                    try:
                        await member.kick()
                    except discord.errors.Forbidden:
                        pass
                    msg = "🚨 **Attempted join**: {} is soft-banned by <@{}> | {}#{}".format(member.mention, softban[2], bot.escape_name(member.name), member.discriminator)
                    embed = discord.Embed(color=discord.Color.red())
                    embed.description = softban[3]
                    await bot.serverlogs_channel.send(msg, embed=embed)
                    return

# loads extensions
cogs = [
    'cogs.assistance',
    'cogs.blah',
    'cogs.err',
    'cogs.events',
    'cogs.extras',
    'cogs.friendcode',
    'cogs.kickban',
    'cogs.load',
    'cogs.lockdown',
    'cogs.logs',
    'cogs.loop',
    'cogs.memes',
    'cogs.helperlist',
    'cogs.imgconvert',
    'cogs.mod_staff',
    'cogs.mod_warn',
    'cogs.mod_watch',
    'cogs.mod',
    'cogs.nxerr',
    'cogs.rules',
]

failed_cogs = []

for extension in cogs:
    try:
        bot.load_extension(extension)
    except Exception as e:
        print('{} failed to load.\n{}: {}'.format(extension, type(e).__name__, e))
        failed_cogs.append([extension, type(e).__name__, e])

# Execute
if __name__ == "__main__":
    print('Bot directory: ', dir_path)
    bot.run(config['Main']['token'])
