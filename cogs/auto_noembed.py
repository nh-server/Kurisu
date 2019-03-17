from discord.ext import commands


class AutoNoEmbed(commands.Cog):
    """
    Logs join and leave messages.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Cog "{}" loaded'.format(self.__class__.__name__))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.add_roles(self.bot.noembed_role, reason="Auto NoEmbed")

def setup(bot):
    bot.add_cog(AutoNoEmbed(bot))
