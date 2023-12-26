from __future__ import annotations

import discord
import hashlib
import re
import struct

from discord.ext import commands
from typing import TYPE_CHECKING, Literal
from utils.utils import send_dm_message

if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.context import KurisuContext, GuildContext


class FriendCode(commands.Cog):
    """
    Stores and obtains friend codes for sharing.
    """

    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.emoji = discord.PartialEmoji.from_str('🤝')
        self.extras = bot.extras

    # based on https://github.com/megumisonoda/SaberBot/blob/master/lib/saberbot/valid_fc.rb
    def verify_3ds_fc(self, fc_str: str):
        try:
            fc = int(fc_str.replace('-', ''))
        except ValueError:
            return None
        if fc > 0x7FFFFFFFFF:
            return None
        principal_id = fc & 0xFFFFFFFF
        checksum = (fc & 0xFF00000000) >> 32
        return fc if hashlib.sha1(struct.pack('<L', principal_id)).digest()[0] >> 1 == checksum else None

    def verify_switch_fc(self, fc: str):
        if re.fullmatch(r"SW(?:-\d{4}){3}", fc):
            return int(fc[2:].replace('-', ''))
        return None

    def n3ds_fc_to_string(self, fc: int):
        fc_str = str(fc).rjust(12, '0')
        return f"{fc_str[0:4]} - {fc_str[4:8]} - {fc_str[8:12]}"

    def switch_fc_to_string(self, fc: int):
        fc_str = str(fc).rjust(12, '0')
        return f"SW - {fc_str[0:4]} - {fc_str[4:8]} - {fc_str[8:12]}"

    @commands.command()
    async def fcregister(self, ctx: KurisuContext, fc_str: str):
        """Add your friend code."""
        console = "Switch" if fc_str.startswith("SW") else "3DS"
        fc = self.verify_3ds_fc(fc_str) if console == "3DS" else self.verify_switch_fc(fc_str)
        if fc is None:
            await ctx.send("This friend code is invalid. Switch friend codes must be "
                           "in a SW-XXXX-XXXX-XXXX format and 3DS friends codes in a XXXX-XXXX-XXXX format.")
            return
        fcs = await self.extras.get_friend_code(ctx.author.id)
        if fcs and (fcs.fc_3ds and console == "3DS" or fcs.fc_switch and console == "Switch"):
            await ctx.send(f"Please delete your current {console} friend code with `.fcdelete {console}` before adding another.")
            return
        if console == "3DS":
            await self.bot.extras.add_3ds_friend_code(ctx.author, fc)
        else:
            await self.extras.add_switch_friend_code(ctx.author, fc)
        await ctx.send(f"{ctx.author.mention} {console} friend code inserted: {self.n3ds_fc_to_string(fc) if console == '3DS' else self.switch_fc_to_string(fc)}")

    @commands.guild_only()
    @commands.command()
    async def fcquery(self, ctx: GuildContext, member: discord.Member):
        """Get other user's friend codes. You must have one yourself in the database."""

        author_fc = await self.extras.get_friend_code(ctx.author.id)
        target_fc = await self.extras.get_friend_code(member.id)
        if not author_fc:
            return await ctx.send("You need to register your own friend code with `.fcregister <friendcode>` before getting others.")
        if not target_fc:
            return await ctx.send("This user does not have a registered friend code.")

        fcs_a = ""
        fcs_t = ""
        fc_3ds = "3DS: {0} \n"
        fc_switch = "Switch: {0}"

        if author_fc.fc_3ds:
            fcs_a += fc_3ds.format(self.n3ds_fc_to_string(author_fc.fc_3ds))
        if author_fc.fc_switch:
            fcs_a += fc_switch.format(self.switch_fc_to_string(author_fc.fc_switch))

        if target_fc.fc_3ds:
            fcs_t += fc_3ds.format(self.n3ds_fc_to_string(target_fc.fc_3ds))
        if target_fc.fc_switch:
            fcs_t += fc_switch.format(self.switch_fc_to_string(target_fc.fc_switch))

        await ctx.send(f"{member.mention}'s friend codes are\n{fcs_t}")
        await send_dm_message(member, f"{ctx.author} has asked for your friend codes! Their codes are\n{fcs_a}")

    @commands.command()
    async def fcdelete(self, ctx: KurisuContext, console: Literal['3DS', 'Switch']):
        """Delete your friend code."""
        if console == '3DS':
            await self.extras.delete_3ds_friend_code(ctx.author.id)
        elif console == 'Switch':
            await self.extras.delete_switch_friend_code(ctx.author.id)
        else:
            return await ctx.send("Invalid console.")
        await ctx.send(f"Your {console} friend code was removed from the database.")

    @commands.command()
    async def fctest_3ds(self, ctx: KurisuContext, fc):
        """Test a 3DS friend code."""
        fc = self.verify_3ds_fc(fc)
        if fc:
            await ctx.send(self.n3ds_fc_to_string(fc))
        else:
            await ctx.send("Invalid.")

    @commands.command()
    async def fctest_switch(self, ctx: KurisuContext, fc):
        """Test a Switch friend code."""
        fc = self.verify_switch_fc(fc)
        if fc:
            await ctx.send(self.switch_fc_to_string(fc))
        else:
            await ctx.send("Invalid.")


async def setup(bot):
    await bot.add_cog(FriendCode(bot))
