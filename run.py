#!/usr/bin/env python3

# Kurisu by 916253 & ihaveamac
# license: Apache License 2.0
# https://github.com/916253/Kurisu

# import dependencies
import logging
from asyncio import Event
from configparser import ConfigParser
import sqlite3
from subprocess import check_output, CalledProcessError
import os
from sys import exit, exc_info, hexversion
from traceback import format_exception
import discord
from discord.ext import commands

# sets working directory to bot's folder
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

#Load config
config = ConfigParser()
config.read("config.ini")

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

DATABASE = 'data/kurisu.sqlite'

class Kurisu(commands.Bot):
    """Its him!!."""
    def __init__(self, command_prefix,description, logging_level=logging.WARNING, ):
        super().__init__(command_prefix=command_prefix, description=description)

        self.roles = {
            'Helpers': None,
            'Staff': None,
            'HalfOP': None,
            'OP': None,
            'SuperOP': None,
            'Owner': None,
            'On-Duty 3DS': None,
            'On-Duty Wii U': None,
            'On-Duty Switch': None,
            'Probation': None,
            'Muted': None,
            'No-Help': None,
            'no-elsewhere': None,
            '#elsewhere': None,
            'Small Help': None,
        }

        self.channels = {
            'mods': None,
            'helpers': None,
            'mod-logs': None,
            'server-logs': None,
            'watch-logs': None,
            'upload-logs': None,
            'mod-mail': None,
        }
        self.exitcode = 2
        self._is_all_ready = Event(loop=self.loop)

        self.failed_cogs = []

        os.makedirs("data", exist_ok=True)
        os.makedirs("data/ninupdates", exist_ok=True)
        if not os.path.isfile(DATABASE):
            # read schema, open db, init
            print("Create database")
            with open('schema.sql', 'r', encoding='utf-8') as f:
                schema = f.read()
            self.dbcon = sqlite3.connect(DATABASE)
            self.dbcon.executescript(schema)
            self.dbcon.commit()

            print('%s initialized', DATABASE)
        else:
            # just open db, no setup
            self.dbcon = sqlite3.connect(DATABASE)
            self.c = self.dbcon.cursor()

        print('Kurisu is alive!')

    def load_cogs(self):
        for extension in cogs:
            try:
                self.load_extension(extension)
            except Exception as e:
                print('{} failed to load.\n{}: {}'.format(extension, type(e).__name__, e))
                self.failed_cogs.append([extension, type(e).__name__, e])

    async def on_ready(self):
        guilds = self.guilds
        assert len(guilds) == 1
        self.guild = guilds[0]

        for n in self.channels.keys():
            self.channels[n] = discord.utils.get(self.guild.channels, name=n)
            if not self.channels[n]:
                print(f'Failed to find channel {n}')

        for n in self.roles.keys():
            self.roles[n] = discord.utils.get(self.guild.roles, name=n)
            if not self.roles[n]:
                print(f'Failed to find role {n}')

        startup_message = f'{self.user.name} has started! {self.guild} has {self.guild.member_count:,} members!'
        if len(self.failed_cogs) != 0:
            startup_message += "\n\nSome addons failed to load:\n"
            for f in self.failed_cogs:
                startup_message += "\n{}: `{}: {}`".format(*f)
        await self.channels['helpers'].send(startup_message)
        self._is_all_ready.set()

    async def on_command_error(self, ctx: commands.Context, exc: commands.CommandInvokeError):
        author: discord.Member = ctx.author
        command: commands.Command = ctx.command or '<unknown cmd>'

        if isinstance(exc, commands.CommandNotFound):
            return

        elif isinstance(exc, commands.NoPrivateMessage):
            await ctx.send(f'`{command}` cannot be used in direct messages.')

        elif isinstance(exc, commands.MissingPermissions):
            await ctx.send(f"{author.mention} You don't have permission to use `{command}`.")

        elif isinstance(exc, commands.CheckFailure):
            await ctx.send(f'{author.mention} You cannot use `{command}`.')

        elif isinstance(exc, commands.BadArgument):
            await ctx.send(f'{author.mention} A bad argument was given: `{exc}`\n')
            await ctx.send_help(ctx.command)

        elif isinstance(exc, commands.MissingRequiredArgument):
            await ctx.send('{author.mention} You are missing required arguments.\n')
            await ctx.send_help(ctx.command)

        elif isinstance(exc, commands.CommandInvokeError):
            print('Exception in %s: %s: %s', command, type(exc).__name__, exc)
            await ctx.send(f'{author.mention} `{command}` raised an exception during usage')

        else:
            print('Unexpected exception in %s: %s: %s', command, type(exc).__name__, exc)
            if not isinstance(command, str):
                command.reset_cooldown(ctx)
            await ctx.send(f'{author.mention} Unexpected exception occurred while using the command `{command}`')

    async def on_error(self, event_method, *args, **kwargs):
        print('Exception occurred in %s', event_method)

    async def is_all_ready(self):
        """Checks if the bot is finished setting up."""
        return self._is_all_ready.is_set()

    async def wait_until_all_ready(self):
        """Wait until the bot is finished setting up."""
        await self._is_all_ready.wait()


def main(debug=False):
    """Main script to run the bot."""
    if discord.version_info.major < 1:
        print(f'discord.py is not at least 1.0.0x. (current version: {discord.__version__})')
        return 2

    if not hexversion >= 0x030702F0:  # 3.7.2
        print('Kurisu requires 3.7.2 or later.')
        return 2

    # attempt to get current git information
    try:
        commit = check_output(['git', 'rev-parse', 'HEAD']).decode('ascii')[:-1]
    except CalledProcessError as e:
        print(f'Checking for git commit failed: {type(e).__name__}: {e}')
        commit = "<unknown>"

    try:
        branch = check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode()[:-1]
    except CalledProcessError as e:
        print(f'Checking for git branch failed: {type(e).__name__}: {e}')
        branch = "<unknown>"


    # do not remove a command prefix unless it is demonstrably causing problems
    bot = Kurisu(('.', '!'), logging_level=logging.DEBUG if debug else logging.INFO, description="Kurisu, the bot for Nintendo Homebrew!")
    bot.help_command.pm_help = None
    bot.log.info('Starting Kurisu2 on commit %s on branch %s', commit, branch)
    bot.load_cogs()

    bot.log.debug('Running bot')
    bot.run(config['Main']['token'])
    return bot.exitcode


if __name__ == '__main__':
    main()
