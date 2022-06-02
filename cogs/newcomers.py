from __future__ import annotations

import asyncio
import discord
import re

from discord.ext import commands
from typing import TYPE_CHECKING, Optional, Literal
from utils import crud
from utils.checks import is_staff, check_if_user_can_ready
from utils.utils import text_to_discord_file, parse_time


if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.context import KurisuContext, GuildContext


class RaidPopFlags(commands.FlagConverter, prefix='--', delimiter=' '):
    reason: Optional[str]
    regex: Optional[str]
    dry_run: bool = commands.flag(name='dry_run', default=False)
    younger_than: Optional[int] = commands.flag(name='younger_than', converter=parse_time, default=None)


class Newcomers(commands.Cog):
    """
    Handles auto-probation and commands related to the newcomers channel.
    """

    on_aliases = ('on', 'true', '1', 'enable')
    off_aliases = ('off', 'false', '0', 'disable')

    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.emoji = discord.PartialEmoji.from_str('🆕')
        self.autoprobate = False
        self.join_list: list[discord.Member] = []

    async def cog_check(self, ctx: KurisuContext):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        return True

    async def cog_load(self):
        flag_name = 'auto_probation'

        if flag := await crud.get_flag(flag_name):
            self.autoprobate = flag.value
        else:
            self.autoprobate = False
            await crud.add_flag(flag_name)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member not in self.join_list:
            self.join_list.append(member)
        if self.autoprobate:
            await member.add_roles(self.bot.roles['Probation'], reason="Auto-probation")
        else:
            if len(self.join_list) > 10:
                self.autoprobate = True
                await crud.set_flag('auto_probation', True)
                await self.bot.channels['mods'].send("@everyone Raid alert multiple joins under 10 seconds! "
                                                     "Autoprobation has been enabled.",
                                                     allowed_mentions=discord.AllowedMentions(everyone=True))
                for member in self.join_list:
                    try:
                        await member.add_roles(self.bot.roles['Probation'], reason="Auto-probation")
                    except (discord.Forbidden, discord.HTTPException):
                        pass
        await asyncio.sleep(10)
        if not self.autoprobate:
            try:
                self.join_list.remove(member)
            except ValueError:
                pass

    async def autoprobate_handler(self, ctx: GuildContext, enabled: Optional[bool] = None):
        if enabled is not None:
            self.autoprobate = enabled
            await crud.set_flag('auto_probation', enabled)

        inactive_text = f'**inactive**. ⚠️\nTo activate it, use `.autoprobate {" | ".join(self.on_aliases)}`.'
        active_text = f'**active**. ✅\nTo deactivate it, use `.autoprobate {" | ".join(self.off_aliases)}`.'
        await ctx.send(f'🔨 Auto-probation is {active_text if self.autoprobate else inactive_text}')

    @is_staff('Helper')
    @commands.group(name="autoprobate", aliases=['autoprobation'], invoke_without_command=True, case_insensitive=True)
    async def autoprobate_cmd(self, ctx: GuildContext):
        """
        Manages auto-probation.
        on | true | 1 | enable: turns on auto-probation.
        off | false | 0 | disable: turns off auto-probation.
        To display the status of auto-probation, invoke with no subcommand.
        """
        await self.autoprobate_handler(ctx)

    @is_staff('OP')
    @autoprobate_cmd.command(aliases=on_aliases, hidden=True)
    async def autoprobate_on(self, ctx: GuildContext):
        await self.autoprobate_handler(ctx, True)

    @is_staff('OP')
    @autoprobate_cmd.command(aliases=off_aliases, hidden=True)
    async def autoprobate_off(self, ctx: GuildContext):
        await self.autoprobate_handler(ctx, False)

    @check_if_user_can_ready()
    @commands.guild_only()
    @commands.command(aliases=['ready'], cooldown=commands.CooldownMapping.from_cooldown(rate=1, per=300.0, type=commands.BucketType.member))
    async def ncready(self, ctx: GuildContext, *, reason: str = ""):
        """Alerts online staff to a ready request in newcomers."""
        newcomers = self.bot.channels['newcomers']
        reason = reason[:300]  # truncate to 300 chars so kurisu doesn't send absurdly huge messages
        reason = re.sub(r'[^\x20-\x5b\x5d-\x7f]', r'', reason)  # filter out non-ascii and backslash
        reason = discord.utils.escape_mentions(reason)  # remove all other mentions, in case escaping tricks are attempted

        await ctx.message.delete()

        if reason:
            await newcomers.send(f'{ctx.author} (ID: {ctx.author.id}) is ready for unprobation.\n\n'
                                 'Message: `{reason}` @here', allowed_mentions=discord.AllowedMentions(everyone=True))
            try:
                await ctx.author.send('✅ Online staff have been notified of your request.')
            except discord.errors.Forbidden:
                pass
        else:
            await newcomers.send(f'{ctx.author.mention}, please run this command again with a brief message '
                                 'explaining your situation (e.g., `.ready hey guys, i was '
                                 'having trouble hacking my console`). **Copying and pasting '
                                 'the example will not remove your probation.**', delete_after=10)
            ctx.command.reset_cooldown(ctx)

    @is_staff('SuperOP')
    @commands.guild_only()
    @commands.command(extras={'examples': ['.raidpop kick --reason mass raid --younger_than 2d', '!raidpop ban --regex GiveAwayBot --dry_run True']})
    async def raidpop(self, ctx: GuildContext, action: Literal['kick', 'ban'], *, flags: RaidPopFlags):
        """Kicks or bans all probated members in the join list. SuperOP+ only.

        **Flags**
        --reason [str] Reason for the kick/ban.
        --regex [str] A regex pattern that the members usernames must partially match.
        --dry_run [True|False] Runs the command without doing any changes. False by default.
        --younger_than [#d#h#m#s] Affect accounts that were created less than the amount of time specified."""

        if not self.autoprobate:
            return await ctx.send("This can only be used with autoprobation on.")

        if len(self.join_list) == 0:
            return await ctx.send("The probation list is empty.")

        members = self.join_list.copy()

        if not flags.dry_run:
            self.join_list.clear()

        if action == 'ban':
            method = ctx.guild.ban
        else:
            method = ctx.guild.kick

        if flags.regex:
            try:
                pattern = re.compile(flags.regex, re.IGNORECASE)
            except re.error:
                return await ctx.send("Invalid regex expression passed in flag `--regex`.")
            members = [member for member in members if pattern.search(member.name)]

        if flags.younger_than:
            now = discord.utils.utcnow()
            members = [member for member in members if (now - member.created_at).total_seconds() < flags.younger_than]

        if len(members) == 0:
            return await ctx.send("No member matched all parameters.")

        file_txt = ""
        failed = 0

        for member in members:
            if not flags.dry_run:
                try:
                    await method(member, reason=flags.reason)
                except (discord.NotFound, discord.Forbidden):
                    failed = failed + 1
                    continue
            file_txt += f"{member.id} - {member}\n"

        file = text_to_discord_file(file_txt, name=f'{action}.txt')

        if not flags.dry_run:
            await ctx.send(f"Cleaned up recent probations {'kicking' if action == 'kick' else 'banning'} {len(members) - failed} members.", file=file)
        else:
            await ctx.send(f"Dry run completed. {len(members)} matched the given parameters", file=file)


async def setup(bot):
    await bot.add_cog(Newcomers(bot))
