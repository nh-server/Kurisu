#!/usr/bin/env python3

# Kurisu by Nintendo Homebrew
# license: Apache License 2.0
# https://github.com/nh-server/Kurisu

import aiohttp
import asyncio
import asyncpg
import discord
import logging
import os
import sys
import traceback

from configparser import ConfigParser
from datetime import datetime

import pytz
from discord import app_commands
from discord.ext import commands
from subprocess import check_output, CalledProcessError
from typing import Optional, Union
from utils import WarnsManager, ConfigurationManager, RestrictionsManager, ExtrasManager, FiltersManager, UserLogManager
from utils.checks import check_staff, InsufficientStaffRank
from utils.help import KuriHelp
from utils.utils import create_error_embed
from utils.context import KurisuContext

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
    'cogs.server_logs'
)

DEBUG = False
IS_DOCKER = os.environ.get('IS_DOCKER', '')

if IS_DOCKER:
    def get_env(name: str):
        contents = os.environ.get(name)
        if contents is None:
            contents_file = os.environ.get(name + '_FILE')
            if contents_file:
                try:
                    with open(contents_file, 'r', encoding='utf-8') as f:
                        contents = f.readline().strip()
                except FileNotFoundError:
                    sys.exit(f"Couldn't find environment variables {name} or {name}_FILE.")
                except IsADirectoryError:
                    sys.exit(f"Attempted to open {contents_file} (env {name}_FILE) but it is a folder.")
            else:
                sys.exit(f"Missing {name}.")

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
    log.setLevel(logging.DEBUG)
    fmt = logging.Formatter('[{asctime}] [{levelname:^7s}] {name}.{funcName}: {message}', datefmt="%Y-%m-%d %H:%M:%S",
                            style='{')
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    log.addHandler(sh)
    logging.getLogger('discord').propagate = False
    logging.getLogger('gino').propagate = False


logger = logging.getLogger(__name__)


class Kurisu(commands.Bot):

    user: discord.ClientUser
    pool: asyncpg.Pool
    db_closed: bool
    tree: 'Kuritree'

    def __init__(self, command_prefix, description, commit, branch, pool):

        intents = discord.Intents(guilds=True, members=True, messages=True, reactions=True, bans=True, message_content=True)
        allowed_mentions = discord.AllowedMentions(everyone=False, roles=False)
        super().__init__(
            command_prefix=commands.when_mentioned_or(*command_prefix),
            description=description,
            intents=intents,
            allowed_mentions=allowed_mentions,
            case_insensitive=True,
            tree_cls=Kuritree
        )

        self.tz = pytz.timezone('US/Pacific')
        self.startup = datetime.now(self.tz)
        self.IS_DOCKER = IS_DOCKER
        self.commit = commit
        self.branch = branch

        self.roles: dict[str, discord.Role] = {}

        self.channels: dict[str, Union[discord.TextChannel, discord.VoiceChannel]] = {}

        self.failed_cogs = []
        self.channels_not_found = []
        self.roles_not_found = []

        self.pool = pool
        self.db_closed = False

        self.logs = UserLogManager(self)

        self.warns = WarnsManager(self)
        self.configuration = ConfigurationManager(self)
        self.restrictions = RestrictionsManager(self)
        self.extras = ExtrasManager(self)
        self.filters = FiltersManager(self)

        self.err_channel: Optional[Union[discord.TextChannel, discord.VoiceChannel]] = None
        self.actions = []
        self.pruning = False
        self.emoji = discord.PartialEmoji.from_str("⁉")
        self.colour = discord.Colour(0xb01ec3)

        self._is_all_ready = asyncio.Event()

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
        await self.load_cogs()

    async def get_context(self, origin: Union[discord.Interaction, discord.Message], /, *, cls=KurisuContext) -> KurisuContext:
        return await super().get_context(origin, cls=cls)

    async def on_ready(self):
        if self._is_all_ready.is_set():
            return

        self.guild = self.guilds[0]

        self.emoji = discord.utils.get(self.guild.emojis, name='kurisu') or discord.PartialEmoji.from_str("⁉")

        # Load channels and roles
        await self.load_channels()
        await self.load_roles()

        self.helper_roles: dict[str, discord.Role] = {"3DS": self.roles['On-Duty 3DS'],
                                                      "WiiU": self.roles['On-Duty Wii U'],
                                                      "Switch": self.roles['On-Duty Switch'],
                                                      "Legacy": self.roles['On-Duty Legacy']
                                                      }

        self.assistance_channels: tuple[Union[discord.TextChannel, discord.VoiceChannel], ...] = (
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
                                                     }

        self.err_channel = self.channels['bot-err']
        self.tree.err_channel = self.err_channel

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
        self.db_closed = True
        await super().close()
        await self.session.close()
        await self.pool.close()

    async def load_cogs(self):
        for extension in cogs:
            try:
                await self.load_extension(extension)
            except BaseException as e:
                traceback.print_exc()
                logger.error("%s failed to load.", extension)
                self.failed_cogs.append((extension, type(e).__name__, e))

    async def load_channels(self):
        channels = ['announcements', 'welcome-and-rules', '3ds-assistance-1', '3ds-assistance-2', 'wiiu-assistance',
                    'switch-assistance-1', 'switch-assistance-2', 'helpers', 'watch-logs', 'message-logs',
                    'upload-logs', 'hacking-general', 'meta', 'appeals', 'legacy-systems', 'dev', 'off-topic',
                    'voice-and-music', 'bot-cmds', 'bot-talk', 'mods', 'mod-mail', 'mod-logs', 'server-logs', 'bot-err',
                    'elsewhere', 'newcomers', 'nintendo-discussion', 'tech-talk', 'hardware', 'streaming-gamer']

        for n in channels:
            db_channel = await self.configuration.get_channel_by_name(n)
            if db_channel:
                channel_id = db_channel[0]
                channel = self.guild.get_channel(channel_id)
                if channel and isinstance(channel, (discord.TextChannel, discord.VoiceChannel)):
                    self.channels[n] = channel
                    continue
            channel = discord.utils.get(self.guild.channels, name=n)
            if channel and isinstance(channel, (discord.TextChannel, discord.VoiceChannel)):
                self.channels[n] = channel
                await self.configuration.add_channel(name=n, channel=channel)
            else:
                self.channels_not_found.append(n)
                logger.warning("Failed to find channel %s", n)

    async def load_roles(self):
        roles = ['Helpers', 'Staff', 'HalfOP', 'OP', 'SuperOP', 'Owner', 'On-Duty 3DS', 'On-Duty Wii U',
                 'On-Duty Switch', 'On-Duty Legacy', 'Probation', 'Retired Staff', 'Verified', 'Trusted', 'Muted',
                 'No-Help', 'No-elsewhere', 'No-Memes', 'No-art', '#art-discussion', 'No-Embed', '#elsewhere',
                 'Small Help', 'meta-mute', 'appeal-mute', 'crc', 'No-Tech', 'help-mute', 'streamer(temp)', '🍰']

        for n in roles:
            db_role = await self.configuration.get_role(n)
            if db_role:
                role_id = db_role[0]
                role = self.guild.get_role(role_id)
                if role:
                    self.roles[n] = role
                    continue
            else:
                role = discord.utils.get(self.guild.roles, name=n)
                if not role:
                    self.roles_not_found.append(n)
                    logger.warning("Failed to find role %s", n)
                else:
                    self.roles[n] = role
                    await self.configuration.add_role(name=n, role=role)

    async def on_command_error(self, ctx: KurisuContext, exc: commands.CommandError):
        author = ctx.author
        command = ctx.command
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

        elif isinstance(exc, InsufficientStaffRank):
            await ctx.send(str(exc))

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

        elif isinstance(exc, commands.errors.CommandOnCooldown):
            if not check_staff(self, 'Helper', author.id):
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
            embed = create_error_embed(ctx, exc)
            await channel.send(embed=embed)
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
        logger.error("", exc_info=True)
        if not self.err_channel:
            return

        exc_type, exc, tb = sys.exc_info()
        embed = discord.Embed(title="Error Event", colour=0xe50730)
        embed.add_field(name="Event Method", value=event_method)
        trace = "".join(traceback.format_exception(exc_type, exc, tb))
        embed.description = f"```py\n{trace}\n```"
        await self.err_channel.send(embed=embed)


