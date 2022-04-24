import discord

from discord.ext import commands
from utils import crud
from utils.checks import is_staff, check_staff_id


class Lockdown(commands.Cog):
    """
    Channel lockdown commands.
    """
    def __init__(self, bot):
        self.bot = bot
        self.emoji = discord.PartialEmoji.from_str('🔒')

    async def cog_check(self, ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        return True

    @is_staff("HalfOP")
    @commands.command()
    async def lockdown(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        """Lock message sending in the channel. Staff only."""

        author = ctx.author
        locked_down = []

        if not channels:
            channels.append(ctx.channel)

        for c in channels:

            dbchannel = await crud.get_dbchannel(c.id)
            if not dbchannel:
                dbchannel = await crud.add_dbchannel(c.id, c.name)

            if dbchannel.lock_level > 0:
                await ctx.send(f"🔒 {c.mention} is already locked down. Use `.unlock` to unlock.")
                continue

            default_role = ctx.guild.get_role(dbchannel.default_role) if dbchannel.default_role else ctx.guild.default_role
            overwrites_default = c.overwrites_for(default_role)

            if overwrites_default.send_messages is False or overwrites_default.read_messages is False:
                await ctx.send(f"Nothing would happen from locking {c.mention}")
                continue

            overwrites_default.send_messages = False

            try:
                await c.set_permissions(default_role, overwrite=overwrites_default)
            except discord.errors.Forbidden:
                await ctx.send(f"💢 I don't have permission to do this for {c.mention}.")
                continue

            await dbchannel.update(lock_level=2).apply()
            locked_down.append(c)
            await c.send("🔒 Channel locked down. Only staff members may speak. Do not bring the topic to other channels or risk disciplinary actions.")
        if locked_down:
            msg = f"🔒 **Lockdown**: {ctx.author.mention} locked down channels | {author}\n📝 __Channels__: {', '.join(c.mention for c in locked_down)}"
            await self.bot.channels['mod-logs'].send(msg)

    @is_staff("Owner")
    @commands.command()
    async def slockdown(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        """Lock message sending in the channel for everyone. Owners only."""

        author = ctx.author
        locked_down = []

        if not channels:
            channels.append(ctx.channel)

        for c in channels:

            dbchannel = await crud.get_dbchannel(c.id)
            if not dbchannel:
                dbchannel = await crud.add_dbchannel(c.id, c.name)

            if dbchannel.lock_level == 3:
                await ctx.send(f"🔒 {c.mention} is already locked down. Use `.unlock` to unlock.")
                continue

            default_role = ctx.guild.get_role(dbchannel.default_role) if dbchannel.default_role else ctx.guild.default_role
            overwrites_default = c.overwrites_for(default_role)
            overwrites_staff = c.overwrites_for(self.bot.roles['Staff'])
            overwrites_helper = c.overwrites_for(self.bot.roles['Helpers'])

            if overwrites_default.send_messages is False or overwrites_default.read_messages is False:
                await ctx.send(f"Nothing would happen from locking {c.mention}")
                continue

            overwrites_default.send_messages = False
            if not overwrites_helper.is_empty():
                overwrites_helper.send_messages = None if overwrites_helper.send_messages is True else overwrites_helper.send_messages
            if not overwrites_helper.is_empty():
                overwrites_staff.send_messages = None if overwrites_staff.send_messages is True else overwrites_helper.send_messages

            try:
                await c.set_permissions(default_role, overwrite=overwrites_default)
                if not overwrites_helper.is_empty():
                    await c.set_permissions(self.bot.roles['Helpers'], overwrite=overwrites_helper)
                if not overwrites_helper.is_empty():
                    await c.set_permissions(self.bot.roles['Staff'], overwrite=overwrites_staff)

            except discord.errors.Forbidden:
                await ctx.send(f"💢 I don't have permission to do this for {c.mention}.")
                continue
            await dbchannel.update(lock_level=3).apply()
            locked_down.append(c)
            await c.send("🔒 Channel locked down. Only owners members may speak. Do not bring the topic to other channels or risk disciplinary actions.")

        if locked_down:
            msg = f"🔒 **Lockdown**: {ctx.author.mention} locked down channels | {author}\n📝 __Channels__: {', '.join(c.mention for c in locked_down)}"
            await self.bot.channels['mod-logs'].send(msg)

    @is_staff('Helper')
    @commands.command()
    async def softlock(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        """Lock message sending in the channel, without the "disciplinary action" note. Staff and Helpers only."""

        author = ctx.author
        locked_down = []

        if not channels:
            channels.append(ctx.channel)

        ishelper = not await check_staff_id('HalfOP', author.id)

        for c in channels:

            if c not in self.bot.assistance_channels and ishelper:
                await ctx.send(f"{ctx.author.mention} {c.mention} can't be locked by a helper.")
                continue

            dbchannel = await crud.get_dbchannel(c.id)
            if not dbchannel:
                dbchannel = await crud.add_dbchannel(c.id, c.name)

            if dbchannel.lock_level > 0:
                await ctx.send(f"🔒 {c.mention} is already locked down. Use `.unlock` to unlock.")
                continue

            default_role = ctx.guild.get_role(dbchannel.default_role) if dbchannel.default_role else ctx.guild.default_role
            overwrites_default = c.overwrites_for(default_role)
            overwrites_helper = c.overwrites_for(self.bot.roles['Helpers'])

            if overwrites_default.send_messages is False or overwrites_default.read_messages is False:
                await ctx.send(f"Nothing would happen from locking {c.mention}")
                continue

            overwrites_default.send_messages = False

            if not overwrites_helper.is_empty():
                overwrites_helper.send_messages = ishelper

            try:
                await c.set_permissions(default_role, overwrite=overwrites_default)
                if not overwrites_helper.is_empty():
                    await c.set_permissions(self.bot.roles['Helpers'], overwrite=overwrites_helper)
            except discord.errors.Forbidden:
                await ctx.send(f"💢 I don't have permission to do this for {c.mention}.")
                continue

            await dbchannel.update(lock_level=1).apply()

            locked_down.append(c)
            await c.send("🔒 Channel locked.")

        if locked_down:
            msg = f"🔒 **Soft-lock**: {ctx.author.mention} soft-locked channels | {author}\n📝 __Channels__: {', '.join(c.mention for c in locked_down)}"
            await self.bot.channels['mod-logs'].send(msg)

    @is_staff('Helper')
    @commands.command()
    async def unlock(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        """Unlock message sending in the channel. Staff only and Helpers only."""
        author = ctx.author

        if not channels:
            channels.append(ctx.channel)

        ishelper = not await check_staff_id("HalfOP", author.id)
        unlocked = []

        for c in channels:
            if c not in self.bot.assistance_channels and ishelper:
                await ctx.send(f"{ctx.author.mention} {c.mention} can't be unlocked by a helper.")
                continue

            dbchannel = await crud.get_dbchannel(c.id)
            if not dbchannel or dbchannel.lock_level == 0:
                await ctx.send("This channel is not locked")
                continue

            default_role = ctx.guild.get_role(dbchannel.default_role) if dbchannel.default_role else ctx.guild.default_role
            overwrites_default = c.overwrites_for(default_role)
            overwrites_default.send_messages = None if default_role is ctx.guild.default_role else True

            if dbchannel.lock_level == 3:
                if not await check_staff_id('Owner', author.id):
                    await ctx.send(f"{ctx.author.mention} {c.mention} can't be unlocked by someone that's not an owner.")
                    continue

                overwrites_staff = c.overwrites_for(self.bot.roles['Staff'])
                overwrites_helper = c.overwrites_for(self.bot.roles['Helpers'])

                if not overwrites_helper.is_empty():
                    overwrites_helper.send_messages = True
                if not overwrites_staff.is_empty():
                    overwrites_staff.send_messages = True

                try:
                    await c.set_permissions(default_role, overwrite=overwrites_default)
                    if not overwrites_helper.is_empty():
                        await c.set_permissions(self.bot.roles['Helpers'], overwrite=overwrites_helper)
                    if not overwrites_staff.is_empty():
                        await c.set_permissions(self.bot.roles['Staff'], overwrite=overwrites_staff)
                except discord.errors.Forbidden:
                    await ctx.send(f"💢 I don't have permission to do this for {c.mention}.")
                    continue

            elif dbchannel.lock_level == 2:
                try:
                    await c.set_permissions(default_role, overwrite=overwrites_default)
                except discord.errors.Forbidden:
                    await ctx.send(f"💢 I don't have permission to do this for {c.mention}.")
                    continue
            else:
                try:
                    if c in self.bot.assistance_channels:
                        overwrites_helper = c.overwrites_for(self.bot.roles['Helpers'])
                        overwrites_helper.send_messages = None
                        await c.set_permissions(self.bot.roles['Helpers'], overwrite=overwrites_helper)
                    await c.set_permissions(default_role, overwrite=overwrites_default)
                except discord.errors.Forbidden:
                    await ctx.send(f"💢 I don't have permission to do this for {c.mention}.")
                    continue
            await c.send("🔓 Channel unlocked.")
            await dbchannel.update(lock_level=0).apply()
            unlocked.append(c)
        if unlocked:
            msg = f"🔓 **Unlock**: {ctx.author.mention} unlocked channels | {author}\n📝 __Channels__: {', '.join(c.mention for c in unlocked)}"
            await self.bot.channels['mod-logs'].send(msg)


def setup(bot):
    bot.add_cog(Lockdown(bot))
