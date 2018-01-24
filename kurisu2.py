#!/usr/bin/env python3

import asyncio
import logging
import os
import subprocess
import sys
from configparser import ConfigParser
from sys import argv

import discord
from discord.ext import commands


class Kurisu2(commands.Bot):
    """Base class for Kurisu2."""

    def __init__(self, command_prefix, config_directory, logging_level=logging.WARNING, **options):
        from kurisumodules.util import restrictions, configuration

        super().__init__(command_prefix, **options)
        self._guild = None
        self._channels = None
        self._roles = {}
        self._channels = {}
        self.config_directory = config_directory
        self._failed_extensions = {}

        self.exitcode = 0

        os.makedirs(self.config_directory, exist_ok=True)

        self._is_all_ready = asyncio.Event(loop=self.loop)

        self.log = logging.getLogger('Kurisu2')
        self.log.setLevel(logging_level)

        ch = logging.StreamHandler()
        self.log.addHandler(ch)

        fh = logging.FileHandler('kurisu2.log')
        self.log.addHandler(fh)

        fmt = logging.Formatter('%(asctime)s - %(name)s - %(module)s - %(levelname)s - %(message)s')
        ch.setFormatter(fmt)
        fh.setFormatter(fmt)

        self.restrictions = restrictions.RestrictionsManager(self, 'restrictions.sqlite3')
        self.configuration = configuration.ConfigurationManager(self, 'configuration.sqlite3')

    def load_extensions(self):
        blacklisted_cogs = ()
        # this is not a good way of doing things i think
        for c in ['kurisumodules.' + x[:-3] for x in os.listdir('kurisumodules') if x.endswith('.py')]:
            if c in blacklisted_cogs:
                self.log.info('Not automatically loading %s since it is listed in blacklisted_cogs', c)
                continue
            self.log.debug('Loading extension %s', c)
            try:
                self.load_extension(c)
            except Exception as e:
                self.log.error('%s failed to load.', c, exc_info=e)
                self._failed_extensions[c] = e

    async def on_ready(self):
        self.log.debug(f'Logged in as {self.user}')
        guilds = self.guilds
        assert len(guilds) == 1
        self._guild = guilds[0]

    async def get_main_guild(self) -> discord.Guild:
        if not self._is_all_ready:
            await self.wait_until_all_ready()
        return self._guild

    async def on_command_error(self, ctx: commands.Context, exc: commands.CommandInvokeError):
        author: discord.Member = ctx.author
        command: commands.Command = ctx.command or '<unknown cmd>'

        try:
            original = exc.original
        except AttributeError:
            # just in case it's not CommandInvokeError for whatever reason
            original = exc

        if isinstance(exc, commands.CommandNotFound):
            return

        elif isinstance(exc, commands.NoPrivateMessage):
            await ctx.send(f'`{command.name}` cannot be used in direct messages.')

        elif isinstance(exc, commands.MissingPermissions):
            await ctx.send(f"{author.mention} You don't have permission to use `{command}`.")

        elif isinstance(exc, commands.CheckFailure):
            await ctx.send(f'{author.mention} You cannot use `{command}`.')

        elif isinstance(exc, commands.BadArgument):
            formatter = commands.HelpFormatter()
            help_text: str = (await formatter.format_help_for(ctx, command))[0]
            await ctx.send(f'{author.mention} A bad argument was given: `{exc}`\n{help_text}')

        elif isinstance(exc, commands.MissingRequiredArgument):
            formatter = commands.HelpFormatter()
            help_text: str = (await formatter.format_help_for(ctx, command))[0]
            await ctx.send(f'{author.mention} You are missing required arguments.\n{help_text}')

        elif isinstance(exc, commands.CommandInvokeError):
            self.log.debug('Exception in %s: %s: %s', command, type(exc).__name__, exc, exc_info=original)
            await ctx.send(f'{author.mention} `{command}` raised an exception during usage')

        else:
            self.log.debug('Unexpected exception in %s: %s: %s', command, type(exc).__name__, exc, exc_info=original)
            if not isinstance(command, str):
                command.reset_cooldown(ctx)
            await ctx.send(f'{author.mention} Unexpected exception occurred while using the command `{command}`')

    async def on_error(self, event_method, *args, **kwargs):
        self.log.error('Exception occurred in %s', event_method, exc_info=sys.exc_info())

    async def close(self):
        self.log.info('Kurisu is shutting down')
        self.restrictions.close()
        await super().close()

    async def is_all_ready(self):
        """Checks if the bot is finished setting up."""
        return self._is_all_ready.is_set()

    async def wait_until_all_ready(self):
        """Wait until the bot is finished setting up."""
        await self._is_all_ready.wait()


def main(*, config_directory='configs', debug=False, change_directory=False):
    """Main script to run the bot."""
    if discord.version_info.major < 2:
        print(f'discord.py is not at least 1.0.0x. (current version: {discord.__version__})')
        return 2

    if change_directory:
        # set current directory to the bot location
        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)

    bot = Kurisu2(('.', '!'), config_directory, logging_level=logging.DEBUG if debug else logging.INFO,
                  description="Kurisu2, the bot for Nintendo Homebrew!", pm_help=None)

    # attempt to get current git information
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii')[:-1]
    except subprocess.CalledProcessError as e:
        bot.log.info('Checking for git commit failed: %s: %s', type(e).__name__, e)
        commit = "<unknown>"

    try:
        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode()[:-1]
    except subprocess.CalledProcessError as e:
        bot.log.info('Checking for git branch failed: %s: %s', type(e).__name__, e)
        branch = "<unknown>"

    bot.log.info('Starting Kurisu2 on commit %s on branch %s', commit, branch)

    config = ConfigParser()
    config.read('config.ini')
    token: str = config['Main']['token']

    bot.load_extensions()

    bot.log.debug('Running bot')
    # noinspection PyBroadException
    try:
        bot.run(token)
    except Exception as e:
        # this should ideally never happen
        bot.log.critical('Kurisu2 shut down due to a critical error.', exc_info=e)

    bot.log.debug('Shutting down logging')

    return bot.exitcode


if __name__ == '__main__':
    sys.exit(main(debug='d' in argv, change_directory=True))
