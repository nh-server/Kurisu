import re
from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from .data import ctr, nin
from .util import Extension

if TYPE_CHECKING:
    from kurisu2 import Kurisu2

ctr_errcode_url = 'http://en-americas-support.nintendo.com/app/answers/list/p/430/kw/{}/sno/0'
wup_errcode_url = 'http://en-americas-support.nintendo.com/app/answers/list/p/431/kw/{}/search/1'
hac_errcode_url = 'http://en-americas-support.nintendo.com/app/answers/list/p/897/kw/{}/sno/0'


def get_name(d, k, show_unknown=False):
    if k in d:
        return '{} ({})'.format(d[k], k)
    else:
        if show_unknown:
            return '_Unknown {}_ ({})'.format(show_unknown, k)  # crappy method
        else:
            return '{}'.format(k)


# noinspection PyDunderSlots
class ErrorCodes(Extension):
    """Explains error codes that happen on Nintendo consoles."""

    @commands.command(name='err')
    async def show_error(self, ctx: commands.Context, err: str):
        if re.match(r'[0-1][0-9][0-9]\-[0-9][0-9][0-9][0-9]', err):
            embed = discord.Embed(title=f'{err}: {"Nintendo 3DS" if err[0] == "0" else "Wii U"}')
            embed.url = (ctr_errcode_url if err[0] == "0" else wup_errcode_url).format(err)
            if err not in nin.ctrwup:
                embed.description = "I don't know this one! Click the error code for details on Nintendo " \
                                    "Support.\n\nIf you keep getting this issue and Nintendo Support does not help, " \
                                    "or know how to fix it, you should report relevant details to " \
                                    "<@78465448093417472> so it can be added to the bot. "
            else:
                embed.description = nin.ctrwup[err]
                embed.color = (discord.Color(0xCE181E) if err[0] == "0" else discord.Color(0x009AC7))
        elif re.match(r'[0-9][0-9][0-9][0-9]\-[0-9][0-9][0-9][0-9]', err):
            embed = discord.Embed(title=err + ": Nintendo Switch")
            embed.url = 'http://en-americas-support.nintendo.com/app/answers/landing/p/897'
            embed.color = discord.Color(0xE60012)
            if re.match(r'2110\-1[0-9][0-9][0-9]', err):
                embed.url = 'http://en-americas-support.nintendo.com/app/answers/detail/a_id/22594'
                embed.description = 'General connection error.'
            elif re.match(r'2110\-29[0-9][0-9]', err):
                embed.url = 'http://en-americas-support.nintendo.com/app/answers/detail/a_id/22277/p/897'
                embed.description = 'General connection error.'
            elif re.match(r'2110\-2[0-8][0-9][0-9]', err):
                embed.url = 'http://en-americas-support.nintendo.com/app/answers/detail/a_id/22263/p/897'
                embed.description = 'General connection error.'
            else:
                if err in nin.hac:
                    embed.url = nin.hac[err][1]
                    embed.description = nin.hac[err][0]
                    if nin.hac[err][1] is None:
                        embed.description += ' (No known support page)'
                else:
                    embed.color = embed.Empty
                    embed.url = hac_errcode_url.format(err)
                    embed.description = "I don't know this one! Click the error code for details on Nintendo " \
                                        "Support.\n\nIf you keep getting this issue and Nintendo Support does not " \
                                        "help, and know how to fix it, you should report relevant details to " \
                                        "<@78465448093417472> so it can be added to the bot. "
        else:
            err = err.strip()
            if err.startswith("0x"):
                err = err[2:]
            try:
                rc = int(err, 16)
            except ValueError:
                await ctx.send('Failed to convert errcode to int.')
                return
            desc = rc & 0x3FF
            mod = (rc >> 10) & 0xFF
            summ = (rc >> 21) & 0x3F
            level = (rc >> 27) & 0x1F

            # garbage
            embed = discord.Embed(title="0x{:X}".format(rc))
            embed.add_field(name="Module", value=get_name(ctr.modules, mod), inline=False)
            embed.add_field(name="Description", value=get_name(ctr.descriptions, desc), inline=False)
            embed.add_field(name="Summary", value=get_name(ctr.summaries, summ), inline=False)
            embed.add_field(name="Level", value=get_name(ctr.levels, level), inline=False)
        await ctx.send(embed=embed)


def setup(bot: 'Kurisu2'):
    bot.add_cog(ErrorCodes(bot))
