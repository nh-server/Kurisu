import json
from discord.ext import commands
import addons.checks

class Helper_list:
    """
    Management of active helpers.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    @addons.checks.is_staff("Owner")
    @commands.command(pass_context=True)
    async def addhelper(self, ctx, user, position):
        """Add user as a helper. Owners only."""
        if position not in self.bot.helper_roles:
            await self.bot.say("💢 That's not a valid position. You can use __{}__".format("__, __".join(self.bot.helper_roles.keys())))
            return
        member = ctx.message.mentions[0]
        addons.checks.helpers[member.id] = position
        with open("data/helpers.json", "w") as f:
            json.dump(addons.checks.helpers, f)
        await self.bot.add_roles(member, self.bot.helpers_role)
        await self.bot.say("{} is now a helper. Welcome to the party room!".format(member.mention, position))

    @addons.checks.is_staff("Owner")
    @commands.command(pass_context=True)
    async def delhelper(self, ctx, user):
        """Remove user from helpers. Owners only."""
        member = ctx.message.mentions[0]
        await self.bot.say(member.name)
        addons.checks.helpers.pop(member.id, None)
        with open("data/helpers.json", "w") as f:
            json.dump(addons.checks.helpers, f)
        await self.bot.remove_roles(member, self.bot.helpers_role, *self.bot.helper_roles.values())
        await self.bot.say("{} is no longer a helper. Stop by some time!".format(member.mention))

    @addons.checks.is_staff("Helper")
    @commands.command(pass_context=True)
    async def helpon(self, ctx):
        """Gain highlighted helping role. Only needed by Helpers."""
        author = ctx.message.author
        if author.id not in addons.checks.helpers:
            await self.bot.say("You are not listed as a helper, and can't use this.")
            return
        await self.bot.add_roles(author, self.bot.helper_roles[addons.checks.helpers[author.id]])
        await self.bot.say("{} is now actively helping.".format(author.mention))
        msg = "🚑 **Elevated: +Help**: {} | {}#{}".format(author.mention, author.name, author.discriminator)
        await self.bot.send_message(self.bot.modlogs_channel, msg)

    @addons.checks.is_staff("Helper")
    @commands.command(pass_context=True)
    async def helpoff(self, ctx):
        """Remove highlighted helping role. Only needed by Helpers."""
        author = ctx.message.author
        if author.id not in addons.checks.helpers:
            await self.bot.say("You are not listed as a helper, and can't use this.")
            return
        await self.bot.remove_roles(author, self.bot.helper_roles[addons.checks.helpers[author.id]])
        await self.bot.say("{} is no longer actively helping!".format(author.mention))
        msg = "👎🏻 **De-Elevated: -Help**: {} | {}#{}".format(author.mention, author.name, author.discriminator)
        await self.bot.send_message(self.bot.modlogs_channel, msg)

def setup(bot):
    bot.add_cog(Helper_list(bot))
