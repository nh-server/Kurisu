#!/usr/bin/env python3

# Kurisu by Nintendo Homebrew, started by 916253 & ihaveamac
# license: Apache License 2.0
# https://github.com/nh-server/Kurisu

from asyncio import Event
from alembic import config, script, command
from alembic.runtime import migration
from configparser import ConfigParser
from datetime import datetime
from discord.ext import commands
from sqlalchemy import engine
from subprocess import check_output, CalledProcessError
from sys import exit, hexversion
from traceback import format_exc

import discord
import os
import sys

from utils import models, crud
from utils.checks import check_staff_id
from utils.manager import WordFilterManager, InviteFilterManager, LevenshteinFilterManager
from utils.models import db
from utils.utils import create_error_embed, paginate_message

IS_DOCKER = os.environ.get('IS_DOCKER', '')

# sets working directory to bot's folder
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

# Load config
if IS_DOCKER:
    def get_env(name: str):
        contents = os.environ.get(name)
        if contents is None:
            contents_file = os.environ.get(name + '_FILE')
            try:
                with open(contents_file, 'r', encoding='utf-8') as f:
                    contents = f.readline().strip()
            except FileNotFoundError:
                sys.exit(f"Couldn't find environment variables {name} or {name}_FILE.")

        return contents

    TOKEN = get_env('KURISU_TOKEN')
    db_user = get_env('DB_USER')
    db_password = get_env('DB_PASSWORD')
    DATABASE_URL = f"postgresql://{db_user}:{db_password}@db/{db_user}"
else:
    kurisu_config = ConfigParser()
    kurisu_config.read("data/config.ini")
    TOKEN = kurisu_config['Main']['token']
    DATABASE_URL = kurisu_config['Main']['database_url']

# loads extensions
cogs = [
    'cogs.assistance',
    'cogs.blah',
    'cogs.events',
    'cogs.extras',
    'cogs.filters',
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
    'cogs.results',
    'cogs.rules',
    'cogs.ssnc',
    'cogs.xkcdparse',
    'cogs.seasonal',
    'cogs.newcomers',
]


class CustomContext(commands.Context):
    async def get_user(self, userid: int):
        if self.guild and (user := self.guild.get_member(userid)):
            return user
        else:
            return await self.bot.fetch_user(userid)


