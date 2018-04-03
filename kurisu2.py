#!/usr/bin/env python3

import logging
import os
from asyncio import Event
from configparser import ConfigParser
from datetime import datetime
from subprocess import check_output, CalledProcessError
from sys import argv
from sys import exit, exc_info, hexversion
from traceback import format_exception
from typing import Dict

import discord
from discord.ext import commands

channel_names = {
    # TODO: add more channel names
    # destination for startup message
    'startup-message': 'helpers',
    # staff channel
    'staff': 'mods',
    # moderator logs
    'moderator-logs': 'mod-logs',
    # server logs
    'server-logs': 'server-logs',
}

private_channels = {'mods', 'helpers'}

role_names = {
    # TODO: add more role names
    # general staff role
    'staff-role': 'Staff',
}


class Kurisu2(commands.Bot):
    """Base class for Kurisu2."""

    _guild: discord.Guild = None

    def __init__(self, command_prefix, config_directory, logging_level=logging.WARNING, **options):
        from kurisumodules.util.database import RestrictionsManager, ConfigurationManager, WarnsManager
        super().__init__(command_prefix, **options)

        self._roles: Dict[str, discord.Role] = {}
        self._channels: Dict[str, discord.TextChannel] = {}
        self._failed_extensions: Dict[str, BaseException] = {}

        self.config_directory = config_directory

        self.exitcode = 0

        os.makedirs(self.config_directory, exist_ok=True)

        self._is_all_ready = Event(loop=self.loop)

        # TODO: actually use logging properly, somehow. if I can figure it out.
        # judging from https://www.python.org/dev/peps/pep-0282/ I shouldn't have to pass around a log object.
        # actually when I tried do use "logging" directly, it interfered with discord.py. so maybe I'll fix this later
        self.log = logging.getLogger('Kurisu2')
        self.log.setLevel(logging_level)

        ch = logging.StreamHandler()
        self.log.addHandler(ch)

        os.makedirs('logs', exist_ok=True)
        fh = logging.FileHandler(f'logs/kurisu2-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log')
        self.log.addHandler(fh)

        fmt = logging.Formatter('%(asctime)s - %(name)s - %(module)s - %(levelname)s - %(message)s')
        ch.setFormatter(fmt)
        fh.setFormatter(fmt)

        self.debug = logging_level is logging.DEBUG

        self.restrictions = RestrictionsManager(self, 'restrictions.sqlite3')
        self.configuration = ConfigurationManager(self, 'configuration.sqlite3')
        self.warns = WarnsManager(self, 'warns.sqlite3')

        self.log.debug('Kurisu2 class initialized')

    def load_extensions(self):
        blacklisted_cogs = ()
        # this is not a good way of doing things i think
        for c in ('kurisumodules.' + x.name[:-3] for x in os.scandir('kurisumodules')
                  if x.name.endswith('.py') and x.name != '__init__.py'):
            if c in blacklisted_cogs:
                self.log.info('Not automatically loading %s since it is listed in blacklisted_cogs', c)
                continue
            self.log.debug('Loading extension %s', c)
            try:
                self.load_extension(c)
            except BaseException as e:
                self.log.error('%s failed to load.', c, exc_info=e)
                self._failed_extensions[c] = e

    async def on_ready(self):
        self.log.debug('Logged in as %s', self.user)
        guilds = self.guilds
        assert len(guilds) == 1
        self._guild = guilds[0]

        # TODO: replace this test code
        for n in {*channel_names.values()}:
            self._channels[n] = discord.utils.get(self._guild.channels, name=n)
            self.log.debug('Result of searching for channel %s: %r', n, self._channels[n])

        startup_message = f'{self.user.name} has started! {self._guild} has {self._guild.member_count:,} members!'
        embed = None
        if self._failed_extensions:
            startup_message += ' <@78465448093417472>'  # mentions ihaveahax (me) if something fails
            embed = discord.Embed(title='Extensions failed to load')
            for c, e in self._failed_extensions.items():
                embed.add_field(name=c, value=f'{type(e).__module__}.{type(e).__qualname__}: {e}')

        await self._channels[channel_names['startup-message']].send(startup_message, embed=embed)

        self._is_all_ready.set()

    async def get_main_guild(self) -> discord.Guild:
        if not self._is_all_ready:
            await self.wait_until_all_ready()
        return self._guild

    async def get_channel_by_name(self, name: str) -> discord.TextChannel:
        if not self._is_all_ready:
            await self.wait_until_all_ready()
        return self._channels[name]

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
            await ctx.send(f'`{command}` cannot be used in direct messages.')

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
            if self.debug:
                await ctx.send(f'```\n{"".join(format_exception(type(exc), exc, exc.__traceback__))}\n```')

        else:
            self.log.debug('Unexpected exception in %s: %s: %s', command, type(exc).__name__, exc, exc_info=original)
            if not isinstance(command, str):
                command.reset_cooldown(ctx)
            await ctx.send(f'{author.mention} Unexpected exception occurred while using the command `{command}`')
            if self.debug:
                await ctx.send(f'```\n{"".join(format_exception(type(exc), exc, exc.__traceback__))}\n```')

    async def on_error(self, event_method, *args, **kwargs):
        self.log.error('Exception occurred in %s', event_method, exc_info=exc_info())

    def add_cog(self, cog):
        super().add_cog(cog)
        self.log.debug('Initialized %s.%s', type(cog).__module__, type(cog).__name__)

    async def close(self):
        self.log.info('Kurisu is shutting down')
        self.restrictions.close()
        self.configuration.close()
        self.warns.close()
        await super().close()

    async def is_all_ready(self):
        """Checks if the bot is finished setting up."""
        return self._is_all_ready.is_set()

    async def wait_until_all_ready(self):
        """Wait until the bot is finished setting up."""
        await self._is_all_ready.wait()


def main(*, config_directory='configs', debug=False, change_directory=False):
    """Main script to run the bot."""
    if discord.version_info.major < 1:
        print(f'discord.py is not at least 1.0.0x. (current version: {discord.__version__})')
        return 2

    if not hexversion >= 0x030605F0:  # 3.6.4
        print('Kurisu2 requires 3.6.5 or later.')
        return 2

    if change_directory:
        # set current directory to the bot location
        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)

    bot = Kurisu2(('.', '!'), config_directory, logging_level=logging.DEBUG if debug else logging.INFO,
                  description="Kurisu2, the bot for Nintendo Homebrew!", pm_help=None)

    # attempt to get current git information
    try:
        commit = check_output(['git', 'rev-parse', 'HEAD']).decode('ascii')[:-1]
    except CalledProcessError as e:
        bot.log.info('Checking for git commit failed: %s: %s', type(e).__name__, e)
        commit = "<unknown>"

    try:
        branch = check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode()[:-1]
    except CalledProcessError as e:
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

    return bot.exitcode


if __name__ == '__main__':
    exit(main(debug='d' in argv, change_directory=True))