class Kuritree(app_commands.CommandTree):

    def __init__(self, client):
        super().__init__(client)
        self.err_channel: Optional[Union[discord.TextChannel, discord.VoiceChannel]] = None
        self.logger = logging.getLogger(__name__)

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ):

        error = getattr(error, 'original', error)

        if isinstance(error, app_commands.CommandNotFound):
            return await interaction.response.send_message(error, ephemeral=True)

        author = interaction.user
        ctx = await commands.Context.from_interaction(interaction)
        command: str = interaction.command.name if interaction.command is not None else "No command"
        channel = self.err_channel or interaction.channel
        assert isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.Thread))

        if isinstance(error, app_commands.NoPrivateMessage):
            await ctx.send(f'`{command}` cannot be used in direct messages.', ephemeral=True)

        elif isinstance(error, app_commands.TransformerError):
            await interaction.response.send_message(error, ephemeral=True)

        elif isinstance(error, app_commands.MissingPermissions):
            await ctx.send(f"{author.mention} You don't have permission to use `{command}`.", ephemeral=True)

        elif isinstance(error, InsufficientStaffRank):
            await ctx.send(str(error), ephemeral=True)

        elif isinstance(error, app_commands.CheckFailure):
            await ctx.send(f'{author.mention} You cannot use `{command}`.', ephemeral=True)

        elif isinstance(error, app_commands.CommandOnCooldown):
            await ctx.send(
                f"{author.mention} This command was used {error.cooldown.per - error.retry_after:.2f}s ago and is on cooldown. "
                f"Try again in {error.retry_after:.2f}s.", ephemeral=True)
        else:
            if isinstance(error, discord.Forbidden):
                msg = f"💢 I can't help you if you don't let me!\n`{error.text}`."
            elif isinstance(error, app_commands.CommandInvokeError):
                msg = f'{author.mention} `{command}` raised an exception during usage'
            else:
                msg = f'{author.mention} Unexpected exception occurred while using the command `{command}`'

            await ctx.send(msg, ephemeral=True)
            if channel:
                embed = create_error_embed(interaction, error)
                await channel.send(embed=embed)
            else:
                self.logger.error("Error during application command usage.", exc_info=True)


async def startup():
    setup_logging()

    if discord.version_info.major < 2:
        logger.error("discord.py is not at least 2.0.0x. (current version: %s)", discord.__version__)
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

    async with asyncpg.create_pool(DATABASE_URL, min_size=20, max_size=20) as pool:
        logger.info("Starting Kurisu on commit %s on branch %s", commit, branch)
        bot = Kurisu(command_prefix=['.', '!'], description="Kurisu, the bot for Nintendo Homebrew!", commit=commit,
                     branch=branch, pool=pool)
        bot.help_command = KuriHelp()
        await bot.start(TOKEN)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(startup())
