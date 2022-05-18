from __future__ import annotations

import asyncio
import discord
import re

from discord.ext import commands
from utils import crud
from utils.checks import is_staff, check_if_user_can_ready
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.utils import KurisuContext, GuildContext


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
        self.join_list: list[int] = []

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
        if self.autoprobate:
            await member.add_roles(self.bot.roles['Probation'], reason="Auto-probation")
        else:
            if member.id not in self.join_list:
                self.join_list.append(member.id)
                if len(self.join_list) > 10:
                    self.autoprobate = True
                    await crud.set_flag('auto_probation', True)
                    await self.bot.channels['mods'].send("@everyone Raid alert multiple joins under 10 seconds! Autoprobation has been enabled.",
                                                         allowed_mentions=discord.AllowedMentions(everyone=True))
                    for member_id in self.join_list:
                        try:
                            await discord.Member(id=member_id).add_roles(self.bot.roles['Probation'], reason="Auto-probation")
                        except (discord.Forbidden, discord.HTTPException):
                            pass
                await asyncio.sleep(10)
                self.join_list.remove(member.id)

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
    async def ncready(self, ctx: GuildContext, *, reason=""):
        """Alerts online staff to a ready request in newcomers."""
        newcomers = self.bot.channels['newcomers']
        reason = reason[:300]  # truncate to 300 chars so kurisu doesn't send absurdly huge messages
        reason = re.sub(r'[^\x20-\x5b\x5d-\x7f]', r'', reason)  # filter out non-ascii and backslash
        reason = discord.utils.escape_mentions(reason)  # remove all other mentions, in case escaping tricks are attempted

        await ctx.message.delete()

        if reason:
            await newcomers.send(f'{ctx.author} (ID: {ctx.author.id}) is ready for unprobation.\n\nMessage: `{reason}` @here', allowed_mentions=discord.AllowedMentions(everyone=True))
            try:
                await ctx.author.send('✅ Online staff have been notified of your request.')
            except discord.errors.Forbidden:
                pass
        else:
            await newcomers.send(f'{ctx.author.mention}, please run this command again \
with a brief message explaining your situation (e.g., `.ready hey guys, i was having trouble hacking my console`). \
**Copying and pasting the example will not remove your probation.**', delete_after=10)
            ctx.command.reset_cooldown(ctx)


async def setup(bot):
    await bot.add_cog(Newcomers(bot))
