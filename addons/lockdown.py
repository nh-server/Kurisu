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

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True, name="lockdown")
    async def lockdown(self, ctx):
       """Lock message sending in the channel. Staff only."""
       try:
            overwrites_everyone = ctx.message.channel.overwrites_for(self.bot.everyone_role)
            if overwrites_everyone.send_messages == False:
                await self.bot.say("🔒 Channel is already locked down. Use `.unlock` to unlock.")
                return
            overwrites_everyone.send_messages = False
            await self.bot.edit_channel_permissions(ctx.message.channel, self.bot.everyone_role, overwrites_everyone)
            await self.bot.say("🔒 Channel locked down. Only staff members may speak. Do not bring the topic to other channels or risk disciplinary actions.")
            msg = "🔒 **Lockdown**: {0} by {1} | {2}#{3}".format(ctx.message.channel.mention, ctx.message.author.mention, ctx.message.author.name, ctx.message.author.discriminator)
            await self.bot.send_message(self.bot.modlogs_channel, msg)
       except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(administrator=True)
    @commands.command(pass_context=True, name="slockdown")
    async def slockdown(self, ctx):
       """Lock message sending in the channel for everyone. Owners only."""
       try:
            overwrites_everyone = ctx.message.channel.overwrites_for(self.bot.everyone_role)
            overwrites_staff = ctx.message.channel.overwrites_for(self.bot.staff_role)
            if overwrites_everyone.send_messages == False:
                await self.bot.say("🔒 Channel is already locked down. Use `.unlock` to unlock.")
                return
            overwrites_everyone.send_messages = False
            overwrites_staff.send_messages = False
            await self.bot.edit_channel_permissions(ctx.message.channel, self.bot.everyone_role, overwrites_everyone)
            await self.bot.edit_channel_permissions(ctx.message.channel, self.bot.staff_role, overwrites_staff)
            await self.bot.say("🔒 Channel locked down. Only owners members may speak. Do not bring the topic to other channels or risk disciplinary actions.")
            msg = "🔒 **Super lockdown**: {0} by {1} | {2}#{3}".format(ctx.message.channel.mention, ctx.message.author.mention, ctx.message.author.name, ctx.message.author.discriminator)
            await self.bot.send_message(self.bot.modlogs_channel, msg)
       except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True, name="softlock")
    async def softlock(self, ctx):
       """Lock message sending in the channel, without the "disciplinary action" note. Staff only."""
       try:
            overwrites_everyone = ctx.message.channel.overwrites_for(self.bot.everyone_role)
            if overwrites_everyone.send_messages == False:
                await self.bot.say("🔒 Channel is already locked down. Use `.unlock` to unlock.")
                return
            overwrites_everyone.send_messages = False
            await self.bot.edit_channel_permissions(ctx.message.channel, self.bot.everyone_role, overwrites_everyone)
            await self.bot.say("🔒 Channel locked.")
            msg = "🔒 **Soft-lock**: {0} by {1} | {2}#{3}".format(ctx.message.channel.mention, ctx.message.author.mention, ctx.message.author.name, ctx.message.author.discriminator)
            await self.bot.send_message(self.bot.modlogs_channel, msg)
       except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True, name="unlock")
    async def unlock(self, ctx):
       """Unlock message sending in the channel. Staff only."""
       try:
            overwrites_everyone = ctx.message.channel.overwrites_for(self.bot.everyone_role)
            overwrites_staff = ctx.message.channel.overwrites_for(self.bot.staff_role)
            if overwrites_everyone.send_messages == None:
                await self.bot.say("🔓 Channel is already unlocked.")
                return
            overwrites_everyone.send_messages = None
            overwrites_staff.send_messages = True
            await self.bot.edit_channel_permissions(ctx.message.channel, self.bot.everyone_role, overwrites_everyone)
            await self.bot.edit_channel_permissions(ctx.message.channel, self.bot.staff_role, overwrites_staff)
            await self.bot.say("🔓 Channel unlocked.")
            msg = "🔓 **Unlock**: {0} by {1} | {2}#{3}".format(ctx.message.channel.mention, ctx.message.author.mention, ctx.message.author.name, ctx.message.author.discriminator)
            await self.bot.send_message(self.bot.modlogs_channel, msg)
       except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

def setup(bot):
    bot.add_cog(Lockdown(bot))
