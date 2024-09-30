from __future__ import annotations

import logging
import asyncio
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from utils.utils import KurisuCooldown, simple_embed
from utils.checks import check_if_user_can_sr, is_staff, soap_check

if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.context import KurisuContext

logger = logging.getLogger(__name__)


class Soap(commands.GroupCog):
    """
    command group related to soaps
    """

    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot

    @soap_check()
    @commands.guild_only()
    @commands.command(aliases=["soup", "soap"])
    async def createsoap(self, ctx: GuildContext, helpee: discord.Member):
        """Creates a 🧼 help channel for a user. crc, small help, helper+ only."""
        if not self.soaps_category:
            return await ctx.send("The soaps category is not set.")
        # Channel names can't be longer than 100 characters
        channel_name = f"3ds-{helpee.name}-soap-🧼"[:100]
        for channel in self.soaps_category.text_channels:
            if channel.name == channel_name:
                return await ctx.send("Soap channel already exists for user.")
        channel = await self.soaps_category.create_text_channel(name=channel_name)
        await asyncio.sleep(3)  # Fix for discord race condition(?)
        await channel.set_permissions(helpee, read_messages=True)
        await channel.send(f"{helpee.mention}, please read the following.\n"
                           "0. If your console is on, turn it off. If your console happens to already be in GodMode9, skip to step 3.\n"
                           "1. Insert your SD card into your console.\n"
                           "2. Boot into GodMode9 by holding start while powering on.\n"
                           "3. Navigate to `SysNAND Virtual`\n"
                           "4. Select `essential.exefs`\n"
                           "5. Select `copy to 0:/gm9/out` (and select `Overwrite file(s)` if prompted - if not prompted, ignore and move on)\n"
                           "6. Power off your console and insert your SD card into your computer.\n"
                           "7. Navigate to `/gm9/out` on your SD, `essential.exefs` should be there.\n"
                           "8. Send the `essential.exefs` in *this specific channel*.\n"
                           " - **Please do not send it anywhere else.**\n"
                           " - **File contains very sensitive console unique certificates.**\n"
                           " - **These allow impersonation of console in servers, do not publicly share it.**\n"
                           "9. Find your serial number label and provide the number or a picture of it.\n"
                           " - On a New 2DS, this is located under the game card/SD card slot cover.\n"
                           " - If you can't locate your serial number or the label is missing/rubbed off:\n"
                           "  - The label may be on the backplate, under the Nintendo logo.\n"
                           "  - If it is not, try unscrewing the backplate and checking there.\n"
                           "  - The screws in the backplate are 'captive screws'. They will not unscrew all the way.\n"
                           "    Unscrew them until they click, then gently lift the backplate using the notches at the sides.\n"
                           "  - The label also may be under the battery.\n"
                           "  - If you still can't find it, please request further assistance.\n"
                           "10. Please wait for further instructions.")
        await self.bot.channels['mod-logs'].send(f"⭕️ **🧼 access granted**: {ctx.author.mention} granted access to 🧼 channel to {helpee.mention}")
        msg = f"🆕 **🧼 channel created**: {ctx.author.mention} created 🧼 channel {channel.mention} | {channel.name} ({channel.id})"
        await self.bot.channels['mod-logs'].send(msg)
        await ctx.send(f"Created 🧼 {channel.mention}.")

    @is_staff('Helper')
    @commands.guild_only()
    @commands.command(aliases=["rinse"])
    async def deletesoap(self, ctx: GuildContext, channels: commands.Greedy[discord.TextChannel]):
        """Deletes a :soap: help channel. helper+ only."""
        if not self.soaps_category:
            return await ctx.send("The soaps category is not set.")
        for channel in channels:
            if channel not in self.soaps_category.channels:
                continue
            msg = f":x: **:soap: channel deleted**: {ctx.author.mention} deleted :soap: channel {channel.name} ({channel.id})"
            await self.bot.channels['mod-logs'].send(msg)
            await ctx.send(f"Deleted :soap: {channel.name}.")
            await channel.delete()

    @soap_check()
    @commands.guild_only()
    async def soapnormal(self, ctx: GuildContext):
        """Normal Soap completion message. crc, small help, helper+ only."""
        await ctx.send(
            f"The SOAP Transfer has completed!\n\n"
             "Please boot normally (with the SD inserted into the console), and then go to `System Settings -> Other Settings -> Profile -> Region Settings` and ensure the desired country is selected\n\n"
             "Then try opening the eShop\n\n"
             "A system transfer was required to do this SOAP, if you are trying to transfer your old console to this one you will need to wait a week (if you have no interest in a system transfer you may ignore this)\n\n"
             "Please let us know if the eshop functions or not"
        )

    @soap_check()
    @commands.guild_only()
    async def soaplottery(self, ctx: GuildContext):
       """Lottery Soap completion message. crc, small help, helper+ only."""
        await ctx.send(
            f"The SOAP Transfer has completed!\n\n"
             "Please boot normally (with the SD inserted into the console), and then go to `System Settings -> Other Settings -> Profile -> Region Settings` and ensure the desired country is selected\n\n"
             "Then try opening the eShop\n\n"
             "You hit the SOAP lottery, no system transfer was needed for this SOAP, if you are trying to transfer your old console to this one you can do it right away (if you have no interest in a system transfer you may ignore this)\n\n"
             "Please let us know if the eshop functions or not"
        )


async def setup(bot):
    await bot.add_cog(AssistanceHardware(bot))
