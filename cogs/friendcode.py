from __future__ import annotations

import discord
import hashlib
import re
import struct

from discord.ext import commands
from typing import TYPE_CHECKING
from utils import crud, utils

if TYPE_CHECKING:
    from kurisu import Kurisu


class FriendCode(commands.Cog):
    """
    Stores and obtains friend codes for sharing.
    """

    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.emoji = discord.PartialEmoji.from_str('🤝')

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
        fc_str = str(fc)
        return f"SW - {fc_str[0:4]} - {fc_str[4:8]} - {fc_str[8:12]}"

    @commands.command()
    async def fcregister(self, ctx: commands.Context, fc_str: str):
        """Add your friend code."""
        console = "switch" if fc_str.startswith("SW") else "3ds"
        fc = self.verify_3ds_fc(fc_str) if console == "3ds" else self.verify_switch_fc(fc_str)
        if fc is None:
            await ctx.send("This friend code is invalid. Switch friend codes must be in a SW-XXXX-XXXX-XXXX format and 3ds friends codes in a XXXX-XXXX-XXXX format.")
            return
        fcs = await crud.get_friendcode(ctx.author.id)
        if fcs and (fcs.fc_3ds and console == "3ds" or fcs.fc_switch and console == "switch"):
            await ctx.send(f"Please delete your current {console} friend code with `.fcdelete {console}` before adding another.")
            return
        if console == "3ds":
            await crud.add_friendcode_3ds(ctx.author.id, fc)
        else:
            await crud.add_friendcode_switch(ctx.author.id, fc)
        await ctx.send(f"{ctx.author.mention} {console} friend code inserted: {self.n3ds_fc_to_string(fc) if console=='3ds' else self.switch_fc_to_string(fc)}")

    @commands.guild_only()
    @commands.command()
    async def fcquery(self, ctx: commands.Context, member: discord.Member):
        """Get other user's friend codes. You must have one yourself in the database."""

        if not (friend_code := await crud.get_friendcode(ctx.author.id)):
            return await ctx.send("You need to register your own friend code with `.fcregister <friendcode>` before getting others.")
        if not (friend_code_m := await crud.get_friendcode(member.id)):
            return await ctx.send("This user does not have a registered friend code.")

        fcs = ""
        fcs_m = ""
        fc_3ds = "3ds: {0} \n"
        fc_switch = "switch: {0}"

        if friend_code.fc_3ds:
            fcs += fc_3ds.format(self.n3ds_fc_to_string(friend_code.fc_3ds))
        if friend_code.fc_switch:
            fcs += fc_switch.format(self.switch_fc_to_string(friend_code.fc_switch))

        if friend_code_m.fc_3ds:
            fcs_m += fc_3ds.format(self.n3ds_fc_to_string(friend_code.fc_3ds))
        if friend_code_m.fc_switch:
            fcs_m += fc_switch.format(self.switch_fc_to_string(friend_code.fc_switch))

        await ctx.send(f"{member.mention} friend codes are\n{fcs}")
        await utils.send_dm_message(member, f"{ctx.author} has asked for your friend codes! Their codes are\n{fcs_m}")

    @commands.command()
    async def fcdelete(self, ctx: commands.Context, console: str):
        """Delete your friend code."""
        if console == '3ds':
            await crud.delete_friendcode_3ds(ctx.author.id)
        elif console == 'switch':
            await crud.delete_friendcode_switch(ctx.author.id)
        else:
            return await ctx.send("Invalid console.")
        await ctx.send(f"Your {console} friend code was removed from the database.")

    @commands.command()
    async def fctest_3ds(self, ctx: commands.Context, fc):
        """Test a 3ds friend code."""
        fc = self.verify_3ds_fc(fc)
        if fc:
            await ctx.send(self.n3ds_fc_to_string(fc))
        else:
            await ctx.send("Invalid.")

    @commands.command()
    async def fctest_switch(self, ctx: commands.Context, fc):
        """Test a switch friend code."""
        fc = self.verify_switch_fc(fc)
        if fc:
            await ctx.send(self.switch_fc_to_string(fc))
        else:
            await ctx.send("Invalid.")


async def setup(bot):
    await bot.add_cog(FriendCode(bot))
