import discord
from discord.ext import commands
from cogs.checks import is_staff, check_staff_id


class Lockdown(commands.Cog):
    """
    Channel lockdown commands.
    """
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        return True

    @is_staff("HalfOP")
    @commands.command()
    async def lockdown(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        """Lock message sending in the channel. Staff only."""
        author = ctx.author
        elsewhere = self.bot.channels['elsewhere']
        if not channels:
            channels.append(ctx.channel)
        locked_down = []

        for c in channels:
            if c == elsewhere:
                everyone_role = self.bot.roles['#elsewhere']
            else:
                everyone_role = ctx.guild.default_role

            overwrites_everyone = c.overwrites_for(everyone_role)
            if overwrites_everyone.send_messages is False:
                await ctx.send(f"🔒 {c.mention} is already locked down. Use `.unlock` to unlock.")
                continue

            overwrites_everyone.send_messages = False

            try:
                await c.set_permissions(everyone_role, overwrite=overwrites_everyone)
            except discord.errors.Forbidden:
                await ctx.send(f"💢 I don't have permission to do this for {c.mention}.")
                continue

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
        elsewhere = self.bot.channels['elsewhere']
        if not channels:
            channels.append(ctx.channel)
        locked_down = []

        for c in channels:

            if c == elsewhere:
                everyone_role = self.bot.roles['#elsewhere']
            else:
                everyone_role = ctx.guild.default_role

            overwrites_everyone = c.overwrites_for(everyone_role)
            overwrites_staff = c.overwrites_for(self.bot.roles['Staff'])
            if overwrites_staff.send_messages is False:
                await ctx.send(f"🔒 {c.mention} is already locked down. Use `.unlock` to unlock.")
                continue

            overwrites_everyone.send_messages = False
            overwrites_staff.send_messages = False

            try:
                await c.set_permissions(everyone_role, overwrite=overwrites_everyone)
                await c.set_permissions(self.bot.roles['Staff'], overwrite=overwrites_staff)
            except discord.errors.Forbidden:
                await ctx.send(f"💢 I don't have permission to do this for {c.mention}.")
                continue

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
        elsewhere = self.bot.channels['elsewhere']
        if not channels:
            channels.append(ctx.channel)
        locked_down = []
        ishelper = not await check_staff_id(ctx, "HalfOP", author.id)

        for c in channels:
            if ishelper and (c not in self.bot.assistance_channels):
                await ctx.send(f"{ctx.author.mention} {c.mention} can't be locked by a helper.")
                continue
            if c == elsewhere:
                everyone_role = self.bot.roles['#elsewhere']
            else:
                everyone_role = ctx.guild.default_role

            overwrites_everyone = c.overwrites_for(everyone_role)
            overwrites_helpers = c.overwrites_for(self.bot.roles['Helpers'])
            if overwrites_everyone.send_messages is False:
                await ctx.send(f"🔒 {c.mention} is already locked down. Use `.unlock` to unlock.")
                continue

            overwrites_everyone.send_messages = False
            overwrites_helpers.send_messages = ishelper

            try:
                await c.set_permissions(everyone_role, overwrite=overwrites_everyone)
                await c.set_permissions(self.bot.roles['Helpers'], overwrite=overwrites_helpers)
            except discord.errors.Forbidden:
                await ctx.send(f"💢 I don't have permission to do this for {c.mention}.")
                continue

            await c.send("🔒 Channel locked.")
            locked_down.append(c)

        if locked_down:
            msg = f"🔒 **Soft-lock**: {ctx.author.mention} soft-locked channels | {author}\n📝 __Channels__: {', '.join(c.mention for c in locked_down)}"
            await self.bot.channels['mod-logs'].send(msg)

    @is_staff('Helper')
    @commands.command()
    async def unlock(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        """Unlock message sending in the channel. Staff only and Helpers only."""
        author = ctx.author
        elsewhere = self.bot.channels['elsewhere']
        if not channels:
            channels.append(ctx.channel)
        ishelper = not await check_staff_id(ctx, "HalfOP", author.id)
        unlocked = []

        for c in channels:
            if ishelper and c not in self.bot.assistance_channels:
                await ctx.send(f"{ctx.author.mention} {c.mention} can't be unlocked by a helper.")
                continue
            if c == elsewhere:
                everyone_role = self.bot.roles['#elsewhere']
                perm = True
            else:
                everyone_role = ctx.guild.default_role
                perm = None

            overwrites_everyone = c.overwrites_for(everyone_role)
            overwrites_staff = c.overwrites_for(self.bot.roles['Staff'])
            overwrites_helpers = c.overwrites_for(self.bot.roles['Helpers'])
            if overwrites_everyone.send_messages is not False:
                await ctx.send(f"🔓 {c.mention} is already unlocked.")
                continue

            overwrites_everyone.send_messages = perm
            overwrites_staff.send_messages = True
            if c == elsewhere:
                overwrites_helpers.send_messages = True
            else:
                overwrites_helpers.send_messages = None

            try:
                await c.set_permissions(everyone_role, overwrite=overwrites_everyone)
                await c.set_permissions(self.bot.roles['Helpers'], overwrite=overwrites_helpers)
                await c.set_permissions(self.bot.roles['Staff'], overwrite=overwrites_staff)
            except discord.errors.Forbidden:
                await ctx.send(f"💢 I don't have permission to do this for {c.mention}.")
                continue

            await c.send("🔓 Channel unlocked.")
            unlocked.append(c)
        if unlocked:
            msg = f"🔓 **Unlock**: {ctx.author.mention} unlocked channels | {author}\n📝 __Channels__: {', '.join(c.mention for c in unlocked)}"
            await self.bot.channels['mod-logs'].send(msg)


def setup(bot):
    bot.add_cog(Lockdown(bot))
