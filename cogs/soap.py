from __future__ import annotations

import logging
import asyncio
from typing import TYPE_CHECKING, Optional

import discord
from discord.ext import commands

from utils.checks import is_staff, check_staff, InsufficientStaffRank

if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.context import GuildContext

logger = logging.getLogger(__name__)


class Soap(commands.Cog):
    """
    command group related to soaps
    """

    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.soaps_category: Optional[discord.CategoryChannel] = None
        self.bot.loop.create_task(self.setup_soap())

    async def cog_check(self, ctx: GuildContext):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        author = ctx.author
        if not check_staff(self.bot, 'Helper', author.id) and not check_staff(self.bot, 'Staff', author.id) and (
                self.bot.roles['crc'] not in author.roles) and (self.bot.roles['Small Help'] not in author.roles):
            raise InsufficientStaffRank("You can't use this command.")
        return True

    async def setup_soap(self):
        await self.bot.wait_until_all_ready()
        db_channel = await self.bot.configuration.get_channel_by_name('soaps')
        if db_channel:
            channel = self.bot.guild.get_channel(db_channel[0])
            if channel and channel.type == discord.ChannelType.category:
                self.soaps_category = channel

    @is_staff('OP')
    @commands.guild_only()
    @commands.command()
    async def setsoaps(self, ctx: GuildContext, category: discord.CategoryChannel):
        """Sets the soaps category for creating channels. OP+ only."""
        await self.bot.configuration.add_channel('soaps', category)
        self.soaps_category = category
        await ctx.send("Soaps category set.")

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
                           "10. Please wait for further instructions.\n"
                           "## Don't have access to a computer?\n"
                           "There is a way to submit your `essential.exefs` using only your hacked 3DS and a WiFi connection, but it's _not preferred_ compared to the above instructions.\n"
                           "If you need more information about this remote submission method, please let us know in this channel.")
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

    @commands.guild_only()
    @commands.command()
    async def soapnormal(self, ctx: GuildContext):
        """Normal Soap completion message. crc, small help, helper+ only."""
        await ctx.send("The SOAP Transfer has completed!\n\n"
                       "Please boot normally (with the SD inserted into the console), and then go to `System Settings -> Other Settings -> Profile -> Region Settings` and ensure the desired country is selected.\n\n"
                       "Then try opening the eShop.\n\n"
                       "A system transfer was required to do this SOAP. If you are trying to transfer your old console to this one you will need to wait a week.\n\n"
                       "(If you have no interest in a system transfer you may ignore this.)\n\n"
                       "Please let us know if the eShop functions or not."
                       )

    @commands.guild_only()
    @commands.command()
    async def soaplottery(self, ctx: GuildContext):
        """Lottery Soap completion message. crc, small help, helper+ only."""
        await ctx.send("The SOAP Transfer has completed!\n\n"
                       "Please boot normally (with the SD inserted into the console), and then go to `System Settings -> Other Settings -> Profile -> Region Settings` and ensure the desired country is selected.\n\n"
                       "Then try opening the eShop.\n\n"
                       "You hit the SOAP lottery! No system transfer was needed for this SOAP.\n\n"
                       "If you are trying to transfer your old console to this one you can do it right away.\n\n"
                       "(If you have no interest in a system transfer you may ignore this.)\n\n"
                       "Please let us know if the eShop functions or not."
                       )

    @commands.guild_only()
    @commands.command()
    async def soapsubmitter(self, ctx: GuildContext):
        """Sends soap submitter message. crc, small help, helper+ only."""
        await ctx.send("**__Essential.exefs submitter__**\n"
                       "Scan this QR code in FBI by going to `Remote Install -> Scan QR Code`\n"
                       "https://nintendohomebrew.com/assets/img/essentialcia-qr.png\n"
                       "Once it's installed, close FBI and open the newly installed app'\n"
                       "After opening the app, press :3ds_button_y: to type in your Discord name, then press OK.\n"
                       "Tap the :soap: icon on the bottom screen to submit your info.\n"
                       )


async def setup(bot):
    await bot.add_cog(Soap(bot))
