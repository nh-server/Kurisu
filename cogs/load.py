from discord.ext import commands
from cogs.checks import is_staff


class Load(commands.Cog):
    """
    Load commands.
    """
    def __init__(self, bot):
        self.bot = bot
        print(f'Cog "{self.qualified_name}" loaded')

    async def cog_check(self, ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        return True

    @is_staff("OP")
    @commands.command(hidden=True)
    async def load(self, ctx, *, module: str):
        """Loads a Cog."""
        try:
            if module[0:7] != "cogs.":
                module = "cogs." + module
            self.bot.load_extension(module)
            await ctx.send('✅ Extension loaded.')
        except Exception as e:
            await ctx.send(f'💢 Failed!\n```\n{type(e).__name__}: {e}\n```')

    @is_staff("OP")
    @commands.command(hidden=True)
    async def unload(self, ctx, *, module: str):
        """Unloads a Cog."""
        try:
            if module[0:7] != "cogs.":
                module = "cogs." + module
            if module == "cogs.load":
                await ctx.send("❌ I don't think you want to unload that!")
            else:
                self.bot.unload_extension(module)
                await ctx.send('✅ Extension unloaded.')
        except Exception as e:
            await ctx.send(f'💢 Failed!\n```\n{type(e).__name__}: {e}\n```')

    @is_staff("OP")
    @commands.command(name='reload')
    async def _reload(self, ctx, *, module: str):
        """Reloads a Cog."""
        try:
            if module[0:7] != "cogs.":
                module = "cogs." + module
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
            await ctx.send('✅ Extension reloaded.')
        except Exception as e:
            await ctx.send(f'💢 Failed!\n```\n{type(e).__name__}: {e}\n```')


def setup(bot):
    bot.add_cog(Load(bot))
