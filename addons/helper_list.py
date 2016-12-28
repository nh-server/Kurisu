import discord
import json
from discord.ext import commands
from sys import argv

class Helper_list:
    """
    Management of active helpers.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    roles = ["On-Duty"]

    @commands.has_permissions(administrator=True)
    @commands.command(pass_context=True)
    async def addhelper(self, ctx, user, position):
        """Add user as a helper. Owners only."""
        if position not in self.roles:
            await self.bot.say("💢 That's not a valid position.")
            return
        helpers_role = discord.utils.get(ctx.message.server.roles, name="Helpers")
        member = ctx.message.mentions[0]
        server = ctx.message.author.server
        with open("helpers.json", "r") as f:
            helpers = json.load(f)
        helpers[member.id] = position
        with open("helpers.json", "w") as f:
            json.dump(helpers, f)
        # replace roles, so to not leave previous ones on by accident
        if position == "On-Duty":  # this role requires the use of sudo
            await self.bot.replace_roles(member, helpers_role)
        else:
            await self.bot.replace_roles(member, helpers_role, discord.utils.get(ctx.message.server.roles, name=position))
        await self.bot.say("{} is now a helper. Welcome to the party room!".format(member.mention, position))

    @commands.has_permissions(administrator=True)
    @commands.command(pass_context=True)
    async def delhelper(self, ctx, user):
        """Remove user from helpers. Owners only."""
        helpers_role = discord.utils.get(ctx.message.server.roles, name="Helpers")
        member = ctx.message.mentions[0]
        server = ctx.message.author.server
        await self.bot.say(member.name)
        with open("helpers.json", "r") as f:
            helpers = json.load(f)
        helpers.pop(member.id, None)
        with open("helpers.json", "w") as f:
            json.dump(helpers, f)
        await self.bot.replace_roles(member)
        await self.bot.say("{} is no longer a helper. Stop by some time!".format(member.mention))
        
#Usage of the helper highlighted role


    @commands.command(pass_context=True)
    async def helpon(self, ctx):
        """Gain highlighted helping role. Only needed by Helpers."""
        onduty_role = discord.utils.get(ctx.message.server.roles, name="On-Duty")
        author = ctx.message.author
        server = author.server
        with open("helpers.json", "r") as f:
            helpers = json.load(f)
        if author.id not in helpers:
            await self.bot.say("You are not listed as a helper, and can't use this.")
            return
        if helpers[author.id] != "On-Duty":
            await self.bot.say("You are not a helper, therefore this command is not required.")
            return
        await self.bot.add_roles(author, onduty_role)
        await self.bot.say("{} is now actively helping.".format(author.mention))
        msg = "🚑 **Elevated: +Help**: {} | {}#{}".format(author.mention, author.name, author.discriminator)
        await self.bot.send_message(discord.utils.get(server.channels, name="mod-logs"), msg)

    @commands.command(pass_context=True)
    async def helpoff(self, ctx):
        """Remove highlighted helping role. Only needed by Helpers."""
        onduty_role = discord.utils.get(ctx.message.server.roles, name="On-Duty")
        author = ctx.message.author
        server = author.server
        with open("helpers.json", "r") as f:
            helpers = json.load(f)
        if author.id not in helpers:
            await self.bot.say("You are not listed as a helper, and can't use this.")
            return
        if helpers[author.id] != "On-Duty":
            await self.bot.say("You are not a helper, therefore this command is not required.")
            return
        await self.bot.remove_roles(author, onduty_role)
        await self.bot.say("{} is no longer actively helping!".format(author.mention))
        msg = "👎🏻 **De-Elevated: -Help**: {} | {}#{}".format(author.mention, author.name, author.discriminator)
        await self.bot.send_message(discord.utils.get(server.channels, name="mod-logs"), msg)
        

def setup(bot):
    bot.add_cog(Helper_list(bot))
