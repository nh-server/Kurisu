from cogs.database import DatabaseCog
from discord.ext import commands
from cogs.checks import is_staff
from cogs import converters


@commands.guild_only()
class Modwatch(DatabaseCog):
    """
    User watch management commands.
    """
    @is_staff("HalfOP")
    @commands.command()
    async def watch(self, ctx, member: converters.SafeMember):
        if self.is_watched(member.id):
            await ctx.send("User is already being watched!")
            return
        self.add_watch(member.id)
        await ctx.send("{} is being watched.".format(member.mention))
        msg = "👀 **Watch**: {} put {} on watch | {}#{}".format(ctx.author.mention, member.mention, member.name, member.discriminator)
        await self.bot.modlogs_channel.send(msg)
        await self.bot.watchlogs_channel.send(msg)

    @is_staff("HalfOP")
    @commands.command(pass_context=True)
    async def unwatch(self, ctx, member: converters.SafeMember):
        if not self.is_watched(member.id):
            await ctx.send("This user was not being watched.")
            return
        self.remove_watch(member.id)
        await ctx.send("{} is no longer being watched.".format(member.mention))
        msg = "❌ **Unwatch**: {} removed {} from watch | {}#{}".format(ctx.author.mention, member.mention, member.name, member.discriminator)
        await self.bot.modlogs_channel.send(msg)
        await self.bot.watchlogs_channel.send(msg)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send("{} You don't have permission to use this command.".format(ctx.author.mention))


def setup(bot):
    bot.add_cog(Modwatch(bot))
