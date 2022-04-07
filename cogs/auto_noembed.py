from discord.ext import commands


class AutoNoEmbed(commands.Cog):
    """
    Logs join and leave messages.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.add_roles(self.bot.roles['No-Embed'], reason="Auto NoEmbed")


async def setup(bot):
    await bot.add_cog(AutoNoEmbed(bot))
