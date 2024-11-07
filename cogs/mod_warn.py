from __future__ import annotations

import discord

from datetime import timedelta
from discord import app_commands
from discord.utils import format_dt
from discord.ext import commands
from typing import TYPE_CHECKING, Optional

from utils.checks import is_staff, check_bot_or_staff
from utils import check_staff, ordinal
from utils.utils import create_userinfo_embed
from utils.warns import WarnType
from utils.views import ModSenseView

if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.context import KurisuContext, GuildContext


@app_commands.default_permissions(manage_nicknames=True)
class ModWarn(commands.GroupCog):
    """
    Warn commands.
    """

    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.emoji = discord.PartialEmoji.from_str('\u26A0')
        self.warns = self.bot.warns
        self.configuration = bot.configuration

    async def cog_check(self, ctx: KurisuContext):
        if ctx.guild is None and ctx.command.name != "listwarns":
            raise commands.NoPrivateMessage()
        return True

    @is_staff('Helper')
    @commands.guild_only()
    @commands.command()
    async def warn(self, ctx: GuildContext, member: Optional[discord.Member | discord.User], *, reason: str):
        """Warn a user. Staff and Helpers only."""
        issuer = ctx.author
        channel = ctx.channel

        reference = ctx.message.reference
        message = None

        if not member and not reference:
            return await ctx.send("Specifiy a member to warn or reply to the offending message with this command.")
        elif reference and not member:
            if not reference.resolved:
                return await ctx.send("Failed to resolve message.")
            if isinstance(reference.resolved, discord.Message):
                member = reference.resolved.author
                message = reference.resolved.content if isinstance(reference.resolved, discord.Message) else None

        if not member:
            return await ctx.send("Failed to get member.")

        if await check_bot_or_staff(ctx, member, "warn"):
            return

        prev_count = await self.bot.warns.get_warnings_count(member)

        if prev_count >= 5:
            await ctx.send("A user can't have more than 5 warns!")
            return

        warn_id, count = await self.bot.warns.add_warning(member, issuer, reason)

        await ctx.send(f"{member} warned. User has {count} warning(s)")
        msg = f"⚠️ **Warned**: {issuer.mention} warned {member.mention} in {channel.mention} ({self.bot.escape_text(channel)}) (warn #{count}) | {self.bot.escape_text(member)}"
        if reason:
            msg += "\n✏️ __Reason__: " + reason
        if message:
            msg += f"\n🖊️ __Message__: {message}"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff('Helper')
    @commands.command()
    async def softwarn(self, ctx: GuildContext, member: discord.Member | discord.User, *, reason: Optional[str]):
        """Warn a user without automated action. Staff and Helpers only."""
        issuer = ctx.author
        channel = ctx.channel

        if await check_bot_or_staff(ctx, member, "warn"):
            return

        prev_count = await self.bot.warns.get_warnings_count(member)

        if prev_count >= 5:
            await ctx.send("A user can't have more than 5 warns!")
            return

        warn_id, count = await self.bot.warns.add_warning(member, issuer, reason, do_action=False)
        await ctx.send(f"{member.mention} softwarned. User has {count} warning(s)")
        msg = f"⚠️ **Warned**: {issuer.mention} softwarned {member.mention} in {channel.mention} ({self.bot.escape_text(channel)}) (warn #{count}) | {self.bot.escape_text(member)}"
        if reason is not None:
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff('OP')
    @app_commands.guild_only
    @app_commands.command(name='multiwarn')
    async def multiwarn_app(self, interaction: discord.Interaction, member: discord.Member | discord.User, warn_number: int, *, reason: Optional[str], pinned: bool = False):
        """Applies a number of warns to a user. Staff only.
        Args:
            member: Member to warn.
            warn_number: Number of warns to apply.
            reason: Reason for the warns.
            pinned: Whether the warns should be pinned or not.
        """

        issuer = interaction.user
        channel = interaction.channel

        assert isinstance(channel, discord.TextChannel)
        assert isinstance(issuer, discord.Member)

        if await check_bot_or_staff(interaction, member, "warn"):
            return

        count = await self.bot.warns.get_warnings_count(member)

        if count + warn_number >= 5:
            await interaction.response.send_message("A user can't have more than 5 warns!", ephemeral=True)
            return

        warn_type = WarnType.Pinned if pinned else WarnType.Ephemeral

        for _ in range(warn_number):
            _, count = await self.bot.warns.add_warning(member, issuer, reason, do_action=False, send_dm=False, warn_type=warn_type)
        await interaction.response.send_message(f"{member.mention} softwarned for {warn_number}. User now has {count} warning(s)")
        msg = f"⚠️ **Warned**: {issuer.mention} softwarned {member.mention} {warn_number} times in {channel.mention} ({self.bot.escape_text(channel)}) (Final warn count: {count}) | {self.bot.escape_text(member)}"
        if reason is not None:
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff('Helper')
    @commands.guild_only()
    @commands.command()
    async def pinwarn(self, ctx: GuildContext, member: Optional[discord.Member | discord.User], *, reason: str):
        """Warn a user with a pinned warn. Staff and Helpers only."""
        issuer = ctx.author
        channel = ctx.channel

        reference = ctx.message.reference
        message = None

        if not member and not reference:
            return await ctx.send("Specifiy a member to warn or reply to the offending message with this command.")
        elif reference and not member:
            if not reference.resolved:
                return await ctx.send("Failed to resolve message.")
            if isinstance(reference.resolved, discord.Message):
                member = reference.resolved.author
                message = reference.resolved.content if isinstance(reference.resolved, discord.Message) else None

        if not member:
            return await ctx.send("Failed to get member.")

        if await check_bot_or_staff(ctx, member, "warn"):
            return

        prev_count = await self.bot.warns.get_warnings_count(member)

        if prev_count >= 5:
            await ctx.send("A user can't have more than 5 warns!")
            return

        warn_id, count = await self.bot.warns.add_warning(member, issuer, reason, warn_type=WarnType.Pinned)

        await ctx.send(f"{member} warned. User has {count} warning(s)")
        msg = f"⚠️ **Warned**: {issuer.mention} warned {member.mention} in {channel.mention} ({self.bot.escape_text(channel)}) (warn #{count}) | {self.bot.escape_text(member)}"
        if reason:
            msg += "\n✏️ __Reason__: " + reason
        if message:
            msg += f"\n🖊️ __Message__: {message}"
        await self.bot.channels['mod-logs'].send(msg)

    @commands.hybrid_command()
    async def listwarns(self, ctx: KurisuContext, member: discord.Member | discord.User = commands.Author):
        """List warns for a user. Helpers+ only for checking others."""
        issuer = ctx.author
        if not check_staff(ctx.bot, "Helper", ctx.author.id) and member != issuer:
            msg = f"{issuer.mention} Using this command on others is limited to Staff and Helpers."
            await ctx.send(msg)
            return
        db_channel = await self.configuration.get_channel(ctx.channel.id)
        show_issuer = db_channel.mod_channel if db_channel else False
        warns = [w async for w in self.warns.get_warnings(member)]

        if not warns:
            return await ctx.send("No warns found.")

        embed = discord.Embed(color=discord.Color.dark_red())
        embed.set_author(name=f"Warns for {member}", icon_url=member.display_avatar.url)

        for idx, warn in enumerate(warns):
            issuer = await ctx.get_user(warn.issuer_id)
            value = ""
            if show_issuer:
                value += f"Issuer: {issuer.name if issuer else warn.issuer_id}\n"
            value += f"Reason: {warn.reason}"
            if warn.type == WarnType.Ephemeral:
                value += f"\nExpires: {format_dt(warn.date + timedelta(days=180))}"
            embed.add_field(
                name=f"{idx + 1}: {warn.date:%Y-%m-%d %H:%M:%S}",
                value=value)
        await ctx.send(embed=embed)

    @is_staff("SuperOP")
    @commands.command()
    async def copywarns(self, ctx: GuildContext, src: discord.Member | discord.User, target: discord.Member | discord.User):
        """Copy warns from one user ID to another. Overwrites all warns of the target user ID. SOP+ only."""

        if await check_bot_or_staff(ctx, target, "warn"):
            return

        src_warns = await self.warns.get_warnings_count(src)
        tgt_warns = await self.warns.get_warnings_count(target)

        if not src_warns:
            await ctx.send(f"{src} has no warns!")
            return

        if tgt_warns + src_warns > 5:
            return await ctx.send("Copying the warns would go over the max warn count.")

        res = await self.warns.copy_warnings(src, target)

        if not res:
            await ctx.send("Failed to copy warns.")
            return

        await ctx.send(f"{src_warns} warns were copied from {src.name} to {target.name}!")
        msg = f"📎 **Copied warns**: {ctx.author.mention} copied {res} warns from {self.bot.escape_text(src.name)}"\
              f"({src}) to {self.bot.escape_text(target.name)} ({target})"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("HalfOP")
    @commands.command()
    async def delwarn(self, ctx: GuildContext, member: discord.Member | discord.User, idx: commands.Range[int, 1, 5], *, reason: str):
        """Remove a specific warn from a user. Staff only."""
        warns = [w async for w in self.warns.get_warnings(member)]
        if not warns:
            await ctx.send(f"{member.mention} has no warns!")
            return
        warn_count = len(warns)
        if idx > warn_count:
            await ctx.send(f"Warn index is higher than warn count ({warn_count})!")
            return
        warn = warns[idx - 1]
        issuer = await ctx.get_user(warn.issuer_id)
        embed = discord.Embed(color=discord.Color.dark_red(), title=f"Warn {idx} on {discord.utils.snowflake_time(warn.warn_id).strftime('%Y-%m-%d %H:%M:%S')}",
                              description=f"Issuer: {issuer.name if issuer else warn.issuer_id}\nReason: {warn.reason}")
        await self.warns.delete_warning(warn.warn_id, ctx.author.id, reason)
        await ctx.send(f"{member.mention} {ordinal(idx)} warn has been removed.")
        msg = f"🗑 **Deleted warn**: {ctx.author.mention} removed warn {idx} from {member.mention} | {self.bot.escape_text(member)}"
        await self.bot.channels['mod-logs'].send(msg, embed=embed)

    @is_staff("HalfOP")
    @commands.command()
    async def clearwarns(self, ctx: GuildContext, member: discord.Member | discord.User, *, reason: str):
        """Clear all warns for a user. Staff only."""
        res = await self.warns.delete_all_warnings(member, ctx.author, reason)
        if not res:
            await ctx.send(f"{member.mention} has no warns!")
            return
        await ctx.send(f"{member.mention} no longer has any warns!")
        msg = f"🗑 **Cleared warns**: {ctx.author.mention} cleared {res} warns from {member.mention} | {self.bot.escape_text(member)}"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("OP")
    @commands.guild_only()
    @commands.max_concurrency(1, commands.BucketType.guild)
    @commands.hybrid_command()
    async def modsense(self, ctx: GuildContext, user: discord.Member | discord.User):
        """Shows information of user along with warn stuff. Staff and Helpers only."""

        embed = await create_userinfo_embed(user, ctx.guild)

        warns = [w async for w in self.warns.get_warnings(user)]
        deleted_warns = [w async for w in self.warns.get_deleted_warnings(user)]

        view = ModSenseView(ctx.bot, warns, deleted_warns, ctx.author, user, embed)

        view.message = await ctx.send(view=view, embed=embed, ephemeral=True)
        await view.wait()


async def setup(bot):
    await bot.add_cog(ModWarn(bot))
