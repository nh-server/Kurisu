from discord.ext import commands
from utils import crud
from utils.checks import is_staff


class ModDB(commands.Cog):
    """
    Database management commands.
    """

    NOT_FOUND = 'Flag was not found in the database. ⚠️'

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        return True

    @is_staff('Owner')
    @commands.command()
    async def addflag(self, ctx, name):
        """Adds a config flag to the database. Owners only."""
        if await crud.get_flag(name) is None:
            await crud.add_flag(name)
            await ctx.send('Flag added to the database. ✅')
        else:
            await ctx.send('Flag already exists in the database. ⚠️')

    @is_staff('Owner')
    @commands.command()
    async def delflag(self, ctx, name):
        """Removes a config flag from the database. Owners only."""
        if await crud.get_flag(name):
            await crud.remove_flag(name)
            await ctx.send('Flag removed from the database. ✅')
        else:
            await ctx.send(self.NOT_FOUND)

    @is_staff('Owner')
    @commands.command()
    async def getflag(self, ctx, name):
        """Retrieves a config flag from the database. Owners only."""
        flag = await crud.get_flag(name)
        if flag is not None:
            await ctx.send(f'{name} is set to: {flag.value}.')
        else:
            await ctx.send(self.NOT_FOUND)

    @is_staff('Owner')
    @commands.command()
    async def setflag(self, ctx, name, value: bool):
        """Sets a config flag in the database. Owners only."""
        if await crud.get_flag(name):
            await crud.set_flag(name, value)
            await ctx.send("Flag's value was set. ✅")
        else:
            await ctx.send(self.NOT_FOUND)


def setup(bot):
    bot.add_cog(ModDB(bot))
