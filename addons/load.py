from discord.ext import commands
from addons.checks import is_staff


class Load(commands.Cog, command_attrs=dict(hidden=True)):
    """
    Load commands.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    # Load test
    @is_staff("OP")
    @commands.command()
    async def load(self, ctx, *, module: str):
        """Loads an addon."""
        try:
            if module[0:7] != "addons.":
                module = "addons." + module
            self.bot.load_extension(module)
            await ctx.send('✅ Extension loaded.')
        except Exception as e:
            await ctx.send('💢 Failed!\n```\n{}: {}\n```'.format(type(e).__name__, e))

    @is_staff("OP")
    @commands.command()
    async def unload(self, ctx, *, module: str):
        """Unloads an addon."""
        try:
            if module[0:7] != "addons.":
                module = "addons." + module
            if module == "addons.load":
                await ctx.send("❌ I don't think you want to unload that!")
            else:
                self.bot.unload_extension(module)
                await ctx.send('✅ Extension unloaded.')
        except Exception as e:
            await ctx.send('💢 Failed!\n```\n{}: {}\n```'.format(type(e).__name__, e))

    @is_staff("OP")
    @commands.command(name='reload')
    async def _reload(self, ctx, *, module : str):
        """Reloads an addon."""
        try:
            if module[0:7] != "addons.":
                module = "addons." + module
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
            await ctx.send('✅ Extension reloaded.')
        except Exception as e:
            await ctx.send('💢 Failed!\n```\n{}: {}\n```'.format(type(e).__name__, e))

def setup(bot):
    bot.add_cog(Load(bot))
