from cogs.database import DatabaseCog
from discord.ext import commands
from cogs.checks import is_staff
from cogs import converters, utils


class Modwatch(DatabaseCog):
    """
    User watch management commands.
    """

    async def cog_check(self, ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        return True

    @is_staff("Helper")
    @commands.command()
    async def watch(self, ctx, member: converters.SafeMember, *, reason=""):
        if await self.is_watched(member.id):
            await ctx.send("User is already being watched!")
            return
        await self.add_watch(member.id)
        await ctx.send(f"{member.mention} is being watched.")
        msg = f"👀 **Watch**: {ctx.author.mention} put {member.mention} on watch | {self.bot.escape_text(member)}"
        reason = self.bot.escape_text(reason)
        if reason != "":
            # much \n
            msg += "\n✏️ __Reason__: " + reason
        signature = utils.command_signature(ctx.command)
        await self.bot.channels['mod-logs'].send(msg + (
            f"\nPlease add an explanation below. In the future, it is recommended to use `{signature}` as the reason is very useful for saving time." if reason == "" else ""))
        await self.bot.channels['watch-logs'].send(msg + (
            "\nNo reason provided." if reason == "" else ""))

    @is_staff("Helper")
    @commands.command()
    async def unwatch(self, ctx, member: converters.SafeMember):
        if not await self.is_watched(member.id):
            await ctx.send("This user was not being watched.")
            return
        await self.remove_watch(member.id)
        await ctx.send(f"{member.mention} is no longer being watched.")
        msg = f"❌ **Unwatch**: {ctx.author.mention} removed {member.mention} from watch | {self.bot.escape_text(member)}"
        await self.bot.channels['mod-logs'].send(msg)
        await self.bot.channels['watch-logs'].send(msg)


def setup(bot):
    bot.add_cog(Modwatch(bot))
