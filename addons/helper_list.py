import json
from discord.ext import commands
import addons.checks
from discord import Member


@commands.guild_only()
class Helper_list(commands.Cog):
    """
    Management of active helpers.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    @addons.checks.is_staff("Owner")
    @commands.command()
    async def addhelper(self, ctx, member: Member, position):
        """Add user as a helper. Owners only."""
        if position not in self.bot.helper_roles:
            await ctx.send("💢 That's not a valid position. You can use __{}__".format("__, __".join(self.bot.helper_roles.keys())))
            return
        addons.checks.helpers[str(member.id)] = position
        with open("data/helpers.json", "w") as f:
            json.dump(addons.checks.helpers, f)
        await member.add_roles(self.bot.helpers_role)
        await ctx.send("{} is now a helper. Welcome to the party room!".format(member.mention, position))

    @addons.checks.is_staff("Owner")
    @commands.command()
    async def delhelper(self, ctx, member: Member):
        """Remove user from helpers. Owners only."""
        await ctx.send(member.name)
        addons.checks.helpers.pop(str(member.id), None)
        with open("data/helpers.json", "w") as f:
            json.dump(addons.checks.helpers, f)
        await member.remove_roles(self.bot.helpers_role, *self.bot.helper_roles.values())
        await ctx.send("{} is no longer a helper. Stop by some time!".format(member.mention))

    @addons.checks.is_staff("Helper")
    @commands.command()
    async def helpon(self, ctx):
        """Gain highlighted helping role. Only needed by Helpers."""
        author = ctx.author
        if str(author.id) not in addons.checks.helpers:
            await ctx.send("You are not listed as a helper, and can't use this.")
            return
        author.add_roles(self.bot.helper_roles[addons.checks.helpers[str(author.id)]])
        await ctx.send("{} is now actively helping.".format(author.mention))
        msg = "🚑 **Elevated: +Help**: {} | {}#{}".format(author.mention, author.name, author.discriminator)
        await self.bot.modlogs_channel.send(msg)

    @addons.checks.is_staff("Helper")
    @commands.command()
    async def helpoff(self, ctx):
        """Remove highlighted helping role. Only needed by Helpers."""
        author = ctx.author
        if str(author.id) not in addons.checks.helpers:
            await ctx.send("You are not listed as a helper, and can't use this.")
            return
        await author.remove_roles(self.bot.helper_roles[addons.checks.helpers[str(author.id)]])
        await ctx.send("{} is no longer actively helping!".format(author.mention))
        msg = "👎🏻 **De-Elevated: -Help**: {} | {}#{}".format(author.mention, author.name, author.discriminator)
        await self.bot.modlogs_channel.send(msg)

def setup(bot):
    bot.add_cog(Helper_list(bot))
