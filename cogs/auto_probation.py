from discord.ext import commands


class AutoProbation(commands.Cog):
    """
    Logs join and leave messages.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Cog "{}" loaded'.format(self.__class__.__name__))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.add_roles(self.bot.probation_role, reason="Auto NoEmbed")

def setup(bot):
    bot.add_cog(AutoProbation(bot))
