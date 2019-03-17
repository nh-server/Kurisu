import discord
import time
from discord.ext import commands
from cogs.checks import is_staff, check_staff_id
from cogs import converters
from cogs.database import DatabaseCog


@commands.guild_only()
class ModWarn(DatabaseCog):
    """
    Warn commands.
    """
    @is_staff('Helper')
    @commands.command()
    async def warn(self, ctx, member: converters.SafeMember, *, reason=""):
        """Warn a user. Staff and Helpers only."""
        issuer = ctx.author
        if check_staff_id(ctx, "Helper", member.id):
            await ctx.send("You can't warn another staffer with this command!")
            return
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.add_warn(member.id, ctx.author.id, reason, timestamp)
        msg = "You were warned on {}.".format(ctx.guild.name)
        if reason != "":
            # much \n
            msg += " The given reason is: " + reason
        warn_count = len(self.get_warns(member.id))
        msg += "\n\nPlease read the rules in <#196618637950451712>. This is warn #{}.".format(warn_count)
        if warn_count == 2:
            msg += " __The next warn will automatically kick.__"
        if warn_count == 3:
            msg += "\n\nYou were kicked because of this warning. You can join again right away. Two more warnings will result in an automatic ban."
        if warn_count == 4:
            msg += "\n\nYou were kicked because of this warning. This is your final warning. You can join again, but **one more warn will result in a ban**."
        if warn_count == 5:
            msg += "\n\nYou were automatically banned due to five warnings."
        try:
            await member.send(msg)
        except discord.errors.Forbidden:
            pass
        except discord.errors.HTTPException:
            pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
        if warn_count == 3 or warn_count == 4:
            self.bot.actions.append("wk:"+str(member.id))
            await member.kick(reason="Warn kicked.")
        if warn_count >= 5:  # just in case
            self.bot.actions.append("wb:"+str(member.id))
            await member.ban(reason="Warn banned.")
        await ctx.send("{} warned. User has {} warning(s)".format(member.mention, warn_count))
        msg = "⚠️ **Warned**: {} warned {} (warn #{}) | {}#{}".format(issuer.mention, member.mention, warn_count, member.name, member.discriminator)
        if reason != "":
            # much \n
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.modlogs_channel.send(msg + ("\nPlease add an explanation below. In the future, it is recommended to use `.warn <user> [reason]` as the reason is automatically sent to the user." if reason == "" else ""))

    @is_staff('OP')
    @commands.command(pass_context=True)
    async def softwarn(self, ctx, member: converters.SafeMember, *, reason=""):
        """Warn a user without automated action. Staff only."""
        issuer = ctx.author
        if check_staff_id(ctx, "Helper", member.id):
            await ctx.send("You can't warn another staffer with this command!")
            return
        warn_count = len(self.get_warns(member.id))
        if(warn_count>=5):
            await ctx.send("A user can't have more than 5 warns!")
            return
        warn_count+=1
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.add_warn(member.id, ctx.author.id, reason, timestamp)
        msg = "You were warned on {}.".format(ctx.guild)
        if reason != "":
            # much \n
            msg += " The given reason is: " + reason
        msg += "\n\nThis is warn #{}.".format(warn_count)
        msg += "\n\nThis won't trigger any action."
        try:
            await member.send(msg)
        except discord.errors.HTTPException:
            pass  # don't fail in case user has DMs disabled for this server, or blocked the bot

        await ctx.send("{} softwarned. User has {} warning(s)".format(member.mention, warn_count))
        msg = "⚠️ **Warned**: {} softwarned {} (warn #{}) | {}#{}".format(issuer.mention, member.mention, warn_count,
                                                                      member.name, member.discriminator)
        if reason != "":
            # much \n
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.modlogs_channel.send(msg + (
            "\nPlease add an explanation below. In the future, it is recommended to use `.warn <user> [reason]` as the reason is automatically sent to the user." if reason == "" else ""))

    @commands.command(pass_context=True)
    async def listwarns(self, ctx, user: discord.Member = None):
        """List warns for a user. Staff and Helpers only."""
        if not user: # If user is set to None, its a selfcheck
            user = ctx.author
        issuer = ctx.author
        member = user # A bit sloppy but its to reduce the amount of work needed to change below.
        if not check_staff_id(ctx, "Helper", ctx.author.id) and (member != issuer):
                msg = "{0} Using this command on others is limited to Staff and Helpers.".format(issuer.mention)
                await ctx.send(msg)
                return
        embed = discord.Embed(color=discord.Color.dark_red())
        embed.set_author(name="Warns for {}#{}".format(member.display_name, member.discriminator), icon_url=member.avatar_url)
        warns = self.get_warns(member.id)
        if warns:
            for idx, warn in enumerate(warns):
                wissuer = await self.bot.get_user_info(warn[1])
                value = ""
                if ctx.channel == self.bot.helpers_channel or ctx.channel == self.bot.mods_channel:
                    value += "Issuer: " + wissuer.name + "\n"
                value += "Reason: " + warn[2] + " "
                embed.add_field(name="{}: {}".format(idx + 1, warn[3]), value=value)
        else:
            embed.description = "There are none!"
            embed.color = discord.Color.green()
        await ctx.send(embed=embed)

    @is_staff("Helper")
    @commands.command(pass_context=True)
    async def listwarnsid(self, ctx, user_id: int):
        """List warns for a user based on ID. Staff and Helpers only."""
        member = await self.bot.get_user_info(user_id)
        embed = discord.Embed(color=discord.Color.dark_red())
        embed.set_author(name="Warns for {}#{}".format(member.display_name, member.discriminator),
                         icon_url=member.avatar_url)
        warns = self.get_warns(member.id)
        if warns:
            for idx, warn in enumerate(warns):
                wissuer = await self.bot.get_user_info(warn[1])
                value = ""
                if ctx.channel == self.bot.helpers_channel or ctx.channel == self.bot.mods_channel:
                    value += "Issuer: " + wissuer.name + "\n"
                value += "Reason: " + warn[2] + " "
                embed.add_field(name="{}: {}".format(idx + 1, warn[3]), value=value)
        else:
            embed.description = "There are none!"
            embed.color = discord.Color.green()
        await ctx.send(embed=embed)

    @is_staff("SuperOP")
    @commands.command(pass_context=True)
    async def copywarns_id2id(self, ctx, user_id1: int, user_id2: int):
        """Copy warns from one user ID to another. Overwrites all warns of the target user ID. Staff only."""
        warns = self.get_warns(user_id1)
        if not warns:
            await ctx.send("{} has no warns!".format(user_id1))
            return

        for warn in warns:
            self.add_warn(user_id2,warn[1], warn[2], warn[3])
        warn_count = len(warns)
        user1 = await self.bot.get_user_info(user_id1)
        user2 = await self.bot.get_user_info(user_id2)
        await ctx.send("{} warns were copied from {} to {}!".format(warn_count, user1.name, user2.name))
        msg = "📎 **Copied warns**: {} copied {} warns from {} ({}) to ".format(ctx.author.mention, warn_count, user1.name, user_id1)
        await self.bot.modlogs_channel.send(msg)

    @is_staff("HalfOP")
    @commands.command(pass_context=True)
    async def delwarn(self, ctx, member: converters.SafeMember, idx: int):
        """Remove a specific warn from a user. Staff only."""
        warns = self.get_warns(member.id)
        if not warns:
            await ctx.send("{} has no warns!".format(member.mention))
            return
        warn_count = len(warns)
        if idx > warn_count:
            await ctx.send("Warn index is higher than warn count ({})!".format(warn_count))
            return
        if idx < 1:
            await ctx.send("Warn index is below 1!")
            return
        warn = warns[idx-1]
        embed = discord.Embed(color=discord.Color.dark_red(), title="Warn {} on {}".format(idx, warn[3]),
                              description="Issuer: {}\nReason: {}".format(warn[1], warn[2]))
        self.remove_warn(member.id, idx)
        await ctx.send("{} has a warning removed!".format(member.mention))
        msg = "🗑 **Deleted warn**: {} removed warn {} from {} | {}#{}".format(ctx.author.mention, idx, member.mention, member.name, member.discriminator)
        await self.bot.modlogs_channel.send(msg, embed=embed)

    @is_staff("HalfOP")
    @commands.command(pass_context=True)
    async def delwarnid(self, ctx, user_id: int, idx: int):
        """Remove a specific warn from a user based on ID. Staff only."""
        warns = self.get_warns(user_id)
        if not warns:
            await ctx.send("{} has no warns!".format(user_id))
            return
        warn_count = len(warns)
        if idx > warn_count:
            await ctx.send("Warn index is higher than warn count ({})!".format(warn_count))
            return
        if idx < 1:
            await ctx.send("Warn index is below 1!")
            return
        warn = warns[idx-1]
        embed = discord.Embed(color=discord.Color.dark_red(), title="Warn {} on {}".format(idx, warn[3]),
                              description="Issuer: {}\nReason: {}".format(warn[1], warn[2]))
        self.remove_warn(user_id, idx)
        member = await self.bot_get_user_info(user_id)
        await ctx.send("{} has a warning removed!".format(member.name))
        msg = "🗑 **Deleted warn**: {} removed warn {} from {} | {}#{}".format(ctx.author.mention, idx, member.mention, member.name, member.discriminator)
        await self.bot.modlogs_channel.send(msg, embed=embed)

    @is_staff("HalfOP")
    @commands.command(pass_context=True)
    async def clearwarns(self, ctx, member: converters.SafeMember):
        """Clear all warns for a user. Staff only."""
        warns = self.get_warns(member.id)
        if not warns:
            await ctx.send("{} has no warns!".format(member.mention))
            return
        warn_count = len(warns)
        self.remove_warns(member.id)
        await ctx.send("{} no longer has any warns!".format(member.mention))
        msg = "🗑 **Cleared warns**: {} cleared {} warns from {} | {}#{}".format(ctx.author.mention, warn_count, member.mention, member.name, member.discriminator)
        await self.bot.modlogs_channel.send(msg)

    @is_staff("HalfOP")
    @commands.command(pass_context=True)
    async def clearwarnsid(self, ctx, user_id):
        """Clear all warns for a user based on ID. Staff only."""
        member = await self.bot.get_user_info(user_id)
        warns = self.get_warns(member.id)
        if not warns:
            await ctx.send("{} has no warns!".format(member.name))
            return
        warn_count = len(warns)
        self.remove_warns(member.id)
        await ctx.send("{} no longer has any warns!".format(member.name))
        msg = "🗑 **Cleared warns**: {} cleared {} warns from {} ({})".format(ctx.author.mention, warn_count, member.name, user_id)
        await self.bot.modlogs_channel.send(msg)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send("{} You don't have permission to use this command.".format(ctx.author.mention))


def setup(bot):
    bot.add_cog(ModWarn(bot))
