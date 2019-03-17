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
        if member.id in self.bot.watching:
            await ctx.send("User is already being watched")
            return
        self.bot.watching.append(member.id)
        self.add_watch(member)
        await ctx.send("{} is being watched.".format(member.mention))
        msg = "👀 **Watch**: {} put {} on watch | {}#{}".format(ctx.author.mention, member.mention, member.name, member.discriminator)
        await self.bot.modlogs_channel.send(msg)
        await self.bot.watchlogs_channel.send(msg)

    @is_staff("HalfOP")
    @commands.command(pass_context=True)
    async def unwatch(self, ctx, member: converters.SafeMember):
        if member.id not in self.bot.watching:
            await ctx.send("This user was not being watched.")
            return
        self.bot.watching.remove(member.id)
        self.remove_watch(member)
        await ctx.send("{} is no longer being watched.".format(member.mention))
        msg = "❌ **Unwatch**: {} removed {} from watch | {}#{}".format(ctx.author.mention, member.mention, member.name, member.discriminator)
        await self.bot.modlogs_channel.send(msg)
        await self.bot.watchlogs_channel.send(msg)

def setup(bot):
    bot.add_cog(Modwatch(bot))
