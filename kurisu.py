#!/usr/bin/env python3

# Kurisu by Nintendo Homebrew
# license: Apache License 2.0
# https://github.com/nh-server/Kurisu

import aiohttp
import asyncio
import discord
import gino
import logging
import os
import sys
import traceback

from alembic.config import main as albmain
from configparser import ConfigParser
from datetime import datetime
from discord.ext import commands
from logging.handlers import TimedRotatingFileHandler
from subprocess import check_output, CalledProcessError
from typing import Optional
from utils import crud
from utils.checks import check_staff_id
from utils.help import KuriHelp
from utils.manager import InviteFilterManager, WordFilterManager, LevenshteinFilterManager
from utils.models import Channel, Role, db
from utils.utils import create_error_embed

cogs = (
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
    'cogs.server_logs',
)

DEBUG = False
IS_DOCKER = os.environ.get('IS_DOCKER', '')

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
            except IsADirectoryError:
                sys.exit(f"Attempted to open {contents_file} (env {name}_FILE) but it is a folder.")

        return contents

    TOKEN = get_env('KURISU_TOKEN')
    db_user = get_env('DB_USER')
    db_password = get_env('DB_PASSWORD')
    SERVER_LOGS_URL = get_env('SERVER_LOGS_URL')
    DATABASE_URL = f"postgresql://{db_user}:{db_password}@db/{db_user}"
else:
    kurisu_config = ConfigParser()
    kurisu_config.read("data/config.ini")
    TOKEN = kurisu_config['Main']['token']
    DATABASE_URL = kurisu_config['Main']['database_url']
    SERVER_LOGS_URL = kurisu_config['Main']['server_logs_url']


def setup_logging():
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    fh = TimedRotatingFileHandler(filename='data/kurisu.log', when='midnight', encoding='utf-8', backupCount=7)
    fmt = logging.Formatter('[{asctime}] [{levelname:^7s}] {module}.{funcName}: {message}', datefmt="%Y-%m-%d %H:%M:%S",
                            style='{')
    fh.setFormatter(fmt)
    log.addHandler(fh)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    log.addHandler(sh)
    logging.getLogger('disnake').propagate = False
    logging.getLogger('gino').propagate = False


logger = logging.getLogger(__name__)


