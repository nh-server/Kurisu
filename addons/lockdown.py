import discord
from discord.ext import commands

class Lockdown:
    """
    Channel lockdown commands.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True, name="lockdown")
    async def lockdown(self, ctx, *, channels=""):
        """Lock message sending in the channel. Staff only."""
        try:
            if len(ctx.message.channel_mentions) == 0:
                channels = [ctx.message.channel]
            else:
                channels = ctx.message.channel_mentions

            locked_down = []
            for c in channels:
                overwrites_everyone = c.overwrites_for(self.bot.everyone_role)
                if overwrites_everyone.send_messages is False:
                    await self.bot.say("🔒 {} is already locked down. Use `.unlock` to unlock.".format(c.mention))
                    continue
                overwrites_everyone.send_messages = False
                await self.bot.edit_channel_permissions(c, self.bot.everyone_role, overwrites_everyone)
                await self.bot.send_message(c, "🔒 Channel locked down. Only staff members may speak. Do not bring the topic to other channels or risk disciplinary actions.")
                locked_down.append(c)
            msg = "🔒 **Lockdown**: {1} locked down channels | {2}#{3}\n📝 __Channels__: {0}".format(', '.join(c.mention for c in locked_down), ctx.message.author.mention, ctx.message.author.name, ctx.message.author.discriminator)
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(administrator=True)
    @commands.command(pass_context=True, name="slockdown")
    async def slockdown(self, ctx, *, channels=""):
        """Lock message sending in the channel for everyone. Owners only."""
        try:
            if len(ctx.message.channel_mentions) == 0:
                channels = [ctx.message.channel]
            else:
                channels = ctx.message.channel_mentions

            locked_down = []
            for c in channels:
                overwrites_everyone = c.overwrites_for(self.bot.everyone_role)
                overwrites_staff = c.overwrites_for(self.bot.everyone_role)
                if overwrites_staff.send_messages is False:
                    await self.bot.say("🔒 {} is already locked down. Use `.unlock` to unlock.".format(c.mention))
                    continue
                overwrites_everyone.send_messages = False
                overwrites_staff.send_messages = False
                await self.bot.edit_channel_permissions(c, self.bot.everyone_role, overwrites_everyone)
                await self.bot.edit_channel_permissions(c, self.bot.staff_role, overwrites_staff)
                await self.bot.send_message(c, "🔒 Channel locked down. Only owners members may speak. Do not bring the topic to other channels or risk disciplinary actions.")
                locked_down.append(c)
            msg = "🔒 **Super lockdown**: {1} locked down channels | {2}#{3}\n📝 __Channels__: {0}".format(', '.join(c.mention for c in locked_down), ctx.message.author.mention, ctx.message.author.name, ctx.message.author.discriminator)
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True, name="softlock")
    async def softlock(self, ctx, *, channels=""):
        """Lock message sending in the channel, without the "disciplinary action" note. Staff only."""
        try:
            if len(ctx.message.channel_mentions) == 0:
                channels = [ctx.message.channel]
            else:
                channels = ctx.message.channel_mentions

            locked_down = []
            for c in channels:
                overwrites_everyone = c.overwrites_for(self.bot.everyone_role)
                if overwrites_everyone.send_messages is False:
                    await self.bot.say("🔒 {} is already locked down. Use `.unlock` to unlock.".format(c.mention))
                    continue
                overwrites_everyone.send_messages = False
                await self.bot.edit_channel_permissions(c, self.bot.everyone_role, overwrites_everyone)
                await self.bot.send_message(c, "🔒 Channel locked.")
                locked_down.append(c)
            msg = "🔒 **Soft-lock**: {1} soft-locked channels | {2}#{3}\n📝 __Channels__: {0}".format(', '.join(c.mention for c in locked_down), ctx.message.author.mention, ctx.message.author.name, ctx.message.author.discriminator)
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True, name="unlock")
    async def unlock(self, ctx, *, channels=""):
        """Unlock message sending in the channel. Staff only."""
        try:
            if len(ctx.message.channel_mentions) == 0:
                channels = [ctx.message.channel]
            else:
                channels = ctx.message.channel_mentions

            unlocked = []
            for c in channels:
                overwrites_everyone = c.overwrites_for(self.bot.everyone_role)
                overwrites_staff = c.overwrites_for(self.bot.staff_role)
                if overwrites_everyone.send_messages is None:
                    await self.bot.say("🔓 {} is already unlocked.".format(c.mention))
                    return
                overwrites_everyone.send_messages = None
                overwrites_staff.send_messages = True
                await self.bot.edit_channel_permissions(c, self.bot.everyone_role, overwrites_everyone)
                await self.bot.edit_channel_permissions(c, self.bot.staff_role, overwrites_staff)
                await self.bot.send_message(c, "🔓 Channel unlocked.")
                unlocked.append(c)
            msg = "🔓 **Unlock**: {1} unlocked channels | {2}#{3}\n📝 __Channels__: {0}".format(', '.join(c.mention for c in unlocked), ctx.message.author.mention, ctx.message.author.name, ctx.message.author.discriminator)
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

def setup(bot):
    bot.add_cog(Lockdown(bot))
