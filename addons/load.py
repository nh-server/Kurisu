from discord.ext import commands
from addons.checks import is_staff

class Load:
    """
    Load commands.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    # Load test
    @is_staff("OP")
    @commands.command(hidden=True)
    async def load(self, *, module : str):
        """Loads an addon."""
        try:
            if module[0:7] != "addons.":
                module = "addons." + module
            self.bot.load_extension(module)
            await self.bot.say('✅ Extension loaded.')
        except Exception as e:
            await self.bot.say('💢 Failed!\n```\n{}: {}\n```'.format(type(e).__name__, e))

    @is_staff("OP")
    @commands.command(hidden=True)
    async def unload(self, *, module : str):
        """Unloads an addon."""
        try:
            if module[0:7] != "addons.":
                module = "addons." + module
            if module == "addons.load":
                await self.bot.say("❌ I don't think you want to unload that!")
            else:
                self.bot.unload_extension(module)
                await self.bot.say('✅ Extension unloaded.')
        except Exception as e:
            await self.bot.say('💢 Failed!\n```\n{}: {}\n```'.format(type(e).__name__, e))

    @is_staff("OP")
    @commands.command(name='reload', hidden=True)
    async def _reload(self, *, module : str):
        """Reloads an addon."""
        try:
            if module[0:7] != "addons.":
                module = "addons." + module
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
            await self.bot.say('✅ Extension reloaded.')
        except Exception as e:
            await self.bot.say('💢 Failed!\n```\n{}: {}\n```'.format(type(e).__name__, e))

def setup(bot):
    bot.add_cog(Load(bot))
