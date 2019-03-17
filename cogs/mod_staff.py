from discord.ext import commands
from cogs.checks import is_staff
from cogs.database import DatabaseCog
from cogs import converters


@commands.guild_only()
class ModStaff(DatabaseCog):
    """
    Staff management commands.
    """
    @is_staff("Owner")
    @commands.command()
    async def addstaff(self, ctx, member: converters.SafeMember, position):
        """Add user as staff. Owners only."""
        if position not in self.bot.staff_ranks:
            await ctx.send("💢 That's not a valid position. You can use __{}__".format("__, __".join(self.bot.staff_ranks.keys())))
            return
        self.add_staff(member.id, position)
        # remove leftover staff roles
        await member.remove_roles(*self.bot.staff_ranks.values())
        if position == "HalfOP":  # this role requires the use of sudo
            await member.add_roles(self.bot.staff_role)
        else:
            await member.add_roles(self.bot.staff_role, self.bot.staff_ranks[position])
        await ctx.send("{} is now on staff as {}. Welcome to the secret party room!".format(member.mention, position))

    @is_staff("Owner")
    @commands.command()
    async def delstaff(self, ctx, member: converters.SafeMember):
        """Remove user from staff. Owners only."""
        await ctx.send(member.name)
        self.remove_staff(member.id)
        await member.remove_roles(self.bot.staff_role, *self.bot.staff_ranks.values())
        await ctx.send("{} is no longer staff. Stop by some time!".format(member.mention))

    @is_staff("HalfOP")
    @commands.command(pass_context=True)
    async def sudo(self, ctx):
        """Gain staff powers temporarily. Only needed by HalfOPs."""
        author = ctx.author
        staff_role = self.get_stafftrole(ctx.author.id)
        if not staff_role:
            await ctx.send("You are not listed as staff, and can't use this. (this message should not appear)")
            return
        if staff_role != "HalfOP":
            await ctx.send("You are not HalfOP, therefore this command is not required.")
            return
        await author.add_roles(self.bot.halfop_role)
        await ctx.send("{} is now using sudo. Welcome to the twilight zone!".format(author.mention))
        msg = "👮 **Sudo**: {} | {}#{}".format(author.mention, author.name, author.discriminator)
        await self.bot.modlogs_channel.send(msg)

    @is_staff("HalfOP")
    @commands.command(pass_context=True)
    async def unsudo(self, ctx):
        """Remove temporary staff powers. Only needed by HalfOPs."""
        author = ctx.author
        staff_role = self.get_stafftrole(ctx.author.id)
        if not staff_role:
            await ctx.send("You are not listed as staff, and can't use this. (this message should not appear)")
            return
        if staff_role != "HalfOP":
            await ctx.send("You are not HalfOP, therefore this command is not required.")
            return
        await author.remove_roles(self.bot.halfop_role)
        await ctx.send("{} is no longer using sudo!".format(author.mention))
        msg = "🕵 **Unsudo**: {} | {}#{}".format(author.mention, author.name, author.discriminator)
        await self.bot.modlogs_channel.send(msg)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send("{} You don't have permission to use this command.".format(ctx.author.mention))


def setup(bot):
    bot.add_cog(ModStaff(bot))
