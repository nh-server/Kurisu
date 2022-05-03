from __future__ import annotations

import discord

from discord.ext import commands
from typing import Union, TYPE_CHECKING
from utils import utils, crud
from utils.checks import is_staff, check_staff_id, check_bot_or_staff
from utils.utils import get_user

if TYPE_CHECKING:
    from kurisu import Kurisu


class ModWarn(commands.Cog):
    """
    Warn commands.
    """

    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.emoji = discord.PartialEmoji.from_str('\u26A0')

    async def cog_check(self, ctx: commands.Context):
        if ctx.guild is None and ctx.command.name != "listwarns":
            raise commands.NoPrivateMessage()
        return True

    @is_staff('Helper')
    @commands.command()
    async def warn(self, ctx: commands.Context, member: Union[discord.Member, discord.User], *, reason=""):
        """Warn a user. Staff and Helpers only."""
        issuer = ctx.author
        channel = ctx.channel
        if await check_bot_or_staff(ctx, member, "warn"):
            return
        warn_count = len(await crud.get_warns(member.id))
        if warn_count >= 5:
            await ctx.send("A user can't have more than 5 warns!")
            return
        await crud.add_warn(member.id, issuer.id, reason)
        warn_count += 1
        if isinstance(member, discord.Member):
            msg = f"You were warned on {ctx.guild.name}."
            if reason != "":
                # much \n
                msg += " The given reason is: " + reason
            msg += f"\n\nPlease read the rules in {self.bot.channels['welcome-and-rules'].mention}. This is warn #{warn_count}."
            if warn_count == 2:
                msg += " __The next warn will automatically kick.__"
            elif warn_count == 3:
                msg += "\n\nYou were kicked because of this warning. You can join again right away. Two more warnings will result in an automatic ban."
            elif warn_count == 4:
                msg += "\n\nYou were kicked because of this warning. This is your final warning. You can join again, but **one more warn will result in a ban**."
            elif warn_count == 5:
                msg += "\n\nYou were automatically banned due to five warnings."
            await utils.send_dm_message(member, msg, ctx)
            if warn_count in {3, 4}:
                try:
                    self.bot.actions.append("wk:" + str(member.id))
                    await member.kick(reason=f"{warn_count} warns.")
                except discord.Forbidden:
                    await ctx.send("I can't kick this user!")
        if warn_count >= 5:  # just in case
            self.bot.actions.append("wb:" + str(member.id))
            try:
                await ctx.guild.ban(member, reason="5 warns.", delete_message_days=0)
            except discord.Forbidden:
                await ctx.send("I can't ban this user!")
        await ctx.send(f"{member.mention} warned. User has {warn_count} warning(s)")
        msg = f"⚠️ **Warned**: {issuer.mention} warned {member.mention} in {channel.mention} ({self.bot.escape_text(channel)}) (warn #{warn_count}) | {self.bot.escape_text(member)}"
        signature = utils.command_signature(ctx.command)
        if reason != "":
            # much \n
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.channels['mod-logs'].send(msg + (f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user." if reason == "" else ""))

    @is_staff('Helper')
    @commands.command()
    async def softwarn(self, ctx: commands.Context, member: Union[discord.Member, discord.User], *, reason=""):
        """Warn a user without automated action. Staff and Helpers only."""
        issuer = ctx.author
        channel = ctx.channel
        if await check_bot_or_staff(ctx, member, "warn"):
            return
        warn_count = len(await crud.get_warns(member.id))
        if warn_count >= 5:
            await ctx.send("A user can't have more than 5 warns!")
            return
        warn_count += 1
        await crud.add_warn(member.id, ctx.author.id, reason)
        if isinstance(member, discord.Member):
            msg = f"You were warned on {ctx.guild}."
            if reason != "":
                # much \n
                msg += " The given reason is: " + reason
            msg += f"\n\nThis is warn #{warn_count}."
            msg += "\n\nThis won't trigger any action."
            await utils.send_dm_message(member, msg, ctx)

        await ctx.send(f"{member.mention} softwarned. User has {warn_count} warning(s)")
        msg = f"⚠️ **Warned**: {issuer.mention} softwarned {member.mention} in {channel.mention} ({self.bot.escape_text(channel)}) (warn #{warn_count}) | {self.bot.escape_text(member)}"
        signature = utils.command_signature(self.warn)
        if reason != "":
            # much \n
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.channels['mod-logs'].send(msg + (
            f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user." if reason == "" else ""))

    @commands.hybrid_command()
    async def listwarns(self, ctx: commands.Context, member: Union[discord.Member, discord.User] = commands.Author):
        """List warns for a user. Helpers+ only for checking others."""
        issuer = ctx.author
        if not await check_staff_id("Helper", ctx.author.id) and (member != issuer):
            msg = f"{issuer.mention} Using this command on others is limited to Staff and Helpers."
            await ctx.send(msg)
            return
        embed = discord.Embed(color=discord.Color.dark_red())
        embed.set_author(name=f"Warns for {member}", icon_url=member.display_avatar.url)
        warns = await crud.get_warns(member.id)
        if warns:
            db_channel = await crud.get_dbchannel(ctx.channel.id)
            for idx, warn in enumerate(warns):
                try:
                    issuer = await get_user(ctx, warn.issuer)
                except discord.NotFound:
                    issuer = None
                value = ""
                if db_channel and db_channel.is_mod_channel:
                    value += f"Issuer: {issuer.name if issuer else warn.issuer}\n"
                value += f"Reason: {warn.reason} "
                embed.add_field(name=f"{idx + 1}: {discord.utils.snowflake_time(warn.id).strftime('%Y-%m-%d %H:%M:%S')}", value=value)
        else:
            embed.description = "There are none!"
            embed.colour = discord.Color.green()
        await ctx.send(embed=embed, ephemeral=True)

    @is_staff("SuperOP")
    @commands.command()
    async def copywarns(self, ctx: commands.Context, src: Union[discord.Member, discord.User], target: Union[discord.Member, discord.User]):
        """Copy warns from one user ID to another. Overwrites all warns of the target user ID. SOP+ only."""
        if await check_bot_or_staff(ctx, target, "warn"):
            return
        src_warns = await crud.get_warns(src.id)
        tgt_warns = await crud.get_warns(target.id)
        src_warn_count = len(src_warns)
        if not src_warns:
            await ctx.send(f"{src} has no warns!")
            return
        if len(tgt_warns) + src_warn_count > 5:
            return await ctx.send("Copying the warns would go over the max warn count.")

        for warn in src_warns:
            await crud.copy_warn(target.id, warn)

        await ctx.send(f"{src_warn_count} warns were copied from {src.name} to {target.name}!")
        msg = f"📎 **Copied warns**: {ctx.author.mention} copied {src_warn_count} warns from {self.bot.escape_text(src.name)}"\
              f"({src}) to {self.bot.escape_text(target.name)} ({target})"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("HalfOP")
    @commands.command()
    async def delwarn(self, ctx: commands.Context, member: Union[discord.Member, discord.User], idx: int):
        """Remove a specific warn from a user. Staff only."""
        warns = await crud.get_warns(member.id)
        if not warns:
            await ctx.send(f"{member.mention} has no warns!")
            return
        warn_count = len(warns)
        if idx > warn_count:
            await ctx.send(f"Warn index is higher than warn count ({warn_count})!")
            return
        if idx < 1:
            await ctx.send("Warn index is below 1!")
            return
        warn = warns[idx - 1]
        issuer = await get_user(ctx, warn.issuer)
        embed = discord.Embed(color=discord.Color.dark_red(), title=f"Warn {idx} on {discord.utils.snowflake_time(warn.id).strftime('%Y-%m-%d %H:%M:%S')}",
                              description=f"Issuer: {issuer}\nReason: {warn.reason}")
        await crud.remove_warn_id(member.id, idx)
        await ctx.send(f"{member.mention} has a warning removed!")
        msg = f"🗑 **Deleted warn**: {ctx.author.mention} removed warn {idx} from {member.mention} | {self.bot.escape_text(member)}"
        await self.bot.channels['mod-logs'].send(msg, embed=embed)

    @is_staff("HalfOP")
    @commands.command()
    async def clearwarns(self, ctx: commands.Context, member: Union[discord.Member, discord.User]):
        """Clear all warns for a user. Staff only."""
        warns = await crud.get_warns(member.id)
        if not warns:
            await ctx.send(f"{member.mention} has no warns!")
            return
        warn_count = len(warns)
        await crud.remove_warns(member.id)
        await ctx.send(f"{member.mention} no longer has any warns!")
        msg = f"🗑 **Cleared warns**: {ctx.author.mention} cleared {warn_count} warns from {member.mention} | {self.bot.escape_text(member)}"
        await self.bot.channels['mod-logs'].send(msg)


async def setup(bot):
    await bot.add_cog(ModWarn(bot))
