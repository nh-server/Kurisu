#!/usr/bin/env python3

# Kurisu by 916253 & ihaveamac
# license: Apache License 2.0
# https://github.com/nh-server/Kurisu

from asyncio import Event
from configparser import ConfigParser
from subprocess import check_output, CalledProcessError
import os
from cogs.database import ConnectionHolder
from sys import exit, hexversion
from traceback import format_exception, format_exc
import discord
from discord.ext import commands
from datetime import datetime
from cogs.checks import check_staff_id

# sets working directory to bot's folder
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

# Load config
config = ConfigParser()
config.read("config.ini")

database_name = 'data/kurisu.sqlite'

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
    'cogs.ssnc',
    'cogs.xkcdparse',
]


class Kurisu(commands.Bot):
    """Its him!!."""
    def __init__(self, command_prefix, description):
        super().__init__(command_prefix=command_prefix, description=description)

        self.startup = datetime.now()

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
            'On-Duty Legacy': None,
            'Probation': None,
            'Retired Staff': None,
            'Verified': None,
            'Trusted' : None,
            'Muted': None,
            'No-Help': None,
            'no-elsewhere': None,
            'No-Memes': None,
            'no-art': None,
            '#art-discussion': None,
            'No-Embed': None,
            '#elsewhere': None,
            'Small Help': None,
        }

        self.actions = []
        self.pruning = False

        self.channels = {
            'announcements': None,
            'welcome-and-rules': None,
            '3ds-assistance-1': None,
            '3ds-assistance-2': None,
            'wiiu-assistance': None,
            'switch-assistance': None,
            'helpers': None,
            'watch-logs': None,
            'message-logs': None,
            'upload-logs': None,
            'hacking-general': None,
            'meta': None,
            'legacy-systems': None,
            'dev': None,
            'off-topic': None,
            'voice-and-music': None,
            'bot-cmds': None,
            'mods': None,
            'mod-mail': None,
            'mod-logs': None,
            'server-logs': None,
            'bot-err': None,

        }

        self.failed_cogs = []
        self.exitcode = 0
        self._is_all_ready = Event(loop=self.loop)

        os.makedirs("data", exist_ok=True)
        os.makedirs("data/ninupdates", exist_ok=True)

    def load_cogs(self):
        for extension in cogs:
            try:
                self.load_extension(extension)
            except BaseException as e:
                print(f'{extension} failed to load.')
                self.failed_cogs.append([extension, type(e).__name__, e])

    @staticmethod
    def escape_text(text):
        text = str(text)
        return discord.utils.escape_markdown(discord.utils.escape_mentions(text))

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

        self.assistance_channels = {
            self.channels['3ds-assistance-1'],
            self.channels['3ds-assistance-2'],
            self.channels['wiiu-assistance'],
            self.channels['switch-assistance'],
            self.channels['hacking-general'],
            self.channels['legacy-systems'],
        }

        self.staff_roles = {'Owner': self.roles['Owner'],
                            'SuperOP': self.roles['SuperOP'],
                            'OP': self.roles['OP'],
                            'HalfOP': self.roles['HalfOP'],
                            'Staff' : self.roles['Staff'],
                            }

        self.helper_roles = {"3DS": self.roles['On-Duty 3DS'],
                             "WiiU": self.roles['On-Duty Wii U'],
                             "Switch": self.roles['On-Duty Switch'],
                             "Legacy": self.roles['On-Duty Legacy']
                             }

        self.holder = ConnectionHolder()
        await self.holder.load_db(database_name, self.loop)

        startup_message = f'{self.user.name} has started! {self.guild} has {self.guild.member_count:,} members!'
        if len(self.failed_cogs) != 0:
            startup_message += "\n\nSome addons failed to load:\n"
            for f in self.failed_cogs:
                startup_message += "\n{}: `{}: {}`".format(*f)
        print(startup_message)
        await self.channels['helpers'].send(startup_message)
        self._is_all_ready.set()

    async def on_command_error(self, ctx: commands.Context, exc: commands.CommandInvokeError):
        author: discord.Member = ctx.author
        command: commands.Command = ctx.command or '<unknown cmd>'
        exc = getattr(exc, 'original', exc)

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

        elif isinstance(exc, discord.ext.commands.errors.CommandOnCooldown):
            if not await check_staff_id(ctx, 'Helper', author.id):
                try:
                    await ctx.message.delete()
                except (discord.errors.NotFound, discord.errors.Forbidden):
                    pass
                await ctx.send(f"{ctx.message.author.mention} This command was used {exc.cooldown.per - exc.retry_after:.2f}s ago and is on cooldown. Try again in {exc.retry_after:.2f}s.", delete_after=10)
            else:
                await ctx.reinvoke()

        elif isinstance(exc, commands.MissingRequiredArgument):
            await ctx.send(f'{author.mention} You are missing required argument {exc.param.name}.\n')
            await ctx.send_help(ctx.command)

        elif isinstance(exc, discord.NotFound):
            await ctx.send(f"ID not found.")

        elif isinstance(exc, discord.Forbidden):
            await ctx.send(f"💢 I can't help you if you don't let me!\n`{exc.text}`.")

        elif isinstance(exc, commands.CommandInvokeError):
            await ctx.send(f'{author.mention} `{command}` raised an exception during usage')
            msg = "".join(format_exception(type(exc), exc, exc.__traceback__))
            for chunk in [msg[i:i + 1800] for i in range(0, len(msg), 1800)]:
                await self.channels['bot-err'].send(f'```\n{chunk}\n```')
        else:
            if not isinstance(command, str):
                command.reset_cooldown(ctx)
            await ctx.send(f'{author.mention} Unexpected exception occurred while using the command `{command}`')
            msg = "".join(format_exception(type(exc), exc, exc.__traceback__))
            for chunk in [msg[i:i + 1800] for i in range(0, len(msg), 1800)]:
                await self.channels['bot-err'].send(f'```\n{chunk}\n```')

    async def on_error(self, event_method, *args, **kwargs):
        await self.channels['bot-err'].send(f'Error in {event_method}:')
        msg = format_exc()
        for chunk in [msg[i:i + 1800] for i in range(0, len(msg), 1800)]:
            await self.channels['bot-err'].send(f'```\n{chunk}\n```')

    def add_cog(self, cog):
        super().add_cog(cog)

    async def close(self):
        print('Kurisu is shutting down')
        self.holder.dbcon.close()
        self.db_closed = True
        await super().close()

    async def is_all_ready(self):
        """Checks if the bot is finished setting up."""
        return self._is_all_ready.is_set()

    async def wait_until_all_ready(self):
        """Wait until the bot is finished setting up."""
        await self._is_all_ready.wait()


def main():
    """Main script to run the bot."""
    if discord.version_info.major < 1:
        print(f'discord.py is not at least 1.0.0x. (current version: {discord.__version__})')
        return 2

    if not hexversion >= 0x030701F0:  # 3.7.1
        print('Kurisu requires 3.7.1 or later.')
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

    bot = Kurisu(('.', '!'), description="Kurisu, the bot for Nintendo Homebrew!")
    bot.help_command = commands.DefaultHelpCommand(dm_help = None)
    print(f'Starting Kurisu on commit {commit} on branch {branch}', commit, branch)
    bot.load_cogs()
    bot.run(config['Main']['token'])

    return bot.exitcode


if __name__ == '__main__':
    exit(main())
