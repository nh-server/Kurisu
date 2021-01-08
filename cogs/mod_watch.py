import discord

from discord.ext import commands
from utils import utils, crud
from utils.checks import is_staff


class Modwatch(commands.Cog):
    """
    User watch management commands.
    """

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        return True

    @is_staff("Helper")
    @commands.command()
    async def watch(self, ctx, member: discord.Member, *, reason=""):
        if await crud.is_watched(member.id):
            await ctx.send("User is already being watched!")
            return
        await crud.add_watch(member.id)
        await ctx.send(f"{member.mention} is being watched.")
        msg = f"👀 **Watch**: {ctx.author.mention} put {member.mention} on watch | {member}"
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
    async def unwatch(self, ctx, member: discord.Member):
        if not await crud.is_watched(member.id):
            await ctx.send("This user was not being watched.")
            return
        await crud.remove_watch(member.id)
        await ctx.send(f"{member.mention} is no longer being watched.")
        msg = f"❌ **Unwatch**: {ctx.author.mention} removed {member.mention} from watch | {self.bot.escape_text(member)}"
        await self.bot.channels['mod-logs'].send(msg)
        await self.bot.channels['watch-logs'].send(msg)


def setup(bot):
    bot.add_cog(Modwatch(bot))
