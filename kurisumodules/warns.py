import discord
from discord.ext import commands

from kurisu2 import Kurisu2, role_names
from .util import ExtensionBase, ordinal


# could this be made better?
def get_warn_action(count: int) -> str:
    if count <= 2:
        return 'nothing'
    elif count <= 4:
        return 'kick'
    else:
        return 'ban'


class Warns(ExtensionBase):
    """User warning commands."""

    @commands.command()
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason: str):
        """Warn a user."""
        res = self.bot.warns.add_warning(user_id=member.id, reason=reason)
        if res[0] is True:
            await ctx.send(f'{member.mention} was given their {ordinal(res[1])} warning.')
            action = get_warn_action(res[1])
            if action == 'kick':
                await member.kick(reason=f'Reached {res[1]} warns')
            elif action == 'ban':
                await member.ban(reason=f'Reached {res[1]} warns')
        else:
            await ctx.send('Failed to add a warning! This should never happen!')

    @commands.command()
    async def delwarn(self, ctx: commands.Context, snowflake: int):
        """Delete a warn."""
        # TODO: delwarn

    @commands.command()
    async def listwarns(self, ctx: commands.Context, member: discord.Member = None):
        await ctx.send(f'member: {member}')
        if member is None:
            member = ctx.author
        if member != ctx.author:
            r: discord.Role
            if role_names['staff-role'] not in (r.name for r in member.roles):
                await ctx.send(f"{member.mention} You can only use this command on yourself.")
                return
        # TODO: listwarns


def setup(bot: Kurisu2):
    bot.add_cog(Warns(bot))
