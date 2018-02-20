import discord
from discord.ext import commands

from kurisu2 import Kurisu2, role_names, private_channels
from .util import Extension, ordinal


# could this be made better?
def get_warn_action(count: int) -> str:
    if count <= 2:
        return 'nothing'
    elif count <= 4:
        return 'kick'
    else:
        return 'ban'


class Warns(Extension):
    """User warning commands."""

    # TODO: add name= to the commands, and set the function names to something more descriptive

    @commands.command(name='warn')
    async def add_warning(self, ctx: commands.Context, member: discord.Member, *, reason: str):
        """Warn a member."""
        res = self.warns.add_warning(user_id=member.id, issuer=ctx.author.id, reason=reason)
        if res[0] is True:
            await ctx.send(f'{member.mention} was given their {ordinal(res[1])} warning.')
            action = get_warn_action(res[1])
            if action == 'kick':
                await member.kick(reason=f'Reached {res[1]} warns')
            elif action == 'ban':
                await member.ban(reason=f'Reached {res[1]} warns')
        else:
            await ctx.send('Failed to add a warning! This should never happen!')

    @commands.command(name='delwarn')
    async def delete_warning(self, ctx: commands.Context, snowflake: int):
        """Delete a warn."""
        # TODO: delwarn

    @commands.command(name='listwarns')
    async def list_warnings(self, ctx: commands.Context, member: discord.Member = None):
        """List warns for a member."""

        if member is None:
            member = ctx.author
        await ctx.send(f'member: {member}')
        if member != ctx.author:
            r: discord.Role
            if role_names['staff-role'] not in (r.name for r in ctx.author.roles):
                await ctx.send(f"{ctx.author.mention} You can only use this command on yourself.")
                return

        embed = discord.Embed()
        embed.set_author(name=f'Warns for {member}', icon_url=member.avatar_url)
        warns = list(self.warns.get_warnings(user_id=member.id))
        warns.sort(key=lambda x: x.warn_id)
        for entry in warns:
            field = [f'Warn ID: {entry.warn_id}']
            if ctx.channel.name in private_channels:
                field.append(f'Issuer: <@!{entry.issuer}>')
            field.append('Reason: ' + entry.reason)
            embed.add_field(name=entry.date.strftime('%Y-%m-%d %H:%M:%S'), value='\n'.join(field))

        # await ctx.send(f'```py\n{embed.to_dict()}\n```')
        await ctx.send(embed=embed)


def setup(bot: Kurisu2):
    bot.add_cog(Warns(bot))
