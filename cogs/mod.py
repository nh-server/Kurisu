from __future__ import annotations

import discord
import re

from datetime import datetime, timedelta
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from discord.utils import format_dt
from subprocess import call
from typing import Union, Optional, TYPE_CHECKING
from utils import Restriction
from utils.converters import DateOrTimeToSecondsConverter, TimeTransformer
from utils.checks import is_staff, check_staff, check_bot_or_staff, is_staff_app
from utils.utils import paginate_message, send_dm_message, parse_time, text_to_discord_file, gen_color, create_error_embed

if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.context import KurisuContext, GuildContext


class PurgeFlags(commands.FlagConverter, prefix='--', delimiter=' '):
    before: Optional[discord.Message]
    after: Optional[discord.Message]
    ignore_list: list[discord.Member] = commands.flag(name='ignore', default=lambda ctx: [])
    exclusive_list: list[discord.Member] = commands.flag(name='only', default=lambda ctx: [])


class Mod(commands.Cog):
    """
    Staff commands.
    """

    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.emoji = discord.PartialEmoji.from_str('🧙')
        self.userinfo_ctx = app_commands.ContextMenu(
            name='userinfo',
            callback=self.userinfo_ctx_menu,
        )
        self.bot.tree.add_command(self.userinfo_ctx)
        self.restrictions = bot.restrictions
        self.configuration = bot.configuration
        self.extras = bot.extras
        self.logs = bot.logs
        self.filters = bot.filters

    async def cog_unload(self):
        self.bot.tree.remove_command(self.userinfo_ctx.name, type=self.userinfo_ctx.type)

    @is_staff("Owner")
    @commands.command()
    async def quit(self, ctx: KurisuContext):
        """Stops the bot."""
        await ctx.send("👋 Bye bye!")
        await self.bot.close()

    @is_staff("SuperOP")
    @commands.command()
    async def pull(self, ctx: KurisuContext):
        """Pull new changes from GitHub and restart."""
        if self.bot.IS_DOCKER:
            await ctx.send("Pull isn't used when running from a Docker container!")
            return
        else:
            await ctx.send("Pulling changes...")
            call(['git', 'pull'])
            await ctx.send("👋 Restarting bot!")
            await self.bot.close()

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command(aliases=['ui'])
    async def userinfo(self, ctx: GuildContext, u: Union[discord.Member, discord.User]):
        """Shows information from a user. Staff and Helpers only."""
        basemsg = f"name = {u.name}\nid = {u.id}\ndiscriminator = {u.discriminator}\navatar = <{u.avatar}>\nbot = {u.bot}\ndefault_avatar= <{u.default_avatar}>\ncreated_at = {u.created_at}\n"
        if isinstance(u, discord.Member):
            role = u.top_role.name
            await ctx.send(f"{basemsg}display_name = {u.display_name}\njoined_at = {u.joined_at}\nstatus ={u.status}\n"
                           f"activity = {u.activity.name if u.activity else None}\ncolour = {u.colour}\ntop_role = {role}\n"
                           f"guild_avatar= {f'<{u.guild_avatar}>' if u.guild_avatar else None}")
        else:
            try:
                ban = await ctx.guild.fetch_ban(u)
            except discord.NotFound:  # NotFound is raised if the user isn't banned
                ban = None
            await ctx.send(f"{basemsg}{f'**Banned**, reason: {ban.reason}' if ban is not None else ''}\n")

    @commands.guild_only()
    @commands.command(aliases=['ui2'])
    async def userinfo2(self, ctx: GuildContext, user: Union[discord.Member, discord.User] = commands.Author):
        """Shows information from a user. Staff and Helpers only."""

        if not check_staff(ctx.bot, 'Helper', ctx.author.id) and (ctx.author != user or ctx.channel != self.bot.channels['bot-cmds']):
            await ctx.message.delete()
            return await ctx.send(f"{ctx.author.mention} This command can only be used in {self.bot.channels['bot-cmds'].mention} and only on yourself.", delete_after=10)

        embed = discord.Embed(color=gen_color(user.id))
        embed.description = (
            f"**User:** {user.mention}\n"
            f"**User's ID:** {user.id}\n"
            f"**Created on:** {format_dt(user.created_at)} ({format_dt(user.created_at, style='R')})\n"
            f"**Default Profile Picture:** {user.default_avatar}\n"
        )

        if isinstance(user, discord.Member):
            member_type = "member"
            embed.description += (
                f"**Join date:** {format_dt(user.joined_at) if user.joined_at else None} ({format_dt(user.joined_at, style='R') if user.joined_at else None})\n"
                f"**Current Status:** {user.status}\n"
                f"**User Activity:** {user.activity}\n"
                f"**Current Display Name:** {user.display_name}\n"
                f"**Nitro Boost Info:** {f'Boosting since {format_dt(user.premium_since)}' if user.premium_since else 'Not a booster'}\n"
                f"**Current Top Role:** {user.top_role}\n"
                f"**Color:** {user.color}\n"
                f"**Profile Picture:** [link]({user.avatar})"
            )
            if user.guild_avatar:
                embed.description += f"\n**Guild Profile Picture:** [link]({user.guild_avatar})"
        else:
            member_type = "user"
            try:
                ban = await ctx.guild.fetch_ban(user)
                embed.description += f"\n**Banned**, reason: {ban.reason}"
            except discord.NotFound:
                pass

        member_type = member_type if not user.bot else "bot"
        embed.title = f"**Userinfo for {member_type} {user}**"
        embed.set_thumbnail(url=user.display_avatar.url)
        await ctx.send(embed=embed)

    @is_staff_app('Helper')
    @app_commands.guild_only
    @app_commands.default_permissions(manage_nicknames=True)
    async def userinfo_ctx_menu(self, interaction: discord.Interaction, user: discord.Member):
        assert interaction.guild is not None
        embed = discord.Embed(color=gen_color(user.id))
        embed.description = (
            f"**User:** {user.mention}\n"
            f"**User's ID:** {user.id}\n"
            f"**Created on:** {format_dt(user.created_at)} ({format_dt(user.created_at, style='R')})\n"
            f"**Default Profile Picture:** [link]({user.default_avatar})\n"
            f"**Created on:** {format_dt(user.created_at)} ({format_dt(user.created_at, style='R')})\n"
            f"**Default Profile Picture:** {user.default_avatar}\n"
        )
        if isinstance(user, discord.Member):
            member_type = "member"
            embed.description += (
                f"**Join date:** {format_dt(user.joined_at) if user.joined_at else None} ({format_dt(user.joined_at, style='R') if user.joined_at else None})\n"
                f"**Current Status:** {user.status}\n"
                f"**User Activity:** {user.activity}\n"
                f"**Current Display Name:** {user.display_name}\n"
                f"**Nitro Boost Info:** {f'Boosting since {format_dt(user.premium_since)}' if user.premium_since else 'Not a booster'}\n"
                f"**Current Top Role:** {user.top_role}\n"
                f"**Color:** {user.color}\n"
            )

            if user.avatar:
                embed.description += f"**Profile Picture:** [link]({user.avatar.url})"

            if user.guild_avatar:
                embed.description += f"\n**Guild Profile Picture:** [link]({user.guild_avatar})"
        else:
            member_type = "user"
            try:
                ban = await interaction.guild.fetch_ban(user)
                embed.description += f"\n**Banned**, reason: {ban.reason}"
            except discord.NotFound:
                pass

        member_type = member_type if not user.bot else "bot"
        embed.title = f"**Userinfo for {member_type} {user}**"
        embed.set_thumbnail(url=user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @is_staff_app('Helper')
    @commands.guild_only()
    @commands.command()
    async def guildinfo(self, ctx: GuildContext, invite: Optional[discord.Invite]):
        if not invite:
            guild = ctx.guild
            member_count = guild.member_count
        else:
            guild = invite.guild
            member_count = invite.approximate_member_count

        if guild is None or isinstance(guild, discord.Object):
            return await ctx.send("No information from the guild could be fetched.")

        embed = discord.Embed(title=f"Guild {guild.name}", color=gen_color(guild.id))
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="ID", value=guild.id)
        embed.add_field(name="Created on", value=format_dt(guild.created_at))
        embed.add_field(name="Verification", value=guild.verification_level)
        embed.add_field(name="Members", value=member_count)
        embed.add_field(name="Nitro boosters", value=guild.premium_subscription_count)
        embed.add_field(name="Vanity url", value=guild.vanity_url_code)
        links = ""
        if guild.icon is not None:
            links += f"[icon]({guild.icon.url}) "
        if guild.banner is not None:
            links += f"[banner]({guild.banner.url})"
        if links:
            embed.add_field(name="Links", value=links)
        if invite:
            expires = format_dt(invite.expires_at) if invite.expires_at else "Never"
            embed.add_field(name="Expires at", value=expires)
            if invite.inviter:
                embed.add_field(name="Inviter", value=f"{invite.inviter} ({invite.inviter.id})", inline=False)

        await ctx.send(embed=embed)

    @is_staff("Owner")
    @commands.guild_only()
    @commands.command(aliases=['gigayeet'])
    async def multiban(self, ctx: GuildContext, users: commands.Greedy[int]):
        """Multi-ban users."""
        author = ctx.author
        msg = "failed:\n"
        for m in users:
            try:
                await self.bot.guild.ban(discord.Object(id=m))
            except (discord.errors.NotFound, discord.errors.Forbidden) as e:
                msg += f"{m}:\n  {e.text}\n"
        paginator = paginate_message(msg)
        for page in paginator.pages:
            await send_dm_message(author, page)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def matchuser(self, ctx: GuildContext, *, rgx: str):
        """Match users by regex."""
        msg = ""
        matches = 0
        try:
            reg_expr = re.compile(rgx, re.IGNORECASE)
        except re.error:
            return await ctx.send("Invalid regex expression.")
        for m in self.bot.guild.members:
            if bool(reg_expr.search(m.name)):
                msg += f"{m.id} - {m}\n"
                matches += 1
        file = text_to_discord_file(msg, name="matches.txt")
        await ctx.send(f"Matched {matches} members.", file=file)

    @is_staff("Owner")
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.command(aliases=['gigayeetre'])
    async def multibanre(self, ctx: GuildContext, *, rgx: str):
        """Multi-ban users by regex."""
        to_ban = []
        banned = 0
        try:
            reg_expr = re.compile(rgx, re.IGNORECASE)
        except re.error:
            return await ctx.send("Invalid regex expression.")
        for m in self.bot.guild.members:
            if bool(reg_expr.search(m.name)):
                to_ban.append(m)
        if not to_ban:
            return await ctx.send("No member matched the regex expression!")
        msg = ""
        for m in to_ban:
            try:
                await m.ban()
                banned += 1
                msg += f"{m.id}\n"
            except (discord.errors.NotFound, discord.errors.Forbidden):
                pass
        file = text_to_discord_file(msg, name="banned.txt")
        await ctx.send(f"Banned {banned} members.", file=file)

    class ChannelorTime(commands.Converter):
        async def convert(self, ctx, arg: str):
            try:
                return ctx.bot.get_channel(int(arg))
            except ValueError:
                time = parse_time(arg)
                if time != -1:
                    return time
            raise commands.BadArgument("Invalid channel id or time format.")

    @is_staff("Helper")
    @commands.bot_has_permissions(manage_channels=True)
    @commands.guild_only()
    @commands.command()
    async def slowmode(self, ctx: GuildContext, channel: Optional[Union[discord.TextChannel, discord.VoiceChannel, discord.Thread]], *, length: int = commands.parameter(converter=DateOrTimeToSecondsConverter)):
        """Apply a given slowmode time to a channel.

        The time format is identical to that used for timed kicks/bans/takehelps.
        It is not possible to set a slowmode longer than 6 hours.

        Helpers in assistance channels and Staff only."""

        if channel is None:
            channel = ctx.channel

        if channel not in self.bot.assistance_channels and not check_staff(ctx.bot, "OP", ctx.author.id):
            return await ctx.send("You cannot use this command outside of assistance channels.")

        if length > 21600:
            return await ctx.send("💢 You can't slowmode a channel for longer than 6 hours!")

        try:
            await channel.edit(slowmode_delay=length)  # type: ignore
        except discord.errors.Forbidden:
            return await ctx.send("💢 I don't have permission to do this.")

        if length > 0:
            await ctx.send(f"Slowmode delay for {channel.mention} is now {length} seconds.")
            msg = f"🕙 **Slowmode**: {ctx.author.mention} set a slowmode delay of {length} seconds in {channel.mention}"
        else:
            await ctx.send(f"Slowmode has been removed for {channel.mention}.")
            msg = f"🕙 **Slowmode**: {ctx.author.mention} removed the slowmode delay in {channel.mention}"
        await self.bot.channels["mod-logs"].send(msg)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command(aliases=['clear'], extras={'examples': ['.purge #hacking-general 10 --exclude Kurisu#1234', '.purge 10', '.purge 10 --before 983086930910654594']})
    async def purge(self, ctx: GuildContext, channel: Optional[Union[discord.TextChannel, discord.VoiceChannel, discord.Thread]], limit: commands.Range[int, 1], *, flags: PurgeFlags):
        """Clears at most a given number of messages in current channel or a channel if given. Helpers in assistance channels and Staff only.

        **Flags**
        --before [Message] Deletes messages created before the provided message.
        --after [Message] Deletes messages created after the provided message. If this is used, the oldest messages are deleted first.
        --ignore [Member] Ignores the member messages when deleting. Can be used multiple times. Can't be used with --only.
        --only [Member] Only deletes the messages by this member. Can be used multiple times. Can't be used with --ignore."""

        if not channel:
            channel = ctx.channel
        if not channel.permissions_for(ctx.author).manage_messages:
            return await ctx.send("You don't have permission to delete messages in this channel.")
        if flags.exclusive_list and flags.ignore_list:
            return await ctx.send("You can't use the flags --include and --exclude together.")

        # Try to recreate original behaviour in all cases
        if channel == ctx.channel:
            await ctx.message.delete()

        checks = [lambda m: not m.pinned]

        if flags.exclusive_list:
            checks.append(lambda m: not m.pinned or m.author_id in flags.exclusive_list)

        if flags.ignore_list:
            checks.append(lambda m: not m.author_id not in flags.ignore_list)

        def check(message):
            return all(c(message) for c in checks)

        try:
            deleted = await channel.purge(limit=limit, before=flags.before, after=flags.after,
                                          check=check)
        except discord.HTTPException as exc:
            return await ctx.send(f"Deleting messages failed {exc}")
        if deleted:
            msg = f"🗑 **Cleared**: {ctx.author.mention} cleared {len(deleted)} messages in {channel.mention}"
            await self.bot.channels['mod-logs'].send(msg)
        else:
            await ctx.send("No messages were deleted.", delete_after=10)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def metamute(self, ctx: GuildContext, member: discord.Member, *, reason: Optional[str]):
        """Mutes a user, so they can't speak in meta. Staff only."""
        await self.restrictions.add_restriction(member, Restriction.MetaMute, reason)
        await self.logs.post_action_log(ctx.author, member, 'meta-mute')
        await ctx.send(f"{member.mention} can no longer speak in meta.")
        await self.logs.post_action_log(ctx.author, member, 'meta-mute', reason=reason)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    @commands.command()
    async def metaunmute(self, ctx: GuildContext, member: discord.Member, *, reason: Optional[str]):
        """Unmutes a user so they can speak in meta. Staff only."""
        await self.bot.restrictions.remove_restriction(member, Restriction.MetaMute)
        await ctx.send(f"{member.mention} can now speak in meta again.")
        await self.logs.post_action_log(ctx.author, member, 'meta-unmute', reason=reason)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command(aliases=["appealsmute"])
    async def appealmute(self, ctx: GuildContext, member: discord.Member, *, reason: Optional[str]):
        """Mutes a user, so they can't speak in appeals. Staff only."""
        await self.bot.restrictions.add_restriction(member, Restriction.AppealsMute, reason)
        await ctx.send(f"{member.mention} can no longer speak in appeals.")
        await self.logs.post_action_log(ctx.author, member, 'appeals-mute', reason=reason)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    @commands.command(aliases=["appealsunmute"])
    async def appealunmute(self, ctx: GuildContext, member: discord.Member, *, reason: Optional[str]):
        """Unmutes a user so they can speak in appeals. Staff only."""
        await self.bot.restrictions.remove_restriction(member, Restriction.AppealsMute)
        await ctx.send(f"{member.mention} can now speak in appeals again.")
        await self.logs.post_action_log(ctx.author, member, 'appeals-unmute', reason=reason)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    @commands.command()
    async def mute(self, ctx: GuildContext, member: discord.Member, *, reason: Optional[str]):
        """Mutes a user so they can't speak. Staff only."""
        if await check_bot_or_staff(ctx, member, "mute"):
            return
        await self.bot.restrictions.add_restriction(member, Restriction.Muted, reason)
        await ctx.send(f"{member.mention} can no longer speak.")
        await self.logs.post_action_log(ctx.author, member, 'mute', reason=reason)

    @is_staff("HalfOP")
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    @commands.command()
    async def oldtimemute(self, ctx: GuildContext, member: discord.Member, length: int = commands.parameter(converter=DateOrTimeToSecondsConverter), *, reason: Optional[str]):
        """Mutes a user for a limited period of time, so they can't speak. Staff only.\n\nLength format: #d#h#m#s"""
        if await check_bot_or_staff(ctx, member, "mute"):
            return

        issuer = ctx.author

        timestamp = datetime.now(self.bot.tz)
        delta = timedelta(seconds=length)
        unmute_time = timestamp + delta

        await self.bot.restrictions.add_restriction(member, Restriction.Muted, reason, end_date=unmute_time)

        await ctx.send(f"{member.mention} can no longer speak.")
        await self.logs.post_action_log(issuer, member, 'time-mute', reason=reason, until=unmute_time)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def unmute(self, ctx: GuildContext, member: discord.Member, *, reason: Optional[str]):
        """Unmutes a user so they can speak. Staff only."""
        await self.bot.restrictions.remove_restriction(member, Restriction.Muted)
        await ctx.send(f"{member.mention} can now speak again.")
        await self.logs.post_action_log(ctx.author, member, 'unmute', reason=reason)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command(aliases=['timemute'])
    async def timeout(self, ctx: GuildContext, member: discord.Member, length: int = commands.parameter(converter=DateOrTimeToSecondsConverter), *, reason: Optional[str]):
        """Times out a user. Staff only.\n\nLength format: #d#h#m#s"""
        if await check_bot_or_staff(ctx, member, "timeout"):
            return

        if length > 2419200:  # Timeout time can't be more than 28 days
            return await ctx.send("Timeouts can't be longer than 28 days!")

        issuer = ctx.author
        timeout_expiration = discord.utils.utcnow() + timedelta(seconds=length)
        timeout_expiration_str = format_dt(timeout_expiration)
        await member.timeout(timeout_expiration, reason=reason)

        msg_user = "You were given a timeout!"
        if reason is not None:
            msg_user += " The given reason is: " + reason
        msg_user += f"\n\nThis timeout lasts until {timeout_expiration_str}."
        await send_dm_message(member, msg_user, ctx)

        await ctx.send(f"{member.mention} has been given a timeout.")
        await self.logs.post_action_log(issuer, member, 'timeout', reason=reason, until=timeout_expiration)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def untimeout(self, ctx: GuildContext, member: discord.Member, *, reason: Optional[str]):
        """Removes a timeout from a user. Staff only."""
        if member.timed_out_until is None:
            return await ctx.send("This member doesn't have a timeout!")
        await member.timeout(None)
        await ctx.send(f"{member.mention} timeout was removed.")
        await self.logs.post_action_log(ctx.author, member, 'no-timeout', reason=reason)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def art(self, ctx: GuildContext, member: discord.Member, *, reason: Optional[str]):
        """Restore art-discussion access for a user. Staff only."""
        await self.bot.restrictions.remove_restriction(member, Restriction.NoArt)
        await ctx.send(f"{member.mention} can access art-discussion again.")
        await self.logs.post_action_log(ctx.author, member, 'give-art', reason=reason)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def noart(self, ctx: GuildContext, member: discord.Member, *, reason: Optional[str]):
        """Removes art-discussion access from a user. Staff only."""
        await self.bot.restrictions.add_restriction(member, Restriction.NoArt, reason)
        await ctx.send(f"{member.mention} can no longer access art-discussion.")
        await self.logs.post_action_log(ctx.author, member, 'take-art', reason=reason)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def elsewhere(self, ctx: GuildContext, member: discord.Member, *, reason: Optional[str]):
        """Restore elsewhere access for a user. Staff only."""

        await self.bot.restrictions.remove_restriction(member, Restriction.NoElsewhere)
        await ctx.send(f"{member.mention} can access elsewhere again.")
        await self.logs.post_action_log(ctx.author, member, 'give-elsewhere', reason=reason)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def noelsewhere(self, ctx: GuildContext, member: discord.Member, *, reason: Optional[str]):
        """Removes elsewhere access from a user. Staff only."""
        await self.bot.restrictions.add_restriction(member, Restriction.NoElsewhere, reason)
        await ctx.send(f"{member.mention} can no longer access elsewhere.")
        await self.logs.post_action_log(ctx.author, member, 'take-elsewhere', reason=reason)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def noembed(self, ctx: GuildContext, member: discord.Member, *, reason: Optional[str]):
        """Removes embed permissions from a user. Staff only."""
        if await check_bot_or_staff(ctx, member, "noembed"):
            return
        await self.bot.restrictions.add_restriction(member, Restriction.NoEmbed, reason)
        await ctx.send(f"{member.mention} can no longer embed links or attach files.")
        await self.logs.post_action_log(ctx.author, member, 'no-embed', reason=reason)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def embed(self, ctx: GuildContext, member: discord.Member, *, reason: Optional[str]):
        """Restore embed permissions for a user. Staff only."""
        await self.bot.restrictions.remove_restriction(member, Restriction.NoEmbed)
        await ctx.send(f"{member.mention} can now embed links and attach files again.")
        await self.logs.post_action_log(ctx.author, member, 'embed', reason=reason)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command(aliases=["nohelp", "yesnthelp"])
    async def takehelp(self, ctx: GuildContext, member: Union[discord.Member, discord.User], *, reason: Optional[str]):
        """Remove access to the assistance channels. Staff and Helpers only."""
        if await check_bot_or_staff(ctx, member, "takehelp"):
            return
        await self.bot.restrictions.add_restriction(member, Restriction.TakeHelp, reason)
        await ctx.send(f"{member.mention} can no longer access the help channels.")
        await self.logs.post_action_log(ctx.author, member, 'take-help', reason=reason)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command(aliases=["yeshelp"])
    async def givehelp(self, ctx: GuildContext, member: Union[discord.Member, discord.User], *, reason: Optional[str]):
        """Restore access to the assistance channels. Staff and Helpers only."""
        await self.restrictions.remove_restriction(member, Restriction.TakeHelp)
        await ctx.send(f"{member.mention} can access the help channels again.")
        await self.logs.post_action_log(ctx.author, member, 'give-help', reason=reason)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command(aliases=["timenohelp"])
    async def timetakehelp(self, ctx: GuildContext, member: discord.Member, length: int = commands.parameter(converter=DateOrTimeToSecondsConverter), *, reason: Optional[str]):
        """Restricts a user from Assistance Channels for a limited period of time. Staff and Helpers only.\n\nLength format: #d#h#m#s"""
        if await check_bot_or_staff(ctx, member, "takehelp"):
            return

        issuer = ctx.author

        delta = timedelta(seconds=length)
        timestamp = datetime.now(self.bot.tz)

        takehelp_expiration = timestamp + delta

        await self.restrictions.add_restriction(member, Restriction.TakeHelp, reason, end_date=takehelp_expiration)
        await ctx.send(f"{member.mention} can no longer speak in Assistance Channels.")
        await self.logs.post_action_log(issuer, member, 'take-help', reason=reason, until=takehelp_expiration)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command(aliases=["notech", "technt"])
    async def taketech(self, ctx: GuildContext, member: Union[discord.Member, discord.User], *, reason: Optional[str]):
        """Remove access to the tech channel. Staff and Helpers only."""
        if await check_bot_or_staff(ctx, member, "taketech"):
            return
        await self.restrictions.add_restriction(member, Restriction.NoTech, reason)
        await ctx.send(f"{member.mention} can no longer access the tech channel.")
        await self.logs.post_action_log(ctx.author, member, 'take-tech', reason=reason)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command(aliases=["yestech"])
    async def givetech(self, ctx: GuildContext, member: Union[discord.Member, discord.User], *, reason: Optional[str]):
        """Restore access to the tech channel. Staff and Helpers only."""
        await self.restrictions.remove_restriction(member, Restriction.NoTech)
        await ctx.send(f"{member.mention} can access the tech channel again.")
        await self.logs.post_action_log(ctx.author, member, 'take-tech', reason=reason)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command(aliases=["timenotech"])
    async def timetaketech(self, ctx: GuildContext, member: discord.Member, length: int = commands.parameter(converter=DateOrTimeToSecondsConverter), *, reason: Optional[str]):
        """Restricts a user from the tech channel for a limited period of time. Staff and Helpers only.\n\nLength format: #d#h#m#s"""
        if await check_bot_or_staff(ctx, member, "taketech"):
            return

        delta = timedelta(seconds=length)
        timestamp = datetime.now(self.bot.tz)

        notech_expiration = timestamp + delta

        await self.restrictions.add_restriction(member, Restriction.NoTech, reason, end_date=notech_expiration)
        await ctx.send(f"{member.mention} can no longer speak in the tech channel.")
        await self.logs.post_action_log(ctx.author, member, 'take-tech', reason=reason, until=notech_expiration)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command(aliases=["mutehelp"])
    async def helpmute(self, ctx: GuildContext, member: Union[discord.Member, discord.User], *, reason: Optional[str]):
        """Remove speak perms to the assistance channels. Staff and Helpers only."""
        if await check_bot_or_staff(ctx, member, "helpmute"):
            return
        await self.restrictions.add_restriction(member, Restriction.HelpMute, reason)
        await ctx.send(f"{member.mention} can no longer speak in the help channels.")
        await self.logs.post_action_log(ctx.author, member, 'help-mute', reason=reason)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command(aliases=["timemutehelp"])
    async def timehelpmute(self, ctx: GuildContext, member: discord.Member, length: int = commands.parameter(converter=DateOrTimeToSecondsConverter), *, reason: Optional[str]):
        """Restricts a user from speaking in Assistance Channels for a limited period of time. Staff and Helpers only.\n\nLength format: #d#h#m#s"""
        if await check_bot_or_staff(ctx, member, "helpmute"):
            return
        delta = timedelta(seconds=length)
        timestamp = datetime.now(self.bot.tz)

        helpmute_expiration = timestamp + delta

        await self.restrictions.add_restriction(member, Restriction.HelpMute, reason, end_date=helpmute_expiration)

        await ctx.send(f"{member.mention} can no longer speak in the help channels.")
        await self.logs.post_action_log(ctx.author, member, 'help-mute', reason=reason, until=helpmute_expiration)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command()
    async def helpunmute(self, ctx: GuildContext, member: Union[discord.Member, discord.User], *, reason: Optional[str]):
        """Restores speak access to help channels. Helpers+ only."""
        await self.restrictions.remove_restriction(member, Restriction.HelpMute)
        await ctx.send(f"{member.mention} can now speak in the help channels again.")
        await self.logs.post_action_log(ctx.author, member, 'help-unmute', reason=reason)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command()
    async def takesmallhelp(self, ctx: GuildContext, members: commands.Greedy[discord.Member]):
        """Remove access to small help channel. Staff and Helpers only."""
        if len(members) < 1:
            await ctx.send("Mention at least one user")
            return
        for member in members:
            await member.remove_roles(self.bot.roles['Small Help'])
        await ctx.send(f"{', '.join(x.mention for x in members)} can no longer access the small help channel.")
        msg = f"⭕️ **Small help access revoked**: {ctx.author.mention} revoked access to small help channel from {', '.join(f'{x.mention} | {x}'for x in members)}"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command()
    async def givesmallhelp(self, ctx: GuildContext, members: commands.Greedy[discord.Member]):
        """Provide access to small help channel for 1-on-1 help. Staff and Helpers only."""
        if len(members) < 1:
            await ctx.send("Mention at least one user")
            return
        for member in members:
            await member.add_roles(self.bot.roles['Small Help'])
        await ctx.send(f"{', '.join(x.mention for x in members)} can access the small help channel.")
        msg = f"⭕️ **Small help access granted**: {ctx.author.mention} granted access to small help channel to {', '.join(f'{x.mention} | {x}'for x in members)}"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command()
    async def probate(self, ctx: GuildContext, member: Union[discord.Member, discord.User], *, reason: Optional[str]):
        """Probate a user. Staff and Helpers only."""
        if await check_bot_or_staff(ctx, member, "probate"):
            return
        await self.restrictions.add_restriction(member, Restriction.Probation, reason)
        await ctx.send(f"{member.mention} is now in probation.")
        await self.logs.post_action_log(ctx.author, member, 'probate', reason=reason)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command()
    async def unprobate(self, ctx: GuildContext, member: Union[discord.Member, discord.User], *, reason: Optional[str]):
        """Unprobate a user. Staff and Helpers only."""
        await self.restrictions.remove_restriction(member, Restriction.Probation)
        await ctx.send(f"{member.mention} is out of probation.")
        await self.logs.post_action_log(ctx.author, member, 'unprobate', reason=reason)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    @commands.command()
    async def banish(self, ctx: GuildContext, member: discord.Member, *, reason: Optional[str]):
        """Banishes a user to the retard chamber."""
        if await check_bot_or_staff(ctx, member, "banish"):
            return
        await self.bot.restrictions.add_restriction(member, Restriction.Banished, reason)
        await ctx.send(f"{member.mention} has been Banished!")
        await self.logs.post_action_log(ctx.author, member, 'banish', reason=reason)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    @commands.command()
    async def unbanish(self, ctx: GuildContext, member: Union[discord.Member, discord.User], *, reason: Optional[str]):
        """Unbanish a user."""
        await self.restrictions.remove_restriction(member, Restriction.Banished)
        await ctx.send(f"{member.mention} is unbanished.")
        await self.logs.post_action_log(ctx.author, member, 'unbanish', reason=reason)

    @is_staff("Owner")
    @commands.guild_only()
    @commands.command()
    async def updatechannel(self, ctx: GuildContext, name: str, channel: Union[discord.TextChannel, discord.VoiceChannel, discord.Thread]):
        """Changes the id of a channel"""
        if name not in self.bot.channels:
            await ctx.send("Invalid channel name!")
            return
        await self.bot.configuration.add_channel(name, channel)
        self.bot.channels[name] = channel
        await ctx.send(f"Changed {name} channel to {channel.mention} | {channel.id}")
        await self.bot.channels['mod-logs'].send(f"⚙ **Changed**: {ctx.author.mention} changed {name} channel to {channel.mention} | {channel.id}")

    @is_staff("Owner")
    @commands.guild_only()
    @commands.command()
    async def setmodchannel(self, ctx: GuildContext, channel: discord.TextChannel, value: bool):
        """Changes the mod flag of a channel"""
        # TODO FIX THIS, useless maybe
        db_channel = self.configuration.get_channel(channel.id)
        if not db_channel:
            await self.configuration.add_channel(channel.name, channel)
            db_channel = await self.configuration.get_channel(channel.id)
        await ctx.send(f"{channel.mention} is {'now' if value else 'no longer'} a mod channel.")

    @is_staff("OP")
    @commands.command()
    async def playing(self, ctx: KurisuContext, *, gamename):
        """Sets playing message. Staff only."""
        await self.bot.change_presence(activity=discord.Game(name=gamename))

    @is_staff("OP")
    @commands.command(aliases=['presence'])
    async def status(self, ctx: KurisuContext, status: str):
        """Sets the bot presence. Staff only.
        Valid statuses are `online`, `offline`, `idle`, `dnd` and `invisible`."""

        status_dict: dict[str, discord.Status] = {
            'online': discord.Status.online,
            'offline': discord.Status.offline,
            'idle': discord.Status.idle,
            'dnd': discord.Status.dnd,
            'invisible': discord.Status.invisible
        }
        if status in status_dict:
            await self.bot.change_presence(status=status_dict[status])
            await ctx.send(f"Changed status to {status} successfully.")
        else:
            await ctx.send_help(ctx.command)

    @is_staff("OP")
    @commands.command()
    async def username(self, ctx: KurisuContext, *, username: str):
        """Sets bot name. Staff only."""
        await self.bot.user.edit(username=username)

    @is_staff_app("Owner")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(file='Image to set as the new avatar.')
    @app_commands.command()
    async def avatar(self, interaction: discord.Interaction, file: discord.Attachment):
        """Sets bot avatar. Owner only"""

        if not file.content_type or file.content_type not in (
            "image/jpeg",
            "image/png",
            "image/gif",
        ):
            return await interaction.response.send_message(
                "File provided is not a valid image.", ephemeral=True
            )

        image_bytes = await file.read()
        try:
            await self.bot.user.edit(avatar=image_bytes)
        except ValueError:
            await interaction.response.send_message(
                "The image has a invalid format.", ephemeral=True
            )
        except discord.HTTPException as exc:
            embed = create_error_embed(interaction, exc)
            await interaction.response.send_message(
                "Failure to edit the bot's profile.",
                embed=embed,
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Profile picture changed successfully.", ephemeral=True
            )

    @is_staff("SuperOP")
    @commands.command()
    async def sync(self, ctx: KurisuContext):
        """Syncs app commands manually. SuperOP only"""
        await ctx.bot.tree.sync()
        await ctx.send("App commands synced!")

    @is_staff("SuperOP")
    @commands.guild_only()
    @commands.command()
    async def nofilter(self, ctx: GuildContext, channel: discord.TextChannel):
        """Adds nofilter to the channel"""
        if channel.id in self.configuration.nofilter_list:
            return await ctx.send("This channel is already no filtered!")
        await self.configuration.set_nofilter_channel(channel, False)
        await self.bot.channels['mod-logs'].send(f"⭕ **No filter**: {ctx.author.mention} added no filter to {channel.mention}")

    @is_staff("SuperOP")
    @commands.guild_only()
    @commands.command()
    async def filter(self, ctx: GuildContext, channel: discord.TextChannel):
        """Removes nofilter from the channel"""
        if channel.id not in self.configuration.nofilter_list:
            return await ctx.send("This channel is already filtered!")
        await self.configuration.set_nofilter_channel(channel, True)
        await self.bot.channels['mod-logs'].send(f"🚫 **Filter**: {ctx.author.mention} removed no filter from {channel.mention}")

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command()
    async def approve(self, ctx: GuildContext, alias: str, invite: discord.Invite, times: commands.Range[int, 1] = 1):
        """Approves a server invite for a number of times. Staff and Helpers only."""

        code = invite.code

        if self.filters.get_invite_named(alias):
            return await ctx.send("This alias is already in use.")
        if self.filters.approved_invites.get(code):
            return await ctx.send("This code is already in use.")

        await self.filters.add_approved_invite(invite, uses=times, alias=alias)
        await ctx.send(f"Approved an invite to {invite.guild}({code}) for posting {times} times")
        await self.bot.channels['mod-logs'].send(f"⭕ **Approved**: {ctx.author.mention} approved server {invite.guild}({code}) to be posted {times} times")

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command(aliases=['ci'])
    async def channelinfo(self, ctx: GuildContext, channel: discord.TextChannel = commands.CurrentChannel):
        """Shows database information about a text channel."""
        state = {0: "Not locked", 1: "softlocked", 2: "locked", 3: "super locked"}
        db_channel = await self.configuration.get_channel(channel.id)
        if db_channel is None:
            return await ctx.send("This channel is not in the database")
        embed = discord.Embed(title=db_channel.name)
        embed.add_field(name="ID", value=db_channel.id, inline=False)
        embed.add_field(name="Filtered", value=str(db_channel.filtered), inline=False)
        embed.add_field(name="Status", value=state[db_channel.lock_level], inline=False)
        await ctx.send(embed=embed)

    @is_staff("OP")
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    @commands.command()
    async def tempstream(self, ctx: GuildContext, member: discord.Member, length: str = "", *, reason: Optional[str]):
        """Gives temporary streaming permissions to a member. Lasts 24 hours by default"""
        await member.add_roles(self.bot.roles['streamer(temp)'])

        timestamp = datetime.now(self.bot.tz)
        seconds = parse_time(length) if length else 86400
        if seconds == -1:
            return await ctx.send("💢 I don't understand your time format.")

        delta = timedelta(seconds=seconds)
        expiring_time = timestamp + delta
        expiring_time_string = format_dt(expiring_time)
        res = await self.extras.add_timed_role(member, self.bot.roles['streamer(temp)'], expiring_time)
        if not res:
            return await ctx.send("Failed to add temporary stream permissions.")
        msg_user = f"You have been given streaming permissions until {expiring_time_string}!"
        await send_dm_message(member, msg_user, ctx)
        await ctx.send(f"{member.mention} has been given streaming permissions until {expiring_time_string}.")
        await self.logs.post_action_log(ctx.author, member, 'tempstream', reason=reason, until=expiring_time)

    @is_staff("OP")
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    @commands.command()
    async def notempstream(self, ctx: GuildContext, member: discord.Member, *, reason: Optional[str]):
        """Revokes temporary streaming permissions from a member."""

        await member.remove_roles(self.bot.roles['streamer(temp)'])
        res = await self.extras.delete_timed_role(member.id, self.bot.roles['streamer(temp)'].id)
        if not res:
            return await ctx.send("Failed to remove temporary role.")
        msg_user = "Your temporary streaming permissions have been revoked!"
        await send_dm_message(member, msg_user, ctx)
        await self.logs.post_action_log(ctx.author, member, 'no-tempstream', reason=reason)

    @is_staff_app("OP")
    @app_commands.default_permissions(ban_members=True)
    @app_commands.guild_only
    @app_commands.command()
    @app_commands.describe(member="Member to apply restriction.",
                           restriction="Restriction Type.",
                           length="Restriction length in ##d##m##ss format.",
                           reason="Reason for restriction")
    @app_commands.choices(restriction=[
        Choice(name='Take Embed Permissions', value='No-Embed',),
        Choice(name='Take Elsewhere access', value='No-elsewhere'),
        Choice(name='Take Meme commands access', value='No-Memes'),
        Choice(name='Take Art-channel access', value='No-art'),
        Choice(name='Mute in appeals', value='appeal-mute'),
        Choice(name='Mute in meta', value='meta-mute')
    ])
    async def giverestriction(self,
                              interaction: discord.Interaction,
                              member: discord.Member,
                              restriction: str,
                              length: app_commands.Transform[Optional[int], TimeTransformer] = None,
                              reason: Optional[str] = None):
        """Applies a restriction to a member. OP+ Only"""

        restriction_action = {'No-Embed': 'no-embed',
                              'No-elsewhere': 'take-elsewhere',
                              'No-Memes': 'take-memes',
                              'No-art': 'take-art',
                              'appeal-mute': 'appeals-mute',
                              'meta-mute': 'meta-mute'}

        if length:
            delta = timedelta(seconds=length)
            timestamp = datetime.now(self.bot.tz)
            end_time = timestamp + delta
        else:
            end_time = None

        await self.restrictions.add_restriction(member, Restriction(restriction), reason, end_date=end_time)
        await interaction.response.send_message(f"{member.mention} now has the {restriction} restriction role{f' until {format_dt(end_time)}.' if end_time else '.'}")
        await self.logs.post_action_log(interaction.user, member, restriction_action[restriction], reason=reason, until=end_time)


async def setup(bot):
    await bot.add_cog(Mod(bot))
