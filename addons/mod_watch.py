import json
from discord.ext import commands
from addons.checks import is_staff

class Modwatch:
    """
    User watch management commands.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    @is_staff("HalfOP")
    @commands.command(pass_context=True)
    async def watch(self, ctx, user):
        try:
            member = ctx.message.mentions[0]
        except IndexError:
            await self.bot.say("Please mention a user.")
            return
        self.bot.watching[member.id] = "{}#{}".format(member.name, member.discriminator)
        with open("data/watch.json", "w") as f:
            json.dump(self.bot.watching, f)
        await self.bot.say("{} is being watched.".format(member.mention))
        msg = "👀 **Watch**: {} put {} on watch | {}#{}".format(ctx.message.author.mention, member.mention, member.name, member.discriminator)
        await self.bot.send_message(self.bot.modlogs_channel, msg)
        await self.bot.send_message(self.bot.watchlogs_channel, msg)

    @is_staff("HalfOP")
    @commands.command(pass_context=True)
    async def unwatch(self, ctx, user):
        try:
            member = ctx.message.mentions[0]
        except IndexError:
            await self.bot.say("Please mention a user.")
            return
        if member.id not in self.bot.watching:
            await self.bot.say("This user was not being watched.")
            return
        self.bot.watching.pop(member.id)
        with open("data/watch.json", "w") as f:
            json.dump(self.bot.watching, f)
        await self.bot.say("{} is no longer being watched.".format(member.mention))
        msg = "❌ **Unwatch**: {} removed {} from watch | {}#{}".format(ctx.message.author.mention, member.mention, member.name, member.discriminator)
        await self.bot.send_message(self.bot.modlogs_channel, msg)
        await self.bot.send_message(self.bot.watchlogs_channel, msg)

def setup(bot):
    bot.add_cog(Modwatch(bot))
