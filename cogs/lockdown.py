import discord
from discord.ext import commands
from cogs.checks import is_staff, check_staff

@commands.guild_only()
class Lockdown(commands.Cog):
    """
    Channel lockdown commands.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Cog "{}" loaded'.format(self.__class__.__name__))

    @is_staff("HalfOP")
    @commands.command()
    async def lockdown(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        """Lock message sending in the channel. Staff only."""
        if not channels:
            channels.append(ctx.channel)
        locked_down = []
        for c in channels:
            if c.overwrites_for(self.bot.everyone_role) is False:
                await ctx.send("🔒 {} is already locked down. Use `.unlock` to unlock.".format(c.mention))
                continue
            try:
                await c.set_permissions(self.bot.everyone_role, send_messages=False)
            except discord.errors.Forbidden:
                await ctx.send("💢 I don't have permission to do this.")
            await c.send("🔒 Channel locked down. Only staff members may speak. Do not bring the topic to other channels or risk disciplinary actions.")
            locked_down.append(c)
        if locked_down:
            msg = "🔒 **Lockdown**: {1} locked down channels | {2}#{3}\n📝 __Channels__: {0}".format(', '.join(c.mention for c in locked_down), ctx.author.mention, ctx.author.name, ctx.author.discriminator)
            await self.bot.modlogs_channel.send(msg)
        
    @is_staff("Owner")
    @commands.command()
    async def slockdown(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        """Lock message sending in the channel for everyone. Owners only."""
        if not channels:
            channels.append(ctx.channel)
        locked_down = []
        for c in channels:
            if c.overwrites_for(self.bot.staff_role).send_messages is False:
                await ctx.send("🔒 {} is already locked down. Use `.unlock` to unlock.".format(c.mention))
                continue
            try:
                await c.set_permissions(self.bot.everyone_role, send_messages=False)
                await c.set_permissions(self.bot.staff_role, send_messages=False)
            except discord.errors.Forbidden:
                await ctx.send("💢 I don't have permission to do this.")
            await c.send("🔒 Channel locked down. Only owners members may speak. Do not bring the topic to other channels or risk disciplinary actions.")
            locked_down.append(c)
        if locked_down:
            msg = "🔒 **Super lockdown**: {1} locked down channels | {2}#{3}\n📝 __Channels__: {0}".format(', '.join(c.mention for c in locked_down), ctx.author.mention, ctx.author.name, ctx.author.discriminator)
            await self.bot.modlogs_channel.send(msg)

    @is_staff('Helper')
    @commands.command()
    async def softlock(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        """Lock message sending in the channel, without the "disciplinary action" note. Staff and Helpers only."""
        if not channels:
            channels.append(ctx.channel)
        locked_down = []
        ishelper= not check_staff(ctx.author.id, "HalfOP")
        for c in channels:
            if (ishelper) and (c not in self.bot.assistance_channels):
                await ctx.send("{0} {1} can't be locked by a helper.".format(ctx.author.mention, c.mention))
                continue
            if c.overwrites_for(self.bot.everyone_role).send_message is False:
                await ctx.send("🔒 {} is already locked down. Use `.unlock` to unlock.".format(c.mention))
                continue
            try:
                await c.set_permissions(self.bot.everyone_role, send_messages=False)
                await c.set_permissions(self.bot.helpers_role, send_messages=ishelper)
            except discord.errors.Forbidden:
                await ctx.send("💢 I don't have permission to do this.")
            await c.send("🔒 Channel locked.")
            locked_down.append(c)
        if len(locked_down):
            msg = "🔒 **Soft-lock**: {1} soft-locked channels | {2}#{3}\n📝 __Channels__: {0}".format(', '.join(c.mention for c in locked_down), ctx.author.mention, ctx.author.name, ctx.author.discriminator)
            await self.bot.modlogs_channel.send(msg)


    @is_staff('Helper')
    @commands.command()
    async def unlock(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        """Unlock message sending in the channel. Staff only and Helpers only."""
        if not channels:
            channels.append(ctx.channel)
        ishelper= not check_staff(ctx.author.id, "HalfOP")
        try:
            if len(ctx.channel_mentions) == 0:
                channels = [ctx.channel]
                if (ishelper) and (ctx.channel not in self.bot.assistance_channels):
                    msg = "{0} Helpers cannot use this command outside of the assistance channels.".format(issuer.mention)
                    await ctx.send(msg)
                    return
            else:
                channels = ctx.channel_mentions
            unlocked = []
            for c in channels:
                if (ishelper) and (c not in self.bot.assistance_channels):
                    await ctx.send("{0} {1} can't be unlocked by a helper.".format(issuer.mention, c.mention))	
                    return
                overwrites_everyone = c.overwrites_for(self.bot.everyone_role)
                overwrites_staff = c.overwrites_for(self.bot.staff_role)
                overwrites_helpers = c.overwrites_for(self.bot.helpers_role)
                if c.overwrites_for(self.bot.everyone_role).send_messages is None:
                    await ctx.send("🔓 {} is already unlocked.".format(c.mention))
                    return
                overwrites_everyone.send_messages = None
                overwrites_staff.send_messages = True                
                overwrites_helpers.send_messages = None
                await c.set_permissions(self.bot.everyone_role, send_messages=None)
                await c.set_permissions(self.bot.helpers_role, send_messages=True)
                await c.set_permissions(self.bot.staff_role, send_messages=None)
                await c.send("🔓 Channel unlocked.")
                unlocked.append(c)
            if unlocked:
                msg = "🔓 **Unlock**: {1} unlocked channels | {2}#{3}\n📝 __Channels__: {0}".format(', '.join(c.mention for c in unlocked), ctx.author.mention, ctx.author.name, ctx.author.discriminator)
                await self.bot.modlogs_channel.send(msg)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

def setup(bot):
    bot.add_cog(Lockdown(bot))