class Kurisu(commands.Bot):
    """Its him!!."""

    def __init__(self, *args, commit, branch, **kwargs):
        super().__init__(*args, **kwargs)
        self.startup = datetime.now()

        self.IS_DOCKER = IS_DOCKER
        self.commit = commit
        self.branch = branch

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
            'Trusted': None,
            'Muted': None,
            'No-Help': None,
            'No-elsewhere': None,
            'No-Memes': None,
            'No-art': None,
            '#art-discussion': None,
            'No-Embed': None,
            '#elsewhere': None,
            'Small Help': None,
            'meta-mute': None,
            'crc': None,
            'No-Tech': None,
            'help-mute': None,
            'streamer(temp)': None,
            '🍰': None,
        }

        self.actions = []
        self.pruning = False

        self.channels = {
            'announcements': None,
            'welcome-and-rules': None,
            '3ds-assistance-1': None,
            '3ds-assistance-2': None,
            'wiiu-assistance': None,
            'switch-assistance-1': None,
            'switch-assistance-2': None,
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
            'bot-talk': None,
            'mods': None,
            'mod-mail': None,
            'mod-logs': None,
            'server-logs': None,
            'bot-err': None,
            'elsewhere': None,  # I'm a bit worried about how often this changes, shouldn't be a problem tho
            'newcomers': None,
            'nintendo-discussion': None,
            'tech-talk': None,
            'hardware': None,
        }

        self.failed_cogs = []
        self.exitcode = 0
        self._is_all_ready = Event()

        os.makedirs("data", exist_ok=True)

    async def get_context(self, message, *, cls=CustomContext):
        return await super().get_context(message, cls=cls)

    def upgrade_database_revision(self):
        connection = engine.create_engine(DATABASE_URL)
        alembic_cfg = config.Config('./alembic.ini', stdout=None)
        directory = script.ScriptDirectory.from_config(alembic_cfg)
        with connection.begin() as connection:
            context = migration.MigrationContext.configure(connection)
            if set(context.get_current_heads()) != set(directory.get_heads()):
                print('Upgrading database revision')
                command.upgrade(alembic_cfg, 'head')

    def load_cogs(self):
        for extension in cogs:
            try:
                self.load_extension(extension)
            except BaseException as e:
                print(f'{extension} failed to load.')
                self.failed_cogs.append([extension, type(e).__name__, e])

    async def load_channels(self):
        for n in self.channels:
            if channel := await models.Channel.query.where(models.Channel.name == n).gino.scalar():
                self.channels[n] = self.guild.get_channel(channel)
            else:
                self.channels[n] = discord.utils.get(self.guild.text_channels, name=n)
                if not self.channels[n]:
                    print(f"Failed to find channel {n}")
                    continue
                if db_chan := await crud.get_dbchannel(self.channels[n].id):
                    await db_chan.update(name=n).apply()
                else:
                    await models.Channel.create(id=self.channels[n].id, name=self.channels[n].name)

    async def load_roles(self):
        for n in self.roles:
            if role := await models.Role.query.where(models.Role.name == n).gino.scalar():
                self.roles[n] = self.guild.get_role(role)
            else:
                self.roles[n] = discord.utils.get(self.guild.roles, name=n)
                if not self.roles[n]:
                    print(f"Failed to find role {n}")
                    continue
                if db_role := await crud.get_dbrole(self.roles[n].id):
                    await db_role.update(name=n).apply()
                else:
                    await models.Role.create(id=self.roles[n].id, name=self.roles[n].name)
        # Nitro Booster existence depends if there is any nitro booster
        self.roles['Nitro Booster'] = self.guild.premium_subscriber_role
        if self.roles['Nitro Booster'] and not await crud.get_dbrole(self.roles['Nitro Booster'].id):
            await models.Role.create(id=self.roles['Nitro Booster'].id, name='Nitro Booster')

    @staticmethod
    def escape_text(text):
        text = str(text)
        return discord.utils.escape_markdown(text)

    async def on_ready(self):
        guilds = self.guilds
        assert len(guilds) == 1
        self.guild = guilds[0]

        try:
            self.upgrade_database_revision()
            await db.set_bind(DATABASE_URL)
        except:
            sys.exit('Error when connecting to database')

        await self.load_channels()
        await self.load_roles()

        self.assistance_channels = {
            self.channels['3ds-assistance-1'],
            self.channels['3ds-assistance-2'],
            self.channels['wiiu-assistance'],
            self.channels['switch-assistance-1'],
            self.channels['switch-assistance-2'],
            self.channels['hacking-general'],
            self.channels['legacy-systems'],
            self.channels['tech-talk'],
            self.channels['hardware'],
        }

        self.staff_roles = {'Owner': self.roles['Owner'],
                            'SuperOP': self.roles['SuperOP'],
                            'OP': self.roles['OP'],
                            'HalfOP': self.roles['HalfOP'],
                            'Staff': self.roles['Staff'],
                            }

        self.helper_roles = {"3DS": self.roles['On-Duty 3DS'],
                             "WiiU": self.roles['On-Duty Wii U'],
                             "Switch": self.roles['On-Duty Switch'],
                             "Legacy": self.roles['On-Duty Legacy']
                             }

        self.wordfilter = WordFilterManager()
        await self.wordfilter.load()

        self.levenshteinfilter = LevenshteinFilterManager()
        await self.levenshteinfilter.load()

        self.invitefilter = InviteFilterManager()
        await self.invitefilter.load()

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
        channel = self.channels['bot-err'] if self.channels['bot-err'] else ctx.channel

        if isinstance(exc, commands.CommandNotFound):
            return

        elif isinstance(exc, commands.ArgumentParsingError):
            await ctx.send_help(ctx.command)

        elif isinstance(exc, commands.NoPrivateMessage):
            await ctx.send(f'`{command}` cannot be used in direct messages.')

        elif isinstance(exc, commands.MissingPermissions):
            await ctx.send(f"{author.mention} You don't have permission to use `{command}`.")

        elif isinstance(exc, commands.CheckFailure):
            await ctx.send(f'{author.mention} You cannot use `{command}`.')

        elif isinstance(exc, commands.BadArgument):
            await ctx.send(f'{author.mention} A bad argument was given: `{exc}`\n')
            await ctx.send_help(ctx.command)

        elif isinstance(exc, commands.BadUnionArgument):
            await ctx.send(f'{author.mention} A bad argument was given: `{exc}`\n')

        elif isinstance(exc, discord.ext.commands.errors.CommandOnCooldown):
            if not await check_staff_id('Helper', author.id):
                try:
                    await ctx.message.delete()
                except (discord.errors.NotFound, discord.errors.Forbidden):
                    pass
                await ctx.send(f"{author.mention} This command was used {exc.cooldown.per - exc.retry_after:.2f}s ago and is on cooldown. Try again in {exc.retry_after:.2f}s.", delete_after=10)
            else:
                await ctx.reinvoke()

        elif isinstance(exc, commands.MissingRequiredArgument):
            await ctx.send(f'{author.mention} You are missing required argument {exc.param.name}.\n')
            await ctx.send_help(ctx.command)

        elif isinstance(exc, discord.NotFound):
            await ctx.send("ID not found.")

        elif isinstance(exc, discord.Forbidden):
            await ctx.send(f"💢 I can't help you if you don't let me!\n`{exc.text}`.")

        elif isinstance(exc, commands.CommandInvokeError):
            await ctx.send(f'{author.mention} `{command}` raised an exception during usage')
            embed = create_error_embed(ctx, exc)
            await channel.send(embed=embed)
        else:
            await ctx.send(f'{author.mention} Unexpected exception occurred while using the command `{command}`')
            embed = create_error_embed(ctx, exc)
            await channel.send(embed=embed)

    async def on_error(self, event_method, *args, **kwargs):
        await self.channels['bot-err'].send(f'Error in {event_method}:')
        msg = format_exc()
        error_paginator = paginate_message(msg)
        for page in error_paginator.pages:
            await self.channels['bot-err'].send(page)

    def add_cog(self, cog):
        super().add_cog(cog)
        print(f'Cog "{cog.qualified_name}" loaded')

    async def close(self):
        print('Kurisu is shutting down')
        await db.pop_bind().close()
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

    if not hexversion >= 0x30800f0:  # 3.8
        print('Kurisu requires 3.8 or later.')
        return 2

    if not IS_DOCKER:
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
    else:
        commit = os.environ.get('COMMIT_SHA')
        branch = os.environ.get('COMMIT_BRANCH')

    intents = discord.Intents(guilds=True, members=True, bans=True, messages=True)

    bot = Kurisu(('.', '!'), description="Kurisu, the bot for Nintendo Homebrew!", allowed_mentions=discord.AllowedMentions(everyone=False, roles=False), commit=commit, branch=branch, intents=intents)
    bot.help_command = commands.DefaultHelpCommand(dm_help=None)
    print(f'Starting Kurisu on commit {commit} on branch {branch}')
    bot.load_cogs()
    bot.run(TOKEN)

    return bot.exitcode


if __name__ == '__main__':
    exit(main())
