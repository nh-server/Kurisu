import discord
from discord.ext import commands
from utils.database import DatabaseCog
from utils.checks import is_staff, check_if_user_can_ready

class Newcomers(DatabaseCog):
    """
    Handles auto-probation and commands related to the newcomers channel.
    """

    on_aliases = ('on', 'true', '1', 'enable')
    off_aliases = ('off', 'false', '0', 'disable')

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.init()) # We can't do proper init here.

    async def init(self):
        await self.bot.wait_until_all_ready()
        flag_name = 'auto_probation'

        self.autoprobate = await self.get_flag(flag_name)

        if self.autoprobate is None:
            self.autoprobate = False
            await self.add_flag(flag_name)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if self.autoprobate:
            await member.add_roles(self.bot.roles['Probation'], reason="Auto Probation")

    async def autoprobate_handler(self, ctx, enabled:bool=None):
        if enabled is not None:
            self.autoprobate = enabled
            await self.set_flag('auto_probation', enabled)

        inactive_text = f'**inactive**. ⚠️\nTo activate it, use `.autoprobate {" | ".join(self.on_aliases)}`.'
        active_text = f'**active**. ✅\nTo deactivate it, use `.autoprobate {" | ".join(self.off_aliases)}`.'
        await ctx.send(f'🔨 Auto-probation is {active_text if self.autoprobate else inactive_text}')

    @is_staff('OP')
    @commands.group(invoke_without_command=True, case_insensitive=True)
    async def autoprobate(self, ctx):
        """
        Manages auto-probation.
        on | true | 1 | enable: turns on auto-probation.
        off | false | 0 | disable: turns off auto-probation.
        To display the status of auto-probation, invoke with no subcommand.
        """
        await self.autoprobate_handler(ctx)

    @autoprobate.command(aliases=on_aliases, hidden=True)
    async def autoprobate_on(self, ctx):
        await self.autoprobate_handler(ctx, True)

    @autoprobate.command(aliases=off_aliases, hidden=True)
    async def autoprobate_off(self, ctx):
        await self.autoprobate_handler(ctx, False)

    @check_if_user_can_ready()
    @commands.guild_only()
    @commands.command(aliases=['ready'], cooldown=commands.Cooldown(rate=1, per=300.0, type=commands.BucketType.channel))
    async def ncready(self, ctx):
        """Alerts online staff to a ready request in newcomers."""

        await ctx.message.delete()

        await self.bot.channels['newcomers'].send(f'{str(ctx.author)} is ready for unprobation. @here\nID: {ctx.author.id}', allowed_mentions=discord.AllowedMentions(everyone=True))
        try:
            await ctx.author.send('✅ Online staff have been notified of your request.')
        except discord.errors.Forbidden:
            pass

def setup(bot):
    bot.add_cog(Newcomers(bot))

