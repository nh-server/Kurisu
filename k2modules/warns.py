from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from kurisu2 import role_names, private_channels
from .util import Extension, MemberOrID, caller_id_as_default, check, ordinal, escape_name

if TYPE_CHECKING:
    from kurisu2 import Kurisu2


class Warns(Extension):
    """User warning commands."""

    @commands.command(name='warn')
    @check.check_for_position(staff=True, helper=True)
    async def add_warning(self, ctx: commands.Context, member: MemberOrID, *, reason: str):
        """Warn a member."""
        res = await self.warns.add_warning(member, ctx.author, reason)
        await ctx.send(f'{escape_name(member.display_if_exist)} was given their {ordinal(res)} warning.')

    @commands.command(name='delwarn')
    @check.check_for_position(staff=True)
    async def delete_warning(self, ctx: commands.Context, warn_id: int):
        """Delete a warn."""
        res = self.warns.delete_warning(warn_id=warn_id)
        if res[0] is True:
            await ctx.send(f'Warning {warn_id} removed from <@!{res[1].user_id}>.')
        else:
            await ctx.send(f'No warning with ID {warn_id} was found.')

    @commands.command(name='listwarns')
    @caller_id_as_default
    async def list_warnings(self, ctx: commands.Context, member: MemberOrID = None):
        """List warns for a member."""
        if member[1] != ctx.author:
            r: discord.Role
            if role_names['staff-role'] not in (r.name for r in ctx.author.roles):
                await ctx.send(f'{ctx.author.mention} You can only use this command on yourself.')
                return

        warns = sorted(self.warns.get_warnings(member), key=lambda x: x.warn_id)
        if not len(warns):
            await ctx.send(f'No warns found for {member.display_if_exist}.')
            return

        embed = discord.Embed()
        embed.set_author(name=f'Warns for {member.display_if_exist}',
                         icon_url=discord.Embed.Empty if member.member is None else member.member.avatar_url)
        for entry in warns:
            field = [f'Warn ID: {entry.warn_id}']
            if ctx.channel.name in private_channels:
                field.append(f'Issuer: <@!{entry.issuer}>')
            field.append('Reason: ' + entry.reason)
            embed.add_field(name=entry.date.strftime('%Y-%m-%d %H:%M:%S'), value='\n'.join(field))

        await ctx.send(embed=embed)

    @commands.command(name='clearwarns')
    @check.check_for_position(staff=True)
    async def clear_warnings(self, ctx: commands.Context, member: MemberOrID):
        """Remove all warnings from a user."""
        res = self.warns.delete_all_warnings(member)
        if res:
            await ctx.send(f'Removed all {res} warnings from {escape_name(member.display_if_exist)}.')
        else:
            await ctx.send(f'No warnings for {escape_name(member.display_if_exist)} were found.')


def setup(bot: 'Kurisu2'):
    bot.add_cog(Warns(bot))
