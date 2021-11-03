from typing import Literal

import disnake
import hashlib
import re
import struct

from disnake.ext import commands
from disnake.ext.commands import Param

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

    @commands.slash_command()
    async def friendcode(self, inter):
        pass

    @friendcode.sub_command()
    async def register(self, inter, fc: str = Param(desc="Your friendcode")):
        """Add your friend code."""
        console = "switch" if fc.startswith("SW") else "3ds"
        fc = self.verify_3ds_fc(fc) if console == "3ds" else self.verify_switch_fc(fc)
        if not fc:
            await inter.response.send_message("This friend code is invalid. Switch friend codes must be in a SW-XXXX-XXXX-XXXX format and 3ds friends codes in a XXXX-XXXX-XXXX format.")
            return
        fcs = await crud.get_friendcode(inter.author.id)
        if fcs and (fcs.fc_3ds and console == "3ds" or fcs.fc_switch and console == "switch"):
            await inter.response.send_message(f"Please delete your current {console} friend code with `.fcdelete {console}` before adding another.")
            return
        if console == "3ds":
            await crud.add_friendcode_3ds(inter.author.id, fc)
        else:
            await crud.add_friendcode_switch(inter.author.id, fc)
        await inter.response.send_message(f"{inter.author.mention} {console} friend code inserted: {self.n3ds_fc_to_string(fc) if console=='3ds' else self.switch_fc_to_string(fc)}")

    @commands.guild_only()
    @friendcode.sub_command()
    async def query(self, inter, member: disnake.Member = Param(desc="Member to query friendcodes")):
        """Get other user's friend codes. You must have one yourself in the database."""

        if not (friendcode := await crud.get_friendcode(inter.author.id)):
            return await inter.response.send_message("You need to register your own friend code with `/friendcode register <friendcode>` before getting others." , ephemeral=True)
        if not (friendcode_m := await crud.get_friendcode(member.id)):
            return await inter.response.send_message("This user does not have a registered friend code." , ephemeral=True)

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

        await inter.response.send_message(f"{member.mention} friend codes are\n{fcs}", ephemeral=True)
        await utils.send_dm_message(member, f"{inter.author} has asked for your friend codes! Their codes are\n{fcs_m}")

    @friendcode.sub_command()
    async def delete(self, inter, console: Literal['3ds', 'switch'] = Param(desc="Console which friendcode you want to delete")):
        """Delete your friend code."""
        if console == '3ds':
            await crud.delete_friendcode_3ds(inter.author.id)
        elif console == 'switch':
            await crud.delete_friendcode_switch(inter.author.id)
        await inter.response.send_message(f"Your {console} friend code was removed from the database.", ephemeral=True)

    @friendcode.sub_command()
    async def test_3ds(self, inter, fc = Param(desc="Friendcode to test")):
        fc = self.verify_3ds_fc(fc)
        if fc:
            await inter.response.send_message(self.n3ds_fc_to_string(fc), ephemeral=True)
        else:
            await inter.response.send_message("Invalid.", ephemeral=True)

    @friendcode.sub_command()
    async def test_switch(self, inter, fc: str = Param(desc="Friendcode to test")):
        fc = self.verify_switch_fc(fc)
        if fc:
            await inter.response.send_message(self.switch_fc_to_string(fc), ephemeral=True)
        else:
            await inter.response.send_message("Invalid.", ephemeral=True)


def setup(bot):
    bot.add_cog(FriendCode(bot))
