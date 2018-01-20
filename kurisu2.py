#!/usr/bin/env python3

import asyncio
import os
import logging
import subprocess
from configparser import ConfigParser
from sys import argv

import discord
from discord.ext import commands


class Kurisu2(commands.Bot):
    """Base class for Kurisu2."""

    def __init__(self, command_prefix, logging_level=logging.WARNING, **options):
        super().__init__(command_prefix, **options)
        self._failed_extensions = []

        self._is_all_ready = asyncio.Event(loop=self.loop)

        self.log = logging.getLogger('Kurisu2')
        self.log.setLevel(logging_level)

        ch = logging.StreamHandler()
        self.log.addHandler(ch)

        fh = logging.FileHandler('kurisu2.log')
        self.log.addHandler(fh)

        fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(fmt)
        fh.setFormatter(fmt)

        # commands.has_any_role("Owner")(self.command()(self.test))

    def _load_extensions(self):
        cogs = ()
        for c in cogs:
            self.log.info("Loading extension %s", c)
            try:
                self.load_extension('kurisumodules.' + c)
            except Exception as e:
                self.log.error("%s failed to load.", c, exc_info=e)

    async def on_command_error(self, ctx: commands.Context, exc: BaseException):
        author: discord.Member = ctx.author
        command: commands.Command = ctx.command
        self.log.debug('Exception in %s: %s: %s', command.name, type(exc).__name__, exc)
        if isinstance(exc, commands.CommandNotFound):
            return
        elif isinstance(exc, commands.NoPrivateMessage):
            await ctx.send(f'`{command.name}` cannot be used in direct messages.')
        elif isinstance(exc, commands.MissingPermissions):
            await ctx.send(f"{author.mention} You don't have permission to use `{command.name}`.")
        elif isinstance(exc, commands.BadArgument):
            formatter = commands.HelpFormatter()
            help_text: str = (await formatter.format_help_for(ctx, command))[0]
            await ctx.send(f'{author.mention} A bad argument was given: `{exc}`\n{help_text}')
        elif isinstance(exc, commands.MissingRequiredArgument):
            formatter = commands.HelpFormatter()
            help_text: str = (await formatter.format_help_for(ctx, command))[0]
            await ctx.send(f'{author.mention} You are missing required arguments.\n{help_text}')

    async def is_all_ready(self):
        """Checks if the bot is finished setting up."""
        return self._is_all_ready.is_set()

    async def wait_until_all_ready(self):
        """Wait until the bot is finished setting up."""
        await self._is_all_ready.wait()

    async def on_ready(self):
        self.log.debug('Bot is setting up')
        # TODO: setup


def main(*, debug=False, change_directory=False):
    """Main script to run the bot."""
    if change_directory:
        # set current directory to the bot location
        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)

    bot = Kurisu2(('.', '!'), logging_level=logging.DEBUG if debug else logging.INFO,
                     description="Kurisu2, the bot for Nintendo Homebrew!", pm_help=None)

    # attempt to get current git information
    # noinspection PyBroadException
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii')[:-1]
    except Exception as e:
        bot.log.info('Checking for git commit failed: %s: %s', type(e).__name__, e)
        commit = "<unknown>"

    bot.log.info('Starting Kurisu2 on commit %s', commit)

    config = ConfigParser()
    config.read('config.ini')
    token: str = config['Main']['token']

    bot._load_extensions()

    bot.run(token)

    bot.log.info('Kurisu2 is shutting down')


if __name__ == '__main__':
    main(debug='d' in argv, change_directory=True)
