from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import discord
from discord.ext import commands

from utils import Restriction
from utils.checks import is_staff, check_bot_or_staff

if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.context import GuildContext


class ZeroBan(commands.Cog):
    """Reply-ban command with source message logging and automatic history scrubbing"""

    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.restrictions = bot.restrictions

    async def cog_check(self, ctx: GuildContext):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()

        return True

    @staticmethod
    def _trim(text: str, limit: int) -> str:
        if len(text) <= limit:
            return text

        return text[:limit - 1] + "…"

    async def _get_replied_message(self, ctx: GuildContext) -> discord.Message:
        reference = ctx.message.reference

        if reference is None or reference.message_id is None:
            raise commands.BadArgument("Reply to the message you want to Zeroban from.")

        if isinstance(reference.resolved, discord.Message):
            return reference.resolved

        channel = self.bot.get_channel(reference.channel_id or ctx.channel.id)

        if channel is None:
            channel = await self.bot.fetch_channel(reference.channel_id or ctx.channel.id)

        return await channel.fetch_message(reference.message_id)

    async def _log_source_message(
        self,
        ctx: GuildContext,
        message: discord.Message,
        reason: Optional[str],
    ):
        target = message.author
        content = self._trim(message.content or "*No text content.*", 4000)

        embed = discord.Embed(
            title="Zeroban source message",
            colour=discord.Colour.red(),
            timestamp=message.created_at,
        )

        embed.add_field(
            name="Message content",
            value=content,
            inline=False,
        )

        embed.add_field(
            name="Author",
            value=f"{target.mention} | `{self.bot.escape_text(target)}`\n`{target.id}`",
            inline=False,
        )

        embed.add_field(
            name="Channel",
            value=getattr(message.channel, "mention", str(message.channel)),
            inline=False,
        )

        if reason:
            embed.add_field(
                name="Reason",
                value=self._trim(reason, 1000),
                inline=False,
            )

        header = (
            f"⛔ **Zeroban evidence**: {ctx.author.mention} is banning "
            f"{target.mention} | `{self.bot.escape_text(target)}`"
        )

        for destination in (self.bot.channels["mod-logs"], self.bot.channels["mods"]):
            await destination.send(
                header,
                embed=embed,
                allowed_mentions=discord.AllowedMentions.none(),
            )

    @is_staff("OP")
    @commands.bot_has_permissions(ban_members=True, manage_messages=True)
    @commands.command(name="zeroban")
    async def zeroban(self, ctx: GuildContext, *, reason: Optional[str] = None):
        """
        Ban the author of the replied-to message, log the source message,
        delete the command invocation, and delete the banned user's last 24h of messages.
        """
        target_message = await self._get_replied_message(ctx)
        target = target_message.author

        if await check_bot_or_staff(ctx, target, "ban"):
            return

        await ctx.message.delete()

        audit_reason = reason or (
            f"Zeroban by {ctx.author}: "
            f"{self._trim(target_message.content or 'No text content.', 300)}"
        )

        await self._log_source_message(ctx, target_message, reason)

        await ctx.guild.ban(
            target,
            reason=audit_reason,
            delete_message_seconds=86400,
        )

        await self.restrictions.remove_restriction(target, Restriction.Ban)

        await self.bot.logs.post_action_log(
            ctx.author,
            target,
            "ban",
            reason=audit_reason,
        )


async def setup(bot):
    await bot.add_cog(ZeroBan(bot))
