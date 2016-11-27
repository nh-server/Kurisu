#Importing libraries
import discord
from discord.ext import commands
from sys import argv

class Lockdown:
    """
    Channel lockdown commands.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    @commands.has_permissions(manage_messages=True)
    @commands.command(pass_context=True, name="lockdown")
    async def lockdown(self, ctx):
       """Lock message sending in the channel. Staff only."""
       try:
            everyone_role = discord.utils.get(ctx.message.server.roles, name="@everyone")
            overwrites = ctx.message.channel.overwrites_for(everyone_role)
            if overwrites.send_messages == False:
                await self.bot.say("🔒 Channel is already locked down. Use `.unlock` to unlock.")
                return
            overwrites.send_messages = False
            await self.bot.edit_channel_permissions(ctx.message.channel, everyone_role, overwrites)
            await self.bot.say("🔒 Channel locked down. Only staff members may speak. Do not bring the topic to other channels or risk disciplinary actions.")
            msg = "🔒 **Lockdown**: {0} by {1} | {2}#{3}".format(ctx.message.channel.mention, ctx.message.author.mention, ctx.message.author.name, ctx.message.author.discriminator)
            await self.bot.send_message(discord.utils.get(ctx.message.server.channels, name="mod-logs"), msg)
       except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(manage_messages=True)
    @commands.command(pass_context=True, name="unlock")
    async def unlock(self, ctx):
       """Unock message sending in the channel. Staff only."""
       try:
            everyone_role = discord.utils.get(ctx.message.server.roles, name="@everyone")
            overwrites = ctx.message.channel.overwrites_for(everyone_role)
            if overwrites.send_messages == None:
                await self.bot.say("🔓 Channel is already unlocked.")
                return
            overwrites.send_messages = None
            await self.bot.edit_channel_permissions(ctx.message.channel, everyone_role, overwrites)
            await self.bot.say("🔓 Channel unlocked.")
            msg = "🔓 **Unlock**: {0} by {1} | {2}#{3}".format(ctx.message.channel.mention, ctx.message.author.mention, ctx.message.author.name, ctx.message.author.discriminator)
            await self.bot.send_message(discord.utils.get(ctx.message.server.channels, name="mod-logs"), msg)
       except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

def setup(bot):
    bot.add_cog(Lockdown(bot))