class Kurisu(commands.Bot):

    def __init__(self, command_prefix, description, commit, branch):

        intents = discord.Intents(guilds=True, members=True, messages=True, reactions=True, bans=True)
        allowed_mentions = discord.AllowedMentions(everyone=False, roles=False)
        super().__init__(
            command_prefix=commands.when_mentioned_or(*command_prefix),
            description=description,
            intents=intents,
            allowed_mentions=allowed_mentions,
            case_insensitive=True,
        )
        self.startup = datetime.now()
        self.IS_DOCKER = IS_DOCKER
        self.commit = commit
        self.branch = branch

        self.roles: dict[str, discord.Role] = {
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
            'appeal-mute': None,
            'crc': None,
            'No-Tech': None,
            'help-mute': None,
            'streamer(temp)': None,
            '🍰': None,
        }

        self.channels: dict[str, discord.TextChannel] = {
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
            'appeals': None,
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
            'elsewhere': None,
            'newcomers': None,
            'nintendo-discussion': None,
            'tech-talk': None,
            'hardware': None,
            'streaming-gamer': None,
        }

        self.failed_cogs = []
        self.channels_not_found = []
        self.roles_not_found = []

        self.wordfilter = WordFilterManager()
        self.levenshteinfilter = LevenshteinFilterManager()
        self.invitefilter = InviteFilterManager()

        self.err_channel: Optional[discord.TextChannel] = None
        self.actions = []
        self.pruning = False
        self.emoji = discord.PartialEmoji.from_str("⁉")
        self.colour = discord.Colour(0xb01ec3)

        self.session = aiohttp.ClientSession(loop=self.loop)

        self._is_all_ready = asyncio.Event()

    async def on_ready(self):
        if self._is_all_ready.is_set():
            return

        self.guild = self.guilds[0]

        self.emoji = discord.utils.get(self.guild.emojis, name='kurisu') or discord.PartialEmoji.from_str("⁉")

        # Load Filters
        await self.wordfilter.load()
        logger.info("Loaded wordfilter")
        await self.levenshteinfilter.load()
        logger.info("Loaded levenshtein filter")
        await self.invitefilter.load()
        logger.info("Loaded invite filter")

        # Load channels and roles
        await self.load_channels()
        await self.load_roles()

        self.helper_roles: dict[str, discord.Role] = {"3DS": self.roles['On-Duty 3DS'],
                                                     "WiiU": self.roles['On-Duty Wii U'],
                                                     "Switch": self.roles['On-Duty Switch'],
                                                     "Legacy": self.roles['On-Duty Legacy']
                                                      }

        self.assistance_channels: tuple[discord.TextChannel, ...] = (
            self.channels['3ds-assistance-1'],
            self.channels['3ds-assistance-2'],
            self.channels['wiiu-assistance'],
            self.channels['switch-assistance-1'],
            self.channels['switch-assistance-2'],
            self.channels['hacking-general'],
            self.channels['legacy-systems'],
            self.channels['tech-talk'],
            self.channels['hardware'],
        )

        self.staff_roles: dict[str, discord.Role] = {'Owner': self.roles['Owner'],
                            'SuperOP': self.roles['SuperOP'],
                            'OP': self.roles['OP'],
                            'HalfOP': self.roles['HalfOP'],
                            'Staff': self.roles['Staff'],
                            }

        self.err_channel = self.channels['bot-err']

        self.load_cogs()

        startup_message = f'{self.user.name} has started! {self.guild} has {self.guild.member_count:,} members!'
        embed = discord.Embed(title=f"{self.user.name} has started!",
                              description=f"{self.guild} has {self.guild.member_count:,} members!", colour=0xb01ec3)
        if self.failed_cogs or self.roles_not_found or self.channels_not_found:
            embed.colour = 0xe50730
            if self.failed_cogs:
                embed.add_field(
                    name="Failed to load cogs:",
                    value='\n'.join(
                        f"**{cog}**\n**{exc_type}**: {exc}\n" for cog, exc_type, exc in self.failed_cogs
                    ),
                    inline=False,
                )
            if self.roles_not_found:
                embed.add_field(name="Roles not Found:", value=', '.join(self.roles_not_found), inline=False)
            if self.channels_not_found:
                embed.add_field(name="Channels not Found:", value=', '.join(self.channels_not_found), inline=False)

        logger.info(startup_message)
        await self.channels['helpers'].send(embed=embed)

        self._is_all_ready.set()

    async def wait_until_all_ready(self):
        """Wait until the bot is finished setting up."""
        await self._is_all_ready.wait()

    @staticmethod
    def escape_text(text):
        text = str(text)
        return discord.utils.escape_markdown(text)

    async def close(self):
        await super().close()
        await db.pop_bind().close()
        await self.session.close()

    def load_cogs(self):
        for extension in cogs:
            try:
                self.load_extension(extension)
            except BaseException as e:
                logger.error("%s failed to load.", extension)
                self.failed_cogs.append((extension, type(e).__name__, e))

    async def load_channels(self):
        for n in self.channels:
            channel_id: Optional[int] = await Channel.query.where(Channel.name == n).gino.scalar()
            if channel_id and (channel := self.guild.get_channel(channel_id)):
                self.channels[n] = channel
            else:
                self.channels[n] = discord.utils.get(self.guild.channels, name=n)
                if not self.channels[n]:
                    self.channels_not_found.append(n)
                    logger.warning("Failed to find channel %s", n)
                    continue
                if db_chan := await crud.get_dbchannel(self.channels[n].id):
                    await db_chan.update(name=n).apply()
                else:
                    await Channel.create(id=self.channels[n].id, name=self.channels[n].name)

    async def load_roles(self):
        for n in self.roles:
            if role := await Role.query.where(Role.name == n).gino.scalar():
                self.roles[n] = self.guild.get_role(role)
            else:
                self.roles[n] = discord.utils.get(self.guild.roles, name=n)
                if not self.roles[n]:
                    self.roles_not_found.append(n)
                    logger.warning("Failed to find role %s", n)
                    continue
                if db_role := await crud.get_dbrole(self.roles[n].id):
                    await db_role.update(name=n).apply()
                else:
                    await Role.create(id=self.roles[n].id, name=self.roles[n].name)
        # Nitro Booster existence depends if there is any nitro booster
        self.roles['Nitro Booster'] = self.guild.premium_subscriber_role
        if self.roles['Nitro Booster'] and not await crud.get_dbrole(self.roles['Nitro Booster'].id):
            await Role.create(id=self.roles['Nitro Booster'].id, name='Nitro Booster')

    async def on_command_error(self, ctx: commands.Context, exc: commands.CommandError):
        author: discord.Member = ctx.author
        command: commands.Command = ctx.command
        exc = getattr(exc, 'original', exc)
        channel = self.err_channel or ctx.channel

        if hasattr(ctx.command, 'on_error'):
            return

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

        elif isinstance(exc, commands.MissingRequiredArgument):
            await ctx.send(f'{author.mention} You are missing required argument `{exc.param.name}`.\n')
            await ctx.send_help(ctx.command)
            command.reset_cooldown(ctx)

        elif isinstance(exc, commands.BadLiteralArgument):
            await ctx.send(f'Argument {exc.param.name} must be one of the following `{"` `".join(str(literal) for literal in exc.literals)}`.')
            command.reset_cooldown(ctx)

        elif isinstance(exc, commands.UserInputError):
            await ctx.send(f'{author.mention} A bad argument was given: `{exc}`\n')
            await ctx.send_help(ctx.command)
            command.reset_cooldown(ctx)

        elif isinstance(exc, discord.ext.commands.errors.CommandOnCooldown):
            if not await check_staff_id('Helper', author.id):
                try:
                    await ctx.message.delete()
                except (discord.errors.NotFound, discord.errors.Forbidden):
                    pass
                await ctx.send(f"{author.mention} This command was used {exc.cooldown.per - exc.retry_after:.2f}s ago and is on cooldown. "
                               f"Try again in {exc.retry_after:.2f}s.", delete_after=10)
            else:
                await ctx.reinvoke()

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

    async def on_slash_command_error(self, inter: discord.CommandInteraction, exc: commands.CommandError):
        author: discord.Member = inter.author
        command: str = inter.application_command.name
        exc = getattr(exc, 'original', exc)
        channel = self.err_channel or inter.channel

        if isinstance(exc, commands.NoPrivateMessage):
            await inter.response.send_message(f'`{command}` cannot be used in direct messages.', ephemeral=True)

        elif isinstance(exc, commands.MissingPermissions):
            await inter.response.send_message(f"{author.mention} You don't have permission to use `{command}`.", ephemeral=True)

        elif isinstance(exc, commands.CheckFailure):
            await inter.response.send_message(f'{author.mention} You cannot use `{command}`.', ephemeral=True)

        elif isinstance(exc, discord.ext.commands.MaxConcurrencyReached):
            await inter.response.send_message(exc, ephemeral=True)
        elif isinstance(exc, discord.ext.commands.errors.CommandOnCooldown):
            await inter.response.send_message(f"{author.mention} This command was used {exc.cooldown.per - exc.retry_after:.2f}s ago and is on cooldown. "
                                              f"Try again in {exc.retry_after:.2f}s.", ephemeral=True)
        else:
            if isinstance(exc, discord.Forbidden):
                msg = f"💢 I can't help you if you don't let me!\n`{exc.text}`."
            elif isinstance(exc, commands.CommandInvokeError):
                msg = f'{author.mention} `{command}` raised an exception during usage'
            else:
                msg = f'{author.mention} Unexpected exception occurred while using the command `{command}`'

            if inter.response.is_done():
                await inter.edit_original_message(content=msg, embed=None, view=None)
            else:
                await inter.response.send_message(msg, ephemeral=True)
            if channel:
                embed = create_error_embed(inter, exc)
                await channel.send(embed=embed)

    async def on_user_command_error(self, inter, exc: commands.CommandError):
        author: discord.Member = inter.author
        command: str = inter.application_command.name
        exc = getattr(exc, 'original', exc)
        channel = self.err_channel or inter.channel

        if isinstance(exc, commands.NoPrivateMessage):
            await inter.response.send_message(f'`{command}` cannot be used in direct messages.', ephemeral=True)

        elif isinstance(exc, commands.MissingPermissions):
            await inter.response.send_message(f"{author.mention} You don't have permission to use `{command}`.", ephemeral=True)

        elif isinstance(exc, commands.CheckFailure):
            await inter.response.send_message(f'{author.mention} You cannot use `{command}`.', ephemeral=True)

        elif isinstance(exc, discord.ext.commands.errors.CommandOnCooldown):
            await inter.response.send_message(f"{author.mention} This command was used {exc.cooldown.per - exc.retry_after:.2f}s ago and is on cooldown. "
                                              f"Try again in {exc.retry_after:.2f}s.", ephemeral=True)
        else:
            if isinstance(exc, discord.Forbidden):
                msg = f"💢 I can't help you if you don't let me!\n`{exc.text}`."
            elif isinstance(exc, commands.CommandInvokeError):
                msg = f'{author.mention} `{command}` raised an exception during usage'
            else:
                msg = f'{author.mention} Unexpected exception occurred while using the command `{command}`'
            if inter.response.is_done():
                await inter.edit_original_message(content=msg, embed=None, view=None)
            else:
                await inter.response.send_message(msg, ephemeral=True)
            if channel:
                embed = create_error_embed(inter, exc)
                await channel.send(embed=embed)

    async def on_error(self, event_method, *args, **kwargs):
        logger.error("", exc_info=True)
        if not self.err_channel:
            return

        exc_type, exc, tb = sys.exc_info()
        embed = discord.Embed(title="Error Event", colour=0xe50730)
        embed.add_field(name="Event Method", value=event_method)
        trace = "".join(traceback.format_exception(exc_type, exc, tb))
        embed.description = f"```py\n{trace}\n```"
        await self.err_channel.send(embed=embed)


