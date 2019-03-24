import discord
from discord.ext import commands
from cogs.checks import is_staff, check_staff_id


@commands.guild_only()
class Lockdown(commands.Cog):
    """
    Channel lockdown commands.
    """
    def __init__(self, bot):
        self.bot = bot
        print(f'Cog "{self.qualified_name}" loaded')

    async def cog_check(self, ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        return True

    @is_staff("HalfOP")
    @commands.command()
    async def lockdown(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        """Lock message sending in the channel. Staff only."""
        author = ctx.author
        if not channels:
            channels.append(ctx.channel)
        locked_down = []
        for c in channels:
            if c.overwrites_for(ctx.guild.default_role) is False:
                await ctx.send(f"🔒 {c.mention} is already locked down. Use `.unlock` to unlock.")
                continue
            try:
                await c.set_permissions(ctx.guild.default_role, send_messages=False)
            except discord.errors.Forbidden:
                await ctx.send("💢 I don't have permission to do this.")
            await c.send("🔒 Channel locked down. Only staff members may speak. Do not bring the topic to other channels or risk disciplinary actions.")
            locked_down.append(c)
        if locked_down:
            msg = f"🔒 **Lockdown**: {ctx.author.mention} locked down channels | {author}\n📝 __Channels__: {', '.join(c.mention for c in locked_down)}"
            await self.bot.channels['mod-logs'].send(msg)

    @is_staff("Owner")
    @commands.command()
    async def slockdown(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        """Lock message sending in the channel for everyone. Owners only."""
        author = ctx.author
        if not channels:
            channels.append(ctx.channel)
        locked_down = []
        for c in channels:
            if c.overwrites_for(self.bot.roles['Staff']).send_messages is False:
                await ctx.send(f"🔒 {c.mention} is already locked down. Use `.unlock` to unlock.")
                continue
            try:
                await c.set_permissions(ctx.guild.default_role, send_messages=False)
                await c.set_permissions(self.bot.roles['Staff'], send_messages=False)
            except discord.errors.Forbidden:
                await ctx.send("💢 I don't have permission to do this.")
            await c.send("🔒 Channel locked down. Only owners members may speak. Do not bring the topic to other channels or risk disciplinary actions.")
            locked_down.append(c)
        if locked_down:
            msg = f"🔒 **Super lockdown**: {ctx.author.mention} locked down channels | {author}\n📝 __Channels__: {', '.join(c.mention for c in locked_down)}"
            await self.bot.channels['mod-logs'].send(msg)

    @is_staff('Helper')
    @commands.command()
    async def softlock(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        """Lock message sending in the channel, without the "disciplinary action" note. Staff and Helpers only."""
        author = ctx.author
        if not channels:
            channels.append(ctx.channel)
        locked_down = []
        ishelper = not await check_staff_id(ctx, "HalfOP", author.id)
        for c in channels:
            if ishelper and (c not in self.bot.assistance_channels):
                await ctx.send(f"{ctx.author.mention} {c.mention} can't be locked by a helper.")
                continue
            if c.overwrites_for(ctx.guild.default_role).send_messages is False:
                await ctx.send(f"🔒 {c.mention} is already locked down. Use `.unlock` to unlock.")
                continue
            try:
                await c.set_permissions(ctx.guild.default_role, send_messages=False)
                await c.set_permissions(self.bot.roles['Helpers'], send_messages=ishelper)
            except discord.errors.Forbidden:
                await ctx.send("💢 I don't have permission to do this.")
            await c.send("🔒 Channel locked.")
            locked_down.append(c)
        if len(locked_down):
            msg = f"🔒 **Soft-lock**: {ctx.author.mention} soft-locked channels | {author}\n📝 __Channels__: {', '.join(c.mention for c in locked_down)}"
            await self.bot.channels['mod-logs'].send(msg)

    @is_staff('Helper')
    @commands.command()
    async def unlock(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        """Unlock message sending in the channel. Staff only and Helpers only."""
        author = ctx.author
        if not channels:
            channels.append(ctx.channel)
        ishelper = not await check_staff_id(ctx, "HalfOP", author.id)
        try:
            unlocked = []
            for c in channels:
                if ishelper and c not in self.bot.assistance_channels:
                    await ctx.send(f"{ctx.author.mention} {c.mention} can't be unlocked by a helper.")
                    return
                overwrites_everyone = c.overwrites_for(ctx.guild.default_role)
                overwrites_staff = c.overwrites_for(self.bot.roles['Staff'])
                overwrites_helpers = c.overwrites_for(self.bot.roles['Helpers'])
                if c.overwrites_for(ctx.guild.default_role).send_messages is None:
                    await ctx.send(f"🔓 {c.mention} is already unlocked.")
                    return
                overwrites_everyone.send_messages = None
                overwrites_staff.send_messages = True
                overwrites_helpers.send_messages = None
                await c.set_permissions(ctx.guild.default_role, send_messages=None)
                await c.set_permissions(self.bot.roles['Helpers'], send_messages=True)
                await c.set_permissions(self.bot.roles['Staff'], send_messages=None)
                await c.send("🔓 Channel unlocked.")
                unlocked.append(c)
            if unlocked:
                msg = f"🔓 **Unlock**: {ctx.author.mention} unlocked channels | {author}\n📝 __Channels__: {', '.join(c.mention for c in unlocked)}"
                await self.bot.channels['mod-logs'].send(msg)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")


def setup(bot):
    bot.add_cog(Lockdown(bot))
