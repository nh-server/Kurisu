import discord
from discord.ext import commands
from cogs.checks import is_staff, check_staff_id, check_bot_or_staff
from cogs.converters import SafeMember
from cogs.database import DatabaseCog
from cogs import utils


class ModWarn(DatabaseCog):
    """
    Warn commands.
    """

    async def cog_check(self, ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        return True

    @is_staff('Helper')
    @commands.command()
    async def warn(self, ctx, member: SafeMember, *, reason=""):
        """Warn a user. Staff and Helpers only."""
        issuer = ctx.author
        if await check_bot_or_staff(ctx, member, "warn"):
            return
        await self.add_warn(member.id, issuer.id, reason)
        msg = f"You were warned on {ctx.guild.name}."
        if reason != "":
            # much \n
            msg += " The given reason is: " + reason
        warn_count = len(await self.get_warns(member.id))
        msg += f"\n\nPlease read the rules in <#196618637950451712>. This is warn #{warn_count}."
        if warn_count == 2:
            msg += " __The next warn will automatically kick.__"
        if warn_count == 3:
            msg += "\n\nYou were kicked because of this warning. You can join again right away. Two more warnings will result in an automatic ban."
        if warn_count == 4:
            msg += "\n\nYou were kicked because of this warning. This is your final warning. You can join again, but **one more warn will result in a ban**."
        if warn_count == 5:
            msg += "\n\nYou were automatically banned due to five warnings."
        await utils.send_dm_message(member, msg)
        if warn_count == 3 or warn_count == 4:
            self.bot.actions.append("wk:"+str(member.id))
            await member.kick(reason="Warn kicked.")
        if warn_count >= 5:  # just in case
            self.bot.actions.append("wb:"+str(member.id))
            try:
                await member.ban(reason="5 warns.", delete_message_days=0)
            except discord.Forbidden:
                await ctx.send("I can't ban this user!")
        await ctx.send(f"{member.mention} warned. User has {warn_count} warning(s)")
        msg = f"⚠️ **Warned**: {issuer.mention} warned {member.mention} (warn #{warn_count}) | {self.bot.escape_text(member)}"
        reason = self.bot.escape_text(reason)
        signature = utils.command_signature(ctx.command)
        if reason != "":
            # much \n
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.channels['mod-logs'].send(msg + (f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user." if reason == "" else ""))

    @is_staff('HalfOP')
    @commands.command()
    async def warnid(self, ctx, userid: int, *, reason=""):
        """Warn a user using their id, even if they're not in the server. Staff only."""
        issuer = ctx.author
        try:
            member = await self.bot.fetch_user(userid)
        except discord.errors.NotFound:
            await ctx.send(f"No user associated with ID {userid}.")
            return
        if await check_bot_or_staff(ctx, member, "warn"):
            return
        await self.add_warn(member.id, issuer.id, reason)
        msg = f"You were warned on {ctx.guild.name}."
        if reason != "":
            # much \n
            msg += " The given reason is: " + reason
        warn_count = len(await self.get_warns(member.id))
        msg += f"\n\nPlease read the rules in <#196618637950451712>. This is warn #{warn_count}."
        if warn_count == 2:
            msg += " __The next warn will automatically kick.__"
        if warn_count == 3:
            msg += "\n\nYou were kicked because of this warning. You can join again right away. Two more warnings will result in an automatic ban."
        if warn_count == 4:
            msg += "\n\nYou were kicked because of this warning. This is your final warning. You can join again, but **one more warn will result in a ban**."
        if warn_count == 5:
            msg += "\n\nYou were automatically banned due to five warnings."
        await utils.send_dm_message(userid, msg)
        if warn_count == 3 or warn_count == 4:
            self.bot.actions.append("wk:"+str(member.id))
            try:
                await member.kick(reason="Warn kicked.")
            except:
                pass
        if warn_count >= 5:  # just in case
            self.bot.actions.append("wb:"+str(member.id))
            try:
                await ctx.guild.ban(member, reason="5 warns.", delete_message_days=0)
            except discord.Forbidden:
                await ctx.send("I can't ban this user!")
        await ctx.send(f"{member.mention} warned. User has {warn_count} warning(s)")
        reason = self.bot.escape_text(reason)
        signature = utils.command_signature(self.warn)
        msg = f"⚠️ **Warned**: {issuer.mention} warned {member.mention} (warn #{warn_count}) | {member}"
        if reason != "":
            # much \n
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.channels['mod-logs'].send(msg + (f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user." if reason == "" else ""))

    @is_staff('Helper')
    @commands.command()
    async def softwarn(self, ctx, member: SafeMember, *, reason=""):
        """Warn a user without automated action. Staff and Helpers only."""
        issuer = ctx.author
        if await check_bot_or_staff(ctx, member, "warn"):
            return
        warn_count = len(await self.get_warns(member.id))
        if warn_count >= 5:
            await ctx.send("A user can't have more than 5 warns!")
            return
        warn_count += 1
        await self.add_warn(member.id, ctx.author.id, reason)
        msg = f"You were warned on {ctx.guild}."
        if reason != "":
            # much \n
            msg += " The given reason is: " + reason
        msg += f"\n\nThis is warn #{warn_count}."
        msg += "\n\nThis won't trigger any action."
        await utils.send_dm_message(member, msg)

        await ctx.send(f"{member.mention} softwarned. User has {warn_count} warning(s)")
        msg = f"⚠️ **Warned**: {issuer.mention} softwarned {member.mention} (warn #{warn_count}) | {self.bot.escape_text(member)}"
        reason = self.bot.escape_text(reason)
        signature = utils.command_signature(self.warn)
        if reason != "":
            # much \n
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.channels['mod-logs'].send(msg + (
            f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is automatically sent to the user." if reason == "" else ""))

    @commands.command()
    async def listwarns(self, ctx, member: SafeMember = None):
        """List warns for a user. Staff and Helpers only."""
        if not member:  # If user is set to None, its a selfcheck
            member = ctx.author
        issuer = ctx.author
        if not await check_staff_id(ctx, "Helper", ctx.author.id) and (member != issuer):
                msg = f"{issuer.mention} Using this command on others is limited to Staff and Helpers."
                await ctx.send(msg)
                return
        embed = discord.Embed(color=discord.Color.dark_red())
        embed.set_author(name=f"Warns for {member}", icon_url=member.avatar_url)
        warns = await self.get_warns(member.id)
        if warns:
            for idx, warn in enumerate(warns):
                issuer = await self.bot.fetch_user(warn[2])
                value = ""
                if ctx.channel == self.bot.channels['helpers'] or ctx.channel == self.bot.channels['mods'] or ctx.channel == self.bot.channels['mod-logs']:
                    value += f"Issuer: {issuer.name}\n"
                value += f"Reason: {warn[3]} "
                embed.add_field(name=f"{idx + 1}: {discord.utils.snowflake_time(warn[0])}", value=value)
        else:
            embed.description = "There are none!"
            embed.color = discord.Color.green()
        await ctx.send(embed=embed)

    @is_staff("Helper")
    @commands.command()
    async def listwarnsid(self, ctx, user_id: int):
        """List warns for a user based on ID. Staff and Helpers only."""
        member = await self.bot.fetch_user(user_id)
        embed = discord.Embed(color=discord.Color.dark_red())
        embed.set_author(name=f"Warns for {member}",
                         icon_url=member.avatar_url)
        warns = await self.get_warns(member.id)
        if warns:
            for idx, warn in enumerate(warns):
                issuer = await self.bot.fetch_user(warn[2])
                value = ""
                if ctx.channel == self.bot.channels['helpers'] or ctx.channel == self.bot.channels['mods'] or ctx.channel == self.bot.channels['mod-logs']:
                    value += f"Issuer: {issuer.name}\n"
                value += f"Reason: {warn[3]} "
                embed.add_field(name=f"{idx + 1}: {discord.utils.snowflake_time(warn[0])}", value=value)
        else:
            embed.description = "There are none!"
            embed.color = discord.Color.green()
        await ctx.send(embed=embed)

    @is_staff("SuperOP")
    @commands.command()
    async def copywarns_id2id(self, ctx, user_id1: int, user_id2: int):
        """Copy warns from one user ID to another. Overwrites all warns of the target user ID. SOP+ only."""
        warns = await self.get_warns(user_id1)
        if not warns:
            await ctx.safe_send(f"{user_id1} has no warns!")
            return
        for warn in warns:
            await self.add_warn(user_id2, warn[2], warn[3])
        warn_count = len(warns)
        user1 = await self.bot.fetch_user(user_id1)
        user2 = await self.bot.fetch_user(user_id2)
        await ctx.safe_send(f"{warn_count} warns were copied from {user1.name} to {user2.name}!")
        msg = f"📎 **Copied warns**: {ctx.author.mention} copied {warn_count} warns from {self.bot.escape_text(user1.name)}"\
              f"({user_id1}) to {self.bot.escape_text(user2.name)} ({user_id2})"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("HalfOP")
    @commands.command()
    async def delwarn(self, ctx, member: SafeMember, idx: int):
        """Remove a specific warn from a user. Staff only."""
        warns = await self.get_warns(member.id)
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
        warn = warns[idx-1]
        issuer = await self.bot.fetch_user(warn[2])
        embed = discord.Embed(color=discord.Color.dark_red(), title=f"Warn {idx} on {discord.utils.snowflake_time(warn[0]).strftime('%Y-%m-%d %H:%M:%S')}",
                              description=f"Issuer: {issuer}\nReason: {warn[3]}")
        await self.remove_warn_id(member.id, idx)
        await ctx.send(f"{member.mention} has a warning removed!")
        msg = f"🗑 **Deleted warn**: {ctx.author.mention} removed warn {idx} from {member.mention} | {self.bot.escape_text(member)}"
        await self.bot.channels['mod-logs'].send(msg, embed=embed)

    @is_staff("HalfOP")
    @commands.command()
    async def delwarnid(self, ctx, user_id: int, idx: int):
        """Remove a specific warn from a user based on ID. Staff only."""
        warns = await self.get_warns(user_id)
        if not warns:
            await ctx.safe_send(f"{user_id} has no warns!")
            return
        warn_count = len(warns)
        if idx > warn_count:
            await ctx.send(f"Warn index is higher than warn count ({warn_count})!")
            return
        if idx < 1:
            await ctx.send("Warn index is below 1!")
            return
        warn = warns[idx-1]
        issuer = await self.bot.fetch_user(warn[2])
        wuser = await self.bot.fetch_user(user_id)
        embed = discord.Embed(color=discord.Color.dark_red(), title=f"Warn {idx} on {discord.utils.snowflake_time(warn[0]).strftime('%Y-%m-%d %H:%M:%S')}",
                              description=f"Issuer: {issuer}\nReason: {warn[3]}")
        await self.remove_warn_id(user_id, idx)
        await ctx.safe_send(f"{wuser.name} has a warning removed!")
        msg = f"🗑 **Deleted warn**: {ctx.author.mention} removed warn {idx} from {wuser.mention} | {self.bot.escape_text(wuser)}"
        await self.bot.channels['mod-logs'].send(msg, embed=embed)

    @is_staff("HalfOP")
    @commands.command()
    async def clearwarns(self, ctx, member: SafeMember):
        """Clear all warns for a user. Staff only."""
        warns = await self.get_warns(member.id)
        if not warns:
            await ctx.send(f"{member.mention} has no warns!")
            return
        warn_count = len(warns)
        await self.remove_warns(member.id)
        await ctx.send(f"{member.mention} no longer has any warns!")
        msg = f"🗑 **Cleared warns**: {ctx.author.mention} cleared {warn_count} warns from {member.mention} | {self.bot.escape_text(member)}"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("HalfOP")
    @commands.command()
    async def clearwarnsid(self, ctx, user_id):
        """Clear all warns for a user based on ID. Staff only."""
        member = await self.bot.fetch_user(user_id)
        warns = await self.get_warns(member.id)
        if not warns:
            await ctx.safe_send(f"{member.name} has no warns!")
            return
        warn_count = len(warns)
        await self.remove_warns(member.id)
        await ctx.safe_send(f"{member.name} no longer has any warns!")
        msg = f"🗑 **Cleared warns**: {ctx.author.mention} cleared {warn_count} warns from {self.bot.escape_text(member.name)} ({user_id})"
        await self.bot.channels['mod-logs'].send(msg)


def setup(bot):
    bot.add_cog(ModWarn(bot))
