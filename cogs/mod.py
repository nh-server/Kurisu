import datetime
import discord
import re

from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from subprocess import call
from typing import Union
from utils import utils, crud, models
from utils.checks import is_staff, check_staff_id, check_bot_or_staff, is_staff_app


class Mod(commands.Cog):
    """
    Staff commands.
    """

    def __init__(self, bot):
        self.bot = bot
        self.userinfo_ctx = app_commands.ContextMenu(
                name='userinfo',
                callback=self.userinfo_ctx_menu,
                guild_ids=[886216686582263809]
        )
        self.bot.tree.add_command(self.userinfo_ctx)

    async def cog_unload(self):
        self.bot.tree.remove_command(self.userinfo_ctx.name, type=self.userinfo_ctx.type)

    @is_staff("Owner")
    @commands.command()
    async def quit(self, ctx):
        """Stops the bot."""
        await ctx.send("👋 Bye bye!")
        await self.bot.close()

    @is_staff("SuperOP")
    @commands.command()
    async def pull(self, ctx):
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
    async def userinfo(self, ctx, u: Union[discord.Member, discord.User]):
        """Shows information from a user. Staff and Helpers only."""
        basemsg = f"name = {u.name}\nid = {u.id}\ndiscriminator = {u.discriminator}\navatar = <{u.avatar}>\nbot = {u.bot}\ndefault_avatar= <{u.default_avatar}>\ncreated_at = {u.created_at}\n"
        if isinstance(u, discord.Member):
            role = u.top_role.name
            await ctx.send(f"{basemsg}display_name = {u.display_name}\njoined_at = {u.joined_at}\nstatus ={u.status}\nactivity = {u.activity.name if u.activity else None}\ncolour = {u.colour}\ntop_role = {role}\nguild_avatar= {f'<{u.guild_avatar}>' if u.guild_avatar else None}")
        else:
            try:
                ban = await ctx.guild.fetch_ban(u)
            except discord.NotFound:  # NotFound is raised if the user isn't banned
                ban = None
            await ctx.send(f"{basemsg}{f'**Banned**, reason: {ban.reason}' if ban is not None else ''}\n")

    @commands.guild_only()
    @commands.command(aliases=['ui2'])
    async def userinfo2(self, ctx, user: Union[discord.Member, discord.User] = commands.Author):
        """Shows information from a user. Staff and Helpers only."""

        if (not await check_staff_id('Helper', ctx.author.id)) and (ctx.author != user or ctx.channel != self.bot.channels['bot-cmds']):
            await ctx.message.delete()
            return await ctx.send(f"{ctx.author.mention} This command can only be used in {self.bot.channels['bot-cmds'].mention} and only on yourself.", delete_after=10)

        embed = discord.Embed(color=utils.gen_color(user.id))
        embed.description = (
            f"**User:** {user.mention}\n"
            f"**User's ID:** {user.id}\n"
            f"**Created on:** {utils.dtm_to_discord_timestamp(user.created_at, utc_time=True)} ({utils.dtm_to_discord_timestamp(user.created_at, date_format='R', utc_time=True)})\n"
            f"**Default Profile Picture:** {user.default_avatar}\n"
        )

        if isinstance(user, discord.Member):
            member_type = "member"
            embed.description += (
                f"**Join date:** {utils.dtm_to_discord_timestamp(user.joined_at, utc_time=True)} ({utils.dtm_to_discord_timestamp(user.joined_at, date_format='R', utc_time=True)})\n"
                f"**Current Status:** {user.status}\n"
                f"**User Activity:** {user.activity}\n"
                f"**Current Display Name:** {user.display_name}\n"
                f"**Nitro Boost Info:** {f'Boosting since {utils.dtm_to_discord_timestamp(user.premium_since, utc_time=True)}' if user.premium_since else 'Not a booster'}\n"
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
    async def userinfo_ctx_menu(self, interaction: discord.Interaction, user: discord.Member):
        embed = discord.Embed(color=utils.gen_color(user.id))
        embed.description = (
            f"**User:** {user.mention}\n"
            f"**User's ID:** {user.id}\n"
            f"**Created on:** {utils.dtm_to_discord_timestamp(user.created_at, utc_time=True)} ({utils.dtm_to_discord_timestamp(user.created_at, date_format='R', utc_time=True)})\n"
            f"**Default Profile Picture:** [link]({user.default_avatar})\n"
        )
        if isinstance(user, discord.Member):
            member_type = "member"
            embed.description += (
                f"**Join date:** {utils.dtm_to_discord_timestamp(user.joined_at, utc_time=True)} ({utils.dtm_to_discord_timestamp(user.joined_at, date_format='R', utc_time=True)})\n"
                f"**Current Status:** {user.status}\n"
                f"**User Activity:** {user.activity}\n"
                f"**Current Display Name:** {user.display_name}\n"
                f"**Nitro Boost Info:** {f'Boosting since {utils.dtm_to_discord_timestamp(user.premium_since, utc_time=True)}' if user.premium_since else 'Not a booster'}\n"
                f"**Current Top Role:** {user.top_role}\n"
                f"**Color:** {user.color}\n"
                f"**Profile Picture:** [link]({user.avatar.url})"
            )
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
    @commands.command()
    async def guildinfo(self, ctx, invite: discord.Invite):

        guild = invite.guild
        embed = discord.Embed(title=f"Guild {guild.name}", color=utils.gen_color(guild.id))
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.description = (
            f"**Guild's ID:** {guild.id}\n"
            f"**Created on:** {utils.dtm_to_discord_timestamp(guild.created_at, utc_time=True)} ({utils.dtm_to_discord_timestamp(guild.created_at, date_format='R', utc_time=True)})\n"
            f"**Verification level:** {guild.verification_level}\n"
            f"**Members:** {invite.approximate_member_count}\n"
            f"**Nitro boosters:** {guild.premium_subscription_count}\n"
        )

        if guild.vanity_url_code:
            embed.description += f"**Vanity url:** {guild.vanity_url_code}\n"
        if guild.icon:
            embed.description += f"**Icon:** [Link]({guild.icon.url})\n"
        if guild.banner:
            embed.description += f"**Banner:** [Link]({guild.banner.url})\n"

        await ctx.send(embed=embed)

    @commands.command()
    async def guildinfo2(self, ctx, invite: discord.Invite):

        guild = invite.guild
        embed = discord.Embed(title=f"Guild {guild.name}", color=utils.gen_color(guild.id))
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="ID", value=guild.id)
        embed.add_field(name="Created on", value=utils.dtm_to_discord_timestamp(guild.created_at, utc_time=True))
        embed.add_field(name="Verification", value=guild.verification_level)
        embed.add_field(name="Members", value=invite.approximate_member_count)
        embed.add_field(name="Nitro boosters", value=guild.premium_subscription_count)
        embed.add_field(name="Vanity url", value=guild.vanity_url_code)
        links = ""
        if guild.icon:
            links += f"[icon]({guild.icon.url}) "
        if guild.banner:
            links += f"[icon]({guild.banner.url})"
        if links:
            embed.add_field(name="Links", value=links)
        await ctx.send(embed=embed)

    @is_staff("Owner")
    @commands.guild_only()
    @commands.command(aliases=['gigayeet'])
    async def multiban(self, ctx, users: commands.Greedy[int]):
        """Multi-ban users."""
        author = ctx.author
        msg = "failed:\n"
        for m in users:
            try:
                await self.bot.guild.ban(discord.Object(id=m))
            except (discord.errors.NotFound, discord.errors.Forbidden) as e:
                msg += f"{m}:\n  {e.text}\n"
        paginator = utils.paginate_message(msg)
        for page in paginator.pages:
            await utils.send_dm_message(author, page)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def matchuser(self, ctx, *, rgx: str):
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
        file = utils.text_to_discord_file(msg, name="matches.txt")
        await ctx.send(f"Matched {matches} members.", file=file)

    @is_staff("Owner")
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.command(aliases=['gigayeetre'])
    async def multibanre(self, ctx, *, rgx: str):
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
        file = utils.text_to_discord_file(msg, name="banned.txt")
        await ctx.send(f"Banned {banned} members.", file=file)

    class ChannelorTime(commands.Converter):
        async def convert(self, ctx, arg: str):
            try:
                return ctx.bot.get_channel(int(arg))
            except ValueError:
                time = utils.parse_time(arg)
                if time != -1:
                    return time
            raise commands.BadArgument("Invalid channel id or time format.")

    @is_staff("Helper")
    @commands.bot_has_permissions(manage_channels=True)
    @commands.guild_only()
    @commands.command()
    async def slowmode(self, ctx, arg: Union[discord.TextChannel, int] = commands.parameter(converter=ChannelorTime), length: int = commands.parameter(converter=utils.TimeConverter, default=None)):
        """Apply a given slowmode time to a channel.

        The time format is identical to that used for timed kicks/bans/takehelps.
        It is not possible to set a slowmode longer than 6 hours.

        Helpers in assistance channels and Staff only."""

        if isinstance(arg, discord.TextChannel):
            channel = arg
            if length is None:
                return await ctx.send_help(ctx.command)
        else:
            channel = ctx.channel
            length = arg

        if channel not in self.bot.assistance_channels and not await check_staff_id("OP", ctx.author.id):
            return await ctx.send("You cannot use this command outside of assistance channels.")

        if length > 21600:
            return await ctx.send("💢 You can't slowmode a channel for longer than 6 hours!")

        try:
            await channel.edit(slowmode_delay=length)
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
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @commands.command(aliases=["clear"])
    async def purge(self, ctx, limit: int):
        """Clears a given number of messages. Helpers in assistance channels and Staff only."""
        deleted = await ctx.channel.purge(limit=limit + 1, check=lambda message: not message.pinned)
        msg = f"🗑 **Cleared**: {ctx.author.mention} cleared {len(deleted)} messages in {ctx.channel.mention}"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def metamute(self, ctx, member: discord.Member, *, reason=""):
        """Mutes a user so they can't speak in meta. Staff only."""
        if not await crud.add_permanent_role(member.id, self.bot.roles['meta-mute'].id):
            await ctx.send("User is already meta muted!")
            return
        await member.add_roles(self.bot.roles['meta-mute'])
        msg_user = "You were meta muted!"
        if reason != "":
            msg_user += " The given reason is: " + reason
        await utils.send_dm_message(member, msg_user, ctx)
        await ctx.send(f"{member.mention} can no longer speak in meta.")
        msg = f"🔇 **Meta muted**: {ctx.author.mention} meta muted {member.mention} | {self.bot.escape_text(member)}"
        signature = utils.command_signature(ctx.command)
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        else:
            msg += f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user."
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    @commands.command()
    async def metaunmute(self, ctx, member: discord.Member):
        """Unmutes a user so they can speak in meta. Staff only."""
        try:
            if not await crud.remove_permanent_role(member.id, self.bot.roles["meta-mute"].id) and self.bot.roles['meta-mute'] not in member.roles:
                return await ctx.send("This user is not meta muted!")
            await member.remove_roles(self.bot.roles['meta-mute'])
            await ctx.send(f"{member.mention} can now speak in meta again.")
            msg = f"🔈 **Meta unmuted**: {ctx.author.mention} meta unmuted {member.mention} | {self.bot.escape_text(member)}"
            await self.bot.channels['mod-logs'].send(msg)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def appealmute(self, ctx, member: discord.Member, *, reason=""):
        """Mutes a user so they can't speak in appeals. Staff only."""
        if not await crud.add_permanent_role(member.id, self.bot.roles['appeal-mute'].id):
            await ctx.send("User is already appeal muted!")
            return
        await member.add_roles(self.bot.roles['appeal-mute'])
        msg_user = "You were appeal muted!"
        if reason != "":
            msg_user += " The given reason is: " + reason
        await utils.send_dm_message(member, msg_user, ctx)
        await ctx.send(f"{member.mention} can no longer speak in appeals.")
        msg = f"🔇 **appeal muted**: {ctx.author.mention} appeal muted {member.mention} | {self.bot.escape_text(member)}"
        signature = utils.command_signature(ctx.command)
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        else:
            msg += f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user."
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    @commands.command()
    async def appealunmute(self, ctx, member: discord.Member):
        """Unmutes a user so they can speak in appeals. Staff only."""
        try:
            if not await crud.remove_permanent_role(member.id, self.bot.roles["appeal-mute"].id) and self.bot.roles['appeal-mute'] not in member.roles:
                return await ctx.send("This user is not appeal muted!")
            await member.remove_roles(self.bot.roles['appeal-mute'])
            await ctx.send(f"{member.mention} can now speak in appeals again.")
            msg = f"🔈 **appeal unmuted**: {ctx.author.mention} appeal unmuted {member.mention} | {self.bot.escape_text(member)}"
            await self.bot.channels['mod-logs'].send(msg)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    @commands.command()
    async def mute(self, ctx, member: discord.Member, *, reason=""):
        """Mutes a user so they can't speak. Staff only."""
        if await check_bot_or_staff(ctx, member, "mute"):
            return
        if not await crud.add_permanent_role(member.id, self.bot.roles['Muted'].id):
            # Check if the user has a timed restriction.
            # If there is one, this will convert it to a permanent one.
            # If not, it will display that it was already taken.
            if not await crud.get_time_restriction_by_user_type(member.id, 'timemute'):
                return await ctx.send("User is already muted!")
            else:
                await crud.remove_timed_restriction(member.id, 'timemute')
        await member.add_roles(self.bot.roles['Muted'])
        await member.remove_roles(self.bot.roles['#elsewhere'], self.bot.roles['#art-discussion'])
        msg_user = "You were muted!"
        if reason != "":
            msg_user += " The given reason is: " + reason
        await utils.send_dm_message(member, msg_user, ctx)
        await ctx.send(f"{member.mention} can no longer speak.")
        msg = f"🔇 **Muted**: {ctx.author.mention} muted {member.mention} | {self.bot.escape_text(member)}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        else:
            signature = utils.command_signature(ctx.command)
            msg += f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user."
        await self.bot.channels['mod-logs'].send(msg)
        # change to permanent mute

    @is_staff("HalfOP")
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    @commands.command()
    async def oldtimemute(self, ctx, member: discord.Member, length: int = commands.parameter(converter=utils.TimeConverter), *, reason=""):
        """Mutes a user for a limited period of time so they can't speak. Staff only.\n\nLength format: #d#h#m#s"""
        if await check_bot_or_staff(ctx, member, "mute"):
            return
        await member.add_roles(self.bot.roles['Muted'])
        await member.remove_roles(self.bot.roles['#elsewhere'], self.bot.roles['#art-discussion'])

        issuer = ctx.author

        timestamp = datetime.datetime.now()
        delta = datetime.timedelta(seconds=length)
        unmute_time = timestamp + delta
        unmute_time_string = utils.dtm_to_discord_timestamp(unmute_time)

        old_mute = await crud.get_time_restriction_by_user_type(member.id, 'timemute')
        await crud.add_timed_restriction(member.id, unmute_time, 'timemute')
        await crud.add_permanent_role(member.id, self.bot.roles['Muted'].id)
        msg_user = "You were muted!"
        if reason != "":
            msg_user += " The given reason is: " + reason
        msg_user += f"\n\nThis mute lasts until {unmute_time_string}."
        await utils.send_dm_message(member, msg_user, ctx)
        signature = utils.command_signature(ctx.command)
        if not old_mute:
            await ctx.send(f"{member.mention} can no longer speak.")
            msg = f"🔇 **Timed mute**: {issuer.mention} muted {member.mention}| {self.bot.escape_text(member)} for {delta}, until {unmute_time_string} "
        else:
            await ctx.send(f"{member.mention} mute was updated.")
            msg = f"🔇 **Timed mute**: {issuer.mention} updated {member.mention}| {self.bot.escape_text(member)} time mute from {utils.dtm_to_discord_timestamp(old_mute.end_date)} until {unmute_time_string}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        else:
            msg += f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user."
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def unmute(self, ctx, member: discord.Member):
        """Unmutes a user so they can speak. Staff only."""
        try:
            if not await crud.remove_permanent_role(member.id, self.bot.roles["Muted"].id):
                return await ctx.send("This user is not muted")
            await member.remove_roles(self.bot.roles['Muted'])
            await ctx.send(f"{member.mention} can now speak again.")
            msg = f"🔈 **Unmuted**: {ctx.author.mention} unmuted {member.mention} | {self.bot.escape_text(member)}"
            await self.bot.channels['mod-logs'].send(msg)
            await crud.remove_timed_restriction(member.id, 'timemute')
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.command(aliases=['timemute'])
    async def timeout(self, ctx, member: discord.Member, length: int = commands.parameter(converter=utils.TimeConverter), *, reason: str = None):
        """Times out a user. Staff only.\n\nLength format: #d#h#m#s"""
        if await check_bot_or_staff(ctx, member, "timeout"):
            return
        if length > 2419200:  # Timeout time can't be more than 28 days
            return await ctx.send("Timeouts can't be longer than 28 days!")

        issuer = ctx.author
        timeout_expiration = discord.utils.utcnow() + datetime.timedelta(seconds=length)
        timeout_expiration_str = utils.dtm_to_discord_timestamp(timeout_expiration, utc_time=True)
        await member.timeout(timeout_expiration, reason=reason)

        msg_user = "You were given a timeout!"
        if reason is not None:
            msg_user += " The given reason is: " + reason
        msg_user += f"\n\nThis timeout lasts until {timeout_expiration_str}."
        await utils.send_dm_message(member, msg_user, ctx)

        signature = utils.command_signature(ctx.command)
        await ctx.send(f"{member.mention} has been given a timeout.")

        msg = f"🔇 **Timeout**: {issuer.mention} timed out {member.mention}| {self.bot.escape_text(member)} until {timeout_expiration_str}."
        if reason is not None:
            msg += "\n✏️ __Reason__: " + reason
        else:
            msg += f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user."
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("HalfOP")
    @commands.command()
    async def untimeout(self, ctx, member: discord.Member):
        """Removes a timeout from a user. Staff only."""
        if member.timed_out_until is None:
            return await ctx.send("This member doesn't have a timeout!")
        await member.timeout(None)
        await ctx.send(f"{member.mention} timeout was removed.")
        msg = f"🔈 **Timeout Removed**: {ctx.author.mention} removed timeout from {member.mention} | {self.bot.escape_text(member)}"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("HalfOP")
    @commands.command()
    async def art(self, ctx, member: discord.Member):
        """Restore art-discussion access for a user. Staff only."""
        if not await crud.remove_permanent_role(member.id, self.bot.roles['No-art'].id):
            return await ctx.send("This user is not restricted from art channels.")
        try:
            await member.remove_roles(self.bot.roles['No-art'])
        except discord.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
        await ctx.send(f"{member.mention} can access art-discussion again.")
        msg = f"⭕️ **Restored art**: {ctx.message.author.mention} restored art access to {member.mention} | {self.bot.escape_text(member)}"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("HalfOP")
    @commands.command()
    async def noart(self, ctx, member: discord.Member, *, reason=""):
        """Removes art-discussion access from a user. Staff only."""
        if not await crud.add_permanent_role(member.id, self.bot.roles['No-art'].id):
            return await ctx.send("This user is already restricted from art channels.")
        try:
            await member.add_roles(self.bot.roles['No-art'])
        except discord.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
        await ctx.send(f"{member.mention} can no longer access art-discussion.")
        msg = f"🚫 **Removed art**: {ctx.message.author.mention} removed art access from {member.mention} | {self.bot.escape_text(member)}"
        signature = utils.command_signature(ctx.command)
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        else:
            msg += f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user."
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def elsewhere(self, ctx, member: discord.Member):
        """Restore elsewhere access for a user. Staff only."""
        try:
            if not await crud.remove_permanent_role(member.id, self.bot.roles["No-elsewhere"].id):
                return await ctx.send("This user is not restricted from elsewhere!")
            await member.remove_roles(self.bot.roles['No-elsewhere'])
            await ctx.send(f"{member.mention} can access elsewhere again.")
            msg = f"⭕️ **Restored elsewhere**: {ctx.author.mention} restored elsewhere access to {member.mention} | {self.bot.escape_text(member)}"
            await self.bot.channels['mod-logs'].send(msg)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def noelsewhere(self, ctx, member: discord.Member, *, reason=""):
        """Removes elsewhere access from a user. Staff only."""
        try:
            if not await crud.add_permanent_role(member.id, self.bot.roles['No-elsewhere'].id):
                return await ctx.send("This user is already restricted from elsewhere!")
            await member.add_roles(self.bot.roles['No-elsewhere'])
            await member.remove_roles(self.bot.roles['#elsewhere'])
            await ctx.send(f"{member.mention} can no longer access elsewhere.")
            msg = f"🚫 **Removed elsewhere**: {ctx.author.mention} removed elsewhere access from {member.mention} | {self.bot.escape_text(member)}"
            signature = utils.command_signature(ctx.command)
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            else:
                msg += f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user."
            await self.bot.channels['mod-logs'].send(msg)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def noembed(self, ctx, member: discord.Member, *, reason=""):
        """Removes embed permissions from a user. Staff only."""
        if await check_bot_or_staff(ctx, member, "noembed"):
            return
        try:
            await crud.add_permanent_role(member.id, self.bot.roles['No-Embed'].id)
            await member.add_roles(self.bot.roles['No-Embed'])
            msg_user = "You lost embed and upload permissions!"
            if reason != "":
                msg_user += " The given reason is: " + reason
            msg_user += f"\n\nIf you feel this was unjustified, you may appeal in {self.bot.channels['appeals'].mention}"
            await utils.send_dm_message(member, msg_user, ctx)
            await ctx.send(f"{member.mention} can no longer embed links or attach files.")
            msg = f"🚫 **Removed Embed**: {ctx.author.mention} removed embed from {member.mention} | {self.bot.escape_text(member)}"
            signature = utils.command_signature(ctx.command)
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            else:
                msg += f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user."
            await self.bot.channels['mod-logs'].send(msg)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def embed(self, ctx, member: discord.Member):
        """Restore embed permissions for a user. Staff only."""
        try:
            await crud.remove_permanent_role(member.id, self.bot.roles["No-Embed"].id)
            await member.remove_roles(self.bot.roles['No-Embed'])
            await ctx.send(f"{member.mention} can now embed links and attach files again.")
            msg = f"⭕️ **Restored Embed**: {ctx.author.mention} restored embed to {member.mention} | {self.bot.escape_text(member)}"
            await self.bot.channels['mod-logs'].send(msg)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command(aliases=["nohelp", "yesnthelp"])
    async def takehelp(self, ctx, member: Union[discord.Member, discord.User], *, reason=""):
        """Remove access to the assistance channels. Staff and Helpers only."""
        if await check_bot_or_staff(ctx, member, "takehelp"):
            return
        if not await crud.add_permanent_role(member.id, self.bot.roles['No-Help'].id):
            # Check if the user has a timed restriction.
            # If there is one, this will convert it to a permanent one.
            # If not, it will display that it was already taken.
            if not await crud.get_time_restriction_by_user_type(member.id, 'timenohelp'):
                return await ctx.send("This user's help is already taken!")
            else:
                await crud.remove_timed_restriction(member.id, 'timenohelp')
        if isinstance(member, discord.Member):
            await member.add_roles(self.bot.roles['No-Help'])
            msg_user = "You lost access to help channels!"
            if reason != "":
                msg_user += " The given reason is: " + reason
            msg_user += f"\n\nIf you feel this was unjustified, you may appeal in {self.bot.channels['appeals'].mention}"
            await utils.send_dm_message(member, msg_user, ctx)
        await ctx.send(f"{member.mention} can no longer access the help channels.")
        msg = f"🚫 **Help access removed**: {ctx.author.mention} removed access to help channels from {member.mention} | {self.bot.escape_text(member)}"
        signature = utils.command_signature(ctx.command)
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        else:
            msg += f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user."
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command(aliases=["yeshelp"])
    async def givehelp(self, ctx, member: Union[discord.Member, discord.User]):
        """Restore access to the assistance channels. Staff and Helpers only."""
        if not await crud.remove_permanent_role(member.id, self.bot.roles["No-Help"].id):
            return await ctx.send("This user is not take-helped!")
        if isinstance(member, discord.Member):
            try:
                await member.remove_roles(self.bot.roles['No-Help'])
            except discord.errors.Forbidden:
                await ctx.send("💢 I don't have permission to do this.")
        await ctx.send(f"{member.mention} can access the help channels again.")
        msg = f"⭕️ **Help access restored**: {ctx.author.mention} restored access to help channels to {member.mention} | {self.bot.escape_text(member)}"
        await self.bot.channels['mod-logs'].send(msg)
        await crud.remove_timed_restriction(member.id, 'timenohelp')

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command(aliases=["timenohelp"])
    async def timetakehelp(self, ctx, member: discord.Member, length: int = commands.parameter(converter=utils.TimeConverter), *, reason=""):
        """Restricts a user from Assistance Channels for a limited period of time. Staff and Helpers only.\n\nLength format: #d#h#m#s"""
        if await check_bot_or_staff(ctx, member, "takehelp"):
            return
        issuer = ctx.author

        delta = datetime.timedelta(seconds=length)
        timestamp = datetime.datetime.now()

        unnohelp_time = timestamp + delta
        unnohelp_time_string = utils.dtm_to_discord_timestamp(unnohelp_time)

        await crud.add_timed_restriction(member.id, unnohelp_time, 'timenohelp')
        await crud.add_permanent_role(member.id, self.bot.roles['No-Help'].id)
        await member.add_roles(self.bot.roles['No-Help'])
        msg_user = "You lost access to help channels temporarily!"
        if reason != "":
            msg_user += " The given reason is: " + reason
        msg_user += f"\n\nIf you feel this was unjustified, you may appeal in {self.bot.channels['appeals'].mention}"
        msg_user += f"\n\nThis restriction lasts until {unnohelp_time_string}."
        await utils.send_dm_message(member, msg_user, ctx)
        await ctx.send(f"{member.mention} can no longer speak in Assistance Channels.")
        signature = utils.command_signature(ctx.command)
        msg = f"🚫 **Timed No-Help**: {issuer.mention} restricted {member.mention} for {delta}, until {unnohelp_time_string} | {self.bot.escape_text(member)}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        else:
            msg += f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user."
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command(aliases=["notech", "technt"])
    async def taketech(self, ctx, member: Union[discord.Member, discord.User], *, reason=""):
        """Remove access to the tech channel. Staff and Helpers only."""
        if await check_bot_or_staff(ctx, member, "taketech"):
            return
        if not await crud.add_permanent_role(member.id, self.bot.roles['No-Tech'].id):
            # Check if the user has a timed restriction.
            # If there is one, this will convert it to a permanent one.
            # If not, it will display that it was already taken.
            if not await crud.get_time_restriction_by_user_type(member.id, 'timenotech'):
                return await ctx.send("This user's tech is already taken!")
            else:
                await crud.remove_timed_restriction(member.id, 'timenotech')
        if isinstance(member, discord.Member):
            await member.add_roles(self.bot.roles['No-Tech'])
            msg_user = "You lost access to the tech channel!"
            if reason != "":
                msg_user += " The given reason is: " + reason
            msg_user += f"\n\nIf you feel this was unjustified, you may appeal in {self.bot.channels['appeals'].mention}"
            await utils.send_dm_message(member, msg_user, ctx)
        await ctx.send(f"{member.mention} can no longer access the tech channel.")
        msg = f"🚫 **Help access removed**: {ctx.author.mention} removed access to tech channel from {member.mention} | {self.bot.escape_text(member)}"
        signature = utils.command_signature(ctx.command)
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        else:
            msg += f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user."
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command(aliases=["yestech"])
    async def givetech(self, ctx, member: Union[discord.Member, discord.User]):
        """Restore access to the tech channel. Staff and Helpers only."""
        if not await crud.remove_permanent_role(member.id, self.bot.roles["No-Tech"].id):
            return await ctx.send("This user is not take-helped!")
        if isinstance(member, discord.Member):
            try:
                await member.remove_roles(self.bot.roles['No-Tech'])
            except discord.errors.Forbidden:
                await ctx.send("💢 I don't have permission to do this.")
        await ctx.send(f"{member.mention} can access the tech channel again.")
        msg = f"⭕️ **Help access restored**: {ctx.author.mention} restored access to tech channel to {member.mention} | {self.bot.escape_text(member)}"
        await self.bot.channels['mod-logs'].send(msg)
        await crud.remove_timed_restriction(member.id, 'timenotech')

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command(aliases=["timenotech"])
    async def timetaketech(self, ctx, member: discord.Member, length: int = commands.parameter(converter=utils.TimeConverter), *, reason=""):
        """Restricts a user from the tech channel for a limited period of time. Staff and Helpers only.\n\nLength format: #d#h#m#s"""
        if await check_bot_or_staff(ctx, member, "taketech"):
            return
        issuer = ctx.author

        delta = datetime.timedelta(seconds=length)
        timestamp = datetime.datetime.now()

        unnotech_time = timestamp + delta
        unnotech_time_string = utils.dtm_to_discord_timestamp(unnotech_time)

        await crud.add_timed_restriction(member.id, unnotech_time, 'timenotech')
        await crud.add_permanent_role(member.id, self.bot.roles['No-Tech'].id)
        await member.add_roles(self.bot.roles['No-Tech'])
        msg_user = "You lost access to the tech channel temporarily!"
        if reason != "":
            msg_user += " The given reason is: " + reason
        msg_user += f"\n\nIf you feel this was unjustified, you may appeal in {self.bot.channels['appeals'].mention}"
        msg_user += f"\n\nThis restriction lasts until {unnotech_time_string}."
        await utils.send_dm_message(member, msg_user, ctx)
        await ctx.send(f"{member.mention} can no longer speak in the tech channel.")
        signature = utils.command_signature(ctx.command)
        msg = f"🚫 **Timed No-Tech**: {issuer.mention} restricted {member.mention} for {delta}, until {unnotech_time_string} | {self.bot.escape_text(member)}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        else:
            msg += f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user."
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command(aliases=["mutehelp"])
    async def helpmute(self, ctx, member: Union[discord.Member, discord.User], *, reason=""):
        """Remove speak perms to the assistance channels. Staff and Helpers only."""
        if await check_bot_or_staff(ctx, member, "helpmute"):
            return
        if not await crud.add_permanent_role(member.id, self.bot.roles['help-mute'].id):
            if not await crud.get_time_restriction_by_user_type(member.id, 'timehelpmute'):
                return await ctx.send("This user is already helpmuted!")
            else:
                await crud.remove_timed_restriction(member.id, 'timehelpmute')
        if isinstance(member, discord.Member):
            await member.add_roles(self.bot.roles['help-mute'])
            msg_user = "You were muted in the help channels!"
            if reason != "":
                msg_user += " The given reason is: " + reason
            msg_user += f"\n\nIf you feel this was unjustified, you may appeal in {self.bot.channels['appeals'].mention}"
            await utils.send_dm_message(member, msg_user, ctx)
        await ctx.send(f"{member.mention} can no longer speak in the help channels.")
        msg = f"🚫 **Help mute**: {ctx.author.mention} removed speak access in help channels from {member.mention} | {self.bot.escape_text(member)}"
        signature = utils.command_signature(ctx.command)
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        else:
            msg += f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user."
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command(aliases=["timemutehelp"])
    async def timehelpmute(self, ctx, member: discord.Member, length: int = commands.parameter(converter=utils.TimeConverter), *, reason=""):
        """Restricts a user from speaking in Assistance Channels for a limited period of time. Staff and Helpers only.\n\nLength format: #d#h#m#s"""
        if await check_bot_or_staff(ctx, member, "helpmute"):
            return
        issuer = ctx.author

        delta = datetime.timedelta(seconds=length)
        timestamp = datetime.datetime.now()

        unhelpmute_time = timestamp + delta
        unhelpmute_time_string = utils.dtm_to_discord_timestamp(unhelpmute_time)

        await crud.add_timed_restriction(member.id, unhelpmute_time, 'timehelpmute')
        await crud.add_permanent_role(member.id, self.bot.roles['help-mute'].id)
        await member.add_roles(self.bot.roles['help-mute'])
        msg_user = "You lost send access to help channels temporarily!"
        if reason != "":
            msg_user += " The given reason is: " + reason
        msg_user += f"\n\nIf you feel this was unjustified, you may appeal in {self.bot.channels['appeals'].mention}"
        msg_user += f"\n\nThis restriction lasts until {unhelpmute_time_string}."
        await utils.send_dm_message(member, msg_user, ctx)
        await ctx.send(f"{member.mention} can no longer speak in the help channels.")
        signature = utils.command_signature(ctx.command)
        msg = f"🚫 **Timed Help mute**: {issuer.mention} help muted {member.mention} for {delta}, until {unhelpmute_time_string} | {self.bot.escape_text(member)}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        else:
            msg += f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user."
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command()
    async def helpunmute(self, ctx, member: Union[discord.Member, discord.User]):
        """Restores speak access to help channels. Helpers+ only."""
        if not await crud.remove_permanent_role(member.id, self.bot.roles["help-mute"].id):
            return await ctx.send("This user is not help muted!")
        if isinstance(member, discord.Member):
            try:
                await member.remove_roles(self.bot.roles['help-mute'])
            except discord.errors.Forbidden:
                await ctx.send("💢 I don't have permission to do this.")
        await crud.remove_timed_restriction(member.id, 'timehelpmute')
        await ctx.send(f"{member.mention} can now speak in the help channels again.")
        msg = f"⭕ **Help unmuted**: {ctx.author.mention} help unmuted {member.mention} | {self.bot.escape_text(member)}"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command()
    async def takesmallhelp(self, ctx, members: commands.Greedy[discord.Member]):
        """Remove access to small help channel. Staff and Helpers only."""
        if len(members) < 1:
            await ctx.send("Mention at least one user")
            return
        for member in members:
            await member.remove_roles(self.bot.roles['Small Help'])
        await ctx.send(f"{', '.join([x.mention for x in members])} can no longer access the small help channel.")
        msg = f"⭕️ **Small help access revoked**: {ctx.author.mention} revoked access to small help channel from {', '.join([f'{x.mention} | {x}'for x in members])}"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command()
    async def givesmallhelp(self, ctx, members: commands.Greedy[discord.Member]):
        """Provide access to small help channel for 1-on-1 help. Staff and Helpers only."""
        if len(members) < 1:
            await ctx.send("Mention at least one user")
            return
        for member in members:
            await member.add_roles(self.bot.roles['Small Help'])
        await ctx.send(f"{', '.join([x.mention for x in members])} can access the small help channel.")
        msg = f"⭕️ **Small help access granted**: {ctx.author.mention} granted access to small help channel to {', '.join([f'{x.mention} | {x}'for x in members])}"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command()
    async def probate(self, ctx, member: Union[discord.Member, discord.User], *, reason=""):
        """Probate a user. Staff and Helpers only."""
        if await check_bot_or_staff(ctx, member, "probate"):
            return
        if not await crud.add_permanent_role(member.id, self.bot.roles['Probation'].id):
            return await ctx.send("This user is already probated!")
        if isinstance(member, discord.Member):
            await member.add_roles(self.bot.roles['Probation'])
            msg_user = "You are under probation!"
            if reason != "":
                msg_user += " The given reason is: " + reason
            await utils.send_dm_message(member, msg_user, ctx)
        await ctx.send(f"{member.mention} is now in probation.")
        msg = f"🚫 **Probated**: {ctx.author.mention} probated {member.mention} | {self.bot.escape_text(member)}"
        signature = utils.command_signature(ctx.command)
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        else:
            msg += f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user."
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command()
    async def unprobate(self, ctx, member: Union[discord.Member, discord.User]):
        """Unprobate a user. Staff and Helpers only."""
        if not await crud.remove_permanent_role(member.id, self.bot.roles["Probation"].id) and self.bot.roles["Probation"] not in member.roles:
            return await ctx.send("This user is not probated!")
        if isinstance(member, discord.Member):
            await member.remove_roles(self.bot.roles['Probation'])
        await ctx.send(f"{member.mention} is out of probation.")
        msg = f"⭕️ **Un-probated**: {ctx.author.mention} un-probated {member.mention} | {self.bot.escape_text(member)}"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("Owner")
    @commands.guild_only()
    @commands.command()
    async def updatechannel(self, ctx, name, channel: Union[discord.TextChannel, discord.VoiceChannel]):
        """Changes the id of a channel"""
        if name not in self.bot.channels:
            await ctx.send("Invalid channel name!")
            return
        await models.Channel.update.values(id=channel.id).where(models.Channel.name == name).gino.status()
        self.bot.channels[name] = channel
        await ctx.send(f"Changed {name} channel to {channel.mention} | {channel.id}")
        await self.bot.channels['server-logs'].send(f"⚙ **Changed**: {ctx.author.mention} changed {name} channel to {channel.mention} | {channel.id}")

    @is_staff("Owner")
    @commands.guild_only()
    @commands.command()
    async def setmodchannel(self, ctx, channel: discord.TextChannel, value: bool):
        """Changes the mod flag of a channel"""
        dbchannel = await crud.get_dbchannel(channel.id)
        await dbchannel.update(mod_channel=value).apply()
        await ctx.send(f"{channel.mention} is {'now' if value else 'no longer'} a mod channel.")

    @is_staff("OP")
    @commands.command()
    async def playing(self, ctx, *, gamename):
        """Sets playing message. Staff only."""
        await self.bot.change_presence(activity=discord.Game(name=gamename))

    @is_staff("OP")
    @commands.command()
    async def status(self, ctx, status):
        """Sets status. Staff only."""
        if status == "online":
            await self.bot.change_presence(status=discord.Status.online)
        elif status == "offline":
            await self.bot.change_presence(status=discord.Status.offline)
        elif status == "idle":
            await self.bot.change_presence(status=discord.Status.idle)
        elif status == "dnd":
            await self.bot.change_presence(status=discord.Status.dnd)
        elif status == "invisible":
            await self.bot.change_presence(status=discord.Status.invisible)

    @is_staff("OP")
    @commands.command()
    async def username(self, ctx, *, username):
        """Sets bot name. Staff only."""
        await self.bot.user.edit(username=username)

    @is_staff("SuperOP")
    @commands.guild_only()
    @commands.command()
    async def nofilter(self, ctx, channel: discord.TextChannel):
        """Adds nofilter to the channel"""
        if await crud.check_nofilter(channel):
            return await ctx.send("This channel is already no filtered!")
        await crud.add_nofilter(channel)
        await self.bot.channels['mod-logs'].send(f"⭕ **No filter**: {ctx.author.mention} added no filter to {channel.mention}")

    @is_staff("SuperOP")
    @commands.guild_only()
    @commands.command()
    async def filter(self, ctx, channel: discord.TextChannel):
        """Removes nofilter from the channel"""
        if not await crud.check_nofilter(channel):
            return await ctx.send("This channel is already filtered!")
        await crud.remove_nofilter(channel)
        await self.bot.channels['mod-logs'].send(f"🚫 **Filter**: {ctx.author.mention} removed no filter from {channel.mention}")

    @is_staff("Helper")
    @commands.guild_only()
    @commands.command()
    async def approve(self, ctx, alias: str, invite: discord.Invite, times: int = 1):
        """Approves a server invite for a number of times. Staff and Helpers only."""

        code = invite.code

        if await self.bot.invitefilter.fetch_invite_by_alias(alias) or await self.bot.invitefilter.fetch_invite_by_code(code):
            return await ctx.send("This code or alias is already in use!")

        if times < 1:
            return await ctx.send("The invite must be approved for a number of times higher than 0")

        await self.bot.invitefilter.add(code=code, alias=alias, uses=times)
        await ctx.send(f"Approved an invite to {invite.guild}({code}) for posting {times} times")
        await self.bot.channels['mod-logs'].send(f"⭕ **Approved**: {ctx.author.mention} approved server {invite.guild}({code}) to be posted {times} times")

    @is_staff("SuperOP")
    @commands.command(aliases=['setrole', 'scr'])
    async def setchannelrole(self, ctx, channel: discord.TextChannel, role: discord.Role):
        """Sets the default role of a channel."""
        dbchannel = await models.Channel.get(channel.id)
        if not dbchannel:
            dbchannel = await crud.add_dbchannel(channel.id, channel.name)
        if not await models.Role.get(role.id):
            await crud.add_dbrole(role.id, role.name)
        await dbchannel.update(default_role=role.id).apply()
        await ctx.send("Parameter updated succesfully")

    @is_staff("Helper")
    @commands.command(aliases=['ci'])
    async def channelinfo(self, ctx, channel: discord.TextChannel = commands.CurrentChannel):
        """Shows database information about a text channel."""
        state = {0: "Not locked", 1: "softlocked", 2: "locked", 3: "super locked"}
        dbchannel = await models.Channel.get(channel.id)
        if not dbchannel:
            return await ctx.send("This channel is not in the database")
        role = await crud.get_dbrole(dbchannel.default_role) if dbchannel.default_role else ctx.guild.default_role
        embed = discord.Embed(title=dbchannel.name)
        embed.add_field(name="ID", value=dbchannel.id, inline=False)
        embed.add_field(name="Default Role", value=role.name, inline=False)
        embed.add_field(name="Filtered", value=str(not dbchannel.nofilter), inline=False)
        embed.add_field(name="Status", value=state[dbchannel.lock_level], inline=False)
        await ctx.send(embed=embed)

    @is_staff("OP")
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    @commands.command()
    async def tempstream(self, ctx, member: discord.Member, length: str = ""):
        """Gives temporary streaming permissions to a member. Lasts 24 hours by default"""
        await member.add_roles(self.bot.roles['streamer(temp)'])

        timestamp = datetime.datetime.now()
        seconds = utils.parse_time(length) if length else 86400
        if seconds == -1:
            return await ctx.send("💢 I don't understand your time format.")

        delta = datetime.timedelta(seconds=seconds)
        expiring_time = timestamp + delta
        expiring_time_string = utils.dtm_to_discord_timestamp(expiring_time)

        await crud.add_timed_role(member.id, self.bot.roles['streamer(temp)'].id, expiring_time)
        msg_user = f"You have been given streaming permissions until {expiring_time_string}!"
        await utils.send_dm_message(member, msg_user, ctx)
        await ctx.send(f"{member.mention} has been given streaming permissions until {expiring_time_string}.")
        await self.bot.channels['mod-logs'].send(f"⭕ **Permission Granted**: {ctx.author.mention} granted streaming permissions to {member.mention} until {expiring_time_string}")

    @is_staff("OP")
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    @commands.command()
    async def notempstream(self, ctx, member: discord.Member):
        """Revokes temporary streaming permissions from a member."""
        await member.remove_roles(self.bot.roles['streamer(temp)'])

        await crud.remove_timed_role(member.id, self.bot.roles['streamer(temp)'].id)
        msg_user = "Your temporary streaming permissions have been revoked!"
        await utils.send_dm_message(member, msg_user, ctx)
        await self.bot.channels['mod-logs'].send(f"⭕ **Permission Revoked**: {ctx.author.mention} revoked {member.mention} streaming permissions.")

    @is_staff_app("OP")
    @app_commands.guilds(886216686582263809)
    @app_commands.command()
    @app_commands.describe(member="Member to apply restriction.",
                           restriction="Restriction Type.",
                           length="Restriction length in ##d##m##ss format.",
                           reason="Reason for restriction")
    @app_commands.choices(restriction=[
        Choice(name='Embed Permissions', value='No-Embed',),
        Choice(name='Elsewhere access', value='No-elsewhere'),
        Choice(name='Meme commands access', value='No-Memes'),
        Choice(name='Art-channel access', value='No-art'),
    ])
    async def take(self,
                   interaction: discord.Interaction,
                   member: discord.Member,
                   restriction: Choice[str],
                   length: app_commands.Transform[int, utils.TimeTransformer],
                   reason: str = None):
        """Applies a temporary restriction to a member. OP+ Only"""

        role = self.bot.roles[restriction.value]

        delta = datetime.timedelta(seconds=length)
        timestamp = datetime.datetime.now()

        end_time = timestamp + delta
        end_time_str = utils.dtm_to_discord_timestamp(end_time)

        await crud.add_timed_role(member.id, role.id, end_time)
        await member.add_roles(role, reason=reason)

        msg_user = f"You have been given the {restriction.value} restriction role temporarily!"
        msg_log = f"🚫 **Timed Restriction**: {interaction.user.mention} gave {restriction.value} to {member.mention} for {delta}, until {end_time_str} | {self.bot.escape_text(member)}"
        if reason is not None:
            msg_user += " The given reason is: " + reason
            msg_log += "\n✏️ __Reason__: " + reason
        msg_user += f"\n\nIf you feel this was unjustified, you may appeal in {self.bot.channels['appeals'].mention}\n\nThis restriction lasts until {end_time_str}."
        dm_sent = await utils.send_dm_message(member, msg_user)
        await interaction.response.send_message(f"{member.mention} now has the {restriction.value} role temporarily.{' Failed to send DM message.' if not dm_sent else ''}")
        await self.bot.channels['mod-logs'].send(msg_log)


async def setup(bot):
    await bot.add_cog(Mod(bot))
