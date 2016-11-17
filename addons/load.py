#Importing libraries
import discord
from discord.ext import commands
from sys import argv

class Load:
    """
    Load commands.
    """
    def __init__(self, bot):
        self.bot = bot
    print('Addon "Load" has been loaded.')

    # Load test
    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def load(self, *, module : str):
        """Loads an addon."""
        try:
            if module[0:7] != "addons.":
                module = "addons." + module
            self.bot.load_extension(module)
        except Exception as e:
            await self.bot.say('💢 Failed!\n```\n{}: {}\n```'.format(type(e).__name__, e))
        else:
            await self.bot.say('✅ Extension loaded.')

    @commands.has_permissions(ban_members=True)
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
        except Exception as e:
            await self.bot.say('💢 Failed!\n```\n{}: {}\n```'.format(type(e).__name__, e))
        else:
            await self.bot.say('✅ Extension unloaded.')

    @commands.has_permissions(ban_members=True)
    @commands.command(name='reload', hidden=True)
    async def _reload(self, *, module : str):
        """Reloads an addon."""
        try:
            if module[0:7] != "addons.":
                module = "addons." + module
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except Exception as e:
            await self.bot.say('💢 Failed!\n```\n{}: {}\n```'.format(type(e).__name__, e))
        else:
            await self.bot.say('✅ Extension reloaded.')

    @commands.command(hidden=True)
    async def addonlist(self):
       """lists addons."""
       await self.bot.say("assistance\nauto_noembed\nauto_probation\nblah\nctrerr\nload\nlockdown\nlogs\nmemes\nmod\nrules")

def setup(bot):
    bot.add_cog(Load(bot))
