from cogs.checks import is_staff
from discord.ext import commands
import cogs.checks
from cogs.database import DatabaseCog
from cogs.converters import SafeMember


@commands.guild_only()
class HelperList(DatabaseCog):
    """
    Management of active helpers.
    """
    @is_staff(role='Owner')
    @commands.command()
    async def addhelper(self, ctx, member: SafeMember, position):
        """Add user as a helper. Owners only."""
        if position not in self.bot.helper_roles:
            await ctx.send("💢 That's not a valid position. You can use __{}__".format("__, __".join(self.bot.helper_roles.keys())))
            return
        self.add_helper(member.id, position)
        await member.add_roles(self.bot.helpers_role)
        await ctx.send("{} is now a helper. Welcome to the party room!".format(member.mention, position))

    @commands.command()
    async def delhelper(self, ctx, member: SafeMember):
        """Remove user from helpers. Owners only."""
        await ctx.send(member.name)
        self.remove_helper(member.id)
        await member.remove_roles(self.bot.helpers_role, *self.bot.helper_roles.values())
        await ctx.send("{} is no longer a helper. Stop by some time!".format(member.mention))

    @commands.command()
    async def helpon(self, ctx):
        """Gain highlighted helping role. Only needed by Helpers."""
        author = ctx.author
        console = self.get_console(ctx.author.id)
        if not console:
            await ctx.send("You are not listed as a helper, and can't use this.")
            return
        await author.add_roles(self.bot.helper_roles[console])
        await ctx.send("{} is now actively helping.".format(author.mention))
        msg = "🚑 **Elevated: +Help**: {} | {}#{}".format(author.mention, author.name, author.discriminator)
        await self.bot.modlogs_channel.send(msg)

    @commands.command()
    async def helpoff(self, ctx):
        """Remove highlighted helping role. Only needed by Helpers."""
        author = ctx.author
        console = self.get_console(ctx.author.id)
        if not console:
            await ctx.send("You are not listed as a helper, and can't use this.")
            return
        await author.remove_roles(self.bot.helper_roles[cogs.checks.helpers[console]])
        await ctx.send("{} is no longer actively helping!".format(author.mention))
        msg = "👎🏻 **De-Elevated: -Help**: {} | {}#{}".format(author.mention, author.name, author.discriminator)
        await self.bot.modlogs_channel.send(msg)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send("{} You don't have permission to use this command.".format(ctx.author.mention))


def setup(bot):
    bot.add_cog(HelperList(bot))
