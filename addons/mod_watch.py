import json
from discord.ext import commands
from addons.checks import is_staff
from addons import converters


@commands.guild_only()
class Modwatch(commands.Cog):
    """
    User watch management commands.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    @is_staff("HalfOP")
    @commands.command()
    async def watch(self, ctx, member: converters.SafeMember):
        self.bot.watching[member.id] = "{}#{}".format(member.name, member.discriminator)
        with open("data/watch.json", "w") as f:
            json.dump(self.bot.watching, f)
        await ctx.send("{} is being watched.".format(member.mention))
        msg = "👀 **Watch**: {} put {} on watch | {}#{}".format(ctx.author.mention, member.mention, member.name, member.discriminator)
        self.bot.modlogs_channel.send(msg)
        self.bot.watchlogs_channel.send(msg)

    @is_staff("HalfOP")
    @commands.command(pass_context=True)
    async def unwatch(self, ctx, member: converters.SafeMember):
        if member.id not in self.bot.watching:
            await ctx.send("This user was not being watched.")
            return
        self.bot.watching.pop(member.id)
        with open("data/watch.json", "w") as f:
            json.dump(self.bot.watching, f)
        await ctx.send("{} is no longer being watched.".format(member.mention))
        msg = "❌ **Unwatch**: {} removed {} from watch | {}#{}".format(ctx.author.mention, member.mention, member.name, member.discriminator)
        self.bot.modlogs_channel.send(msg)
        self.bot.watchlogs_channel.send(msg)

def setup(bot):
    bot.add_cog(Modwatch(bot))