async def startup():
    setup_logging()

    if discord.version_info.major < 1:
        logger.error("discord.py is not at least 1.0.0x. (current version: %s)", discord.__version__)
        return 2

    if sys.hexversion < 0x30900F0:  # 3.9
        logger.error("Kurisu requires 3.9 or later.")
        return 2

    if not IS_DOCKER:
        # attempt to get current git information
        try:
            commit = check_output(['git', 'rev-parse', 'HEAD']).decode('ascii')[:-1]
        except CalledProcessError as e:
            logger.error("Checking for git commit failed: %s: %s", type(e).__name__, e)
            commit = "<unknown>"

        try:
            branch = check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode()[:-1]
        except CalledProcessError as e:
            logger.error("Checking for git branch failed: %s: %s", type(e).__name__, e)
            branch = "<unknown>"
    else:
        commit = os.environ.get('COMMIT_SHA')
        branch = os.environ.get('COMMIT_BRANCH')

    try:
        albmain(['--raiseerr', 'upgrade', 'head'])
        engine = await gino.create_engine(DATABASE_URL)
        db.bind = engine
    except Exception:
        logger.exception("Failed to connect to postgreSQL server", exc_info=True)
        return
    logger.info("Starting Kurisu on commit %s on branch %s", commit, branch)
    bot = Kurisu(command_prefix=['.', '!'], description="Kurisu, the bot for Nintendo Homebrew!", commit=commit,
                 branch=branch)
    bot.help_command = KuriHelp()
    bot.engine = engine
    await bot.start(TOKEN)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(startup())
