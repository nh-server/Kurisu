from discord.ext import commands


class AutoNoEmbed(commands.Cog):
    """
    Logs join and leave messages.
    """
    def __init__(self, bot):
        self.bot = bot
        print(f'Cog "{self.qualified_name}" loaded')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.add_roles(self.bot.roles['No-Embed'], reason="Auto NoEmbed")


def setup(bot):
    bot.add_cog(AutoNoEmbed(bot))
