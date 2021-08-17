import discord
import hashlib
import re
import struct

from discord.ext import commands
from utils import crud, utils


class FriendCode(commands.Cog):
    """
    Stores and obtains friend codes for sharing.
    """

    def __init__(self, bot):
        self.bot = bot

    # based on https://github.com/megumisonoda/SaberBot/blob/master/lib/saberbot/valid_fc.rb
    def verify_3ds_fc(self, fc: str):
        try:
            fc = int(fc.replace('-', ''))
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
        fc = str(fc).rjust(12, '0')
        return f"{fc[0:4]} - {fc[4:8]} - {fc[8:12]}"

    def switch_fc_to_string(self, fc: int):
        fc = str(fc)
        return f"SW - {fc[0:4]} - {fc[4:8]} - {fc[8:12]}"

    @commands.command()
    async def fcregister(self, ctx, fc: str):
        """Add your friend code."""
        console = "switch" if fc.startswith("SW") else "3ds"
        if console == "3ds":
            fc = self.verify_3ds_fc(fc)
        else:
            fc = self.verify_switch_fc(fc)
        if not fc:
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
    async def fcquery(self, ctx, member: discord.Member):
        """Get other user's friend codes. You must have one yourself in the database."""

        if not (friendcode := await crud.get_friendcode(ctx.author.id)):
            return await ctx.send("You need to register your own friend code with `.fcregister <friendcode>` before getting others.")
        if not (friendcode_m := await crud.get_friendcode(member.id)):
            return await ctx.send("This user does not have a registered friend code.")

        fcs = ""
        fcs_m = ""
        fc_3ds = "3ds: {0} \n"
        fc_switch = "switch: {0}"

        if friendcode.fc_3ds:
            fcs += fc_3ds.format(self.n3ds_fc_to_string(friendcode.fc_3ds))
        if friendcode.fc_switch:
            fcs += fc_switch.format(self.switch_fc_to_string(friendcode.fc_switch))

        if friendcode_m.fc_3ds:
            fcs_m += fc_3ds.format(self.n3ds_fc_to_string(friendcode.fc_3ds))
        if friendcode_m.fc_switch:
            fcs_m += fc_switch.format(self.switch_fc_to_string(friendcode.fc_switch))

        await ctx.send(f"{member.mention} friend codes are\n{fcs}")
        await utils.send_dm_message(member, f"{ctx.author} has asked for your friend codes! Their codes are\n{fcs_m}")

    @commands.command()
    async def fcdelete(self, ctx, console: str):
        """Delete your friend code."""
        if console == '3ds':
            await crud.delete_friendcode_3ds(ctx.author.id)
        elif console == 'switch':
            await crud.delete_friendcode_switch(ctx.author.id)
        else:
            return await ctx.send("Invalid console.")
        await ctx.send(f"Your {console} friend code was removed from the database.")

    @commands.command()
    async def fctest_3ds(self, ctx, fc):
        fc = self.verify_3ds_fc(fc)
        if fc:
            await ctx.send(self.n3ds_fc_to_string(fc))
        else:
            await ctx.send("Invalid.")

    @commands.command()
    async def fctest_switch(self, ctx, fc):
        fc = self.verify_switch_fc(fc)
        if fc:
            await ctx.send(self.switch_fc_to_string(fc))
        else:
            await ctx.send("Invalid.")


def setup(bot):
    bot.add_cog(FriendCode(bot))
