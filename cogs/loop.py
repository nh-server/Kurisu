from __future__ import annotations

import asyncio
import discord
import pytz
import logging

from datetime import datetime, timedelta
from discord import AllowedMentions
from discord.ext import commands
from discord.utils import format_dt
from typing import TYPE_CHECKING
from utils.utils import send_dm_message
from utils import Restriction, OptionalMember

if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.context import KurisuContext

logger = logging.getLogger(__name__)


class Loop(commands.Cog):
    """
    Loop events.
    """

    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.emoji = discord.PartialEmoji.from_str('⌚')
        self.restrictions = bot.restrictions
        self.extras = bot.extras
        bot.loop.create_task(self.start_update_loop())

    def __unload(self):
        self.is_active = False

    is_active = True

    last_hour = datetime.now().hour

    tz = pytz.timezone('US/Pacific')

    netinfo_embed = discord.Embed(description="The Network Maintenance Information page has not been successfully checked yet.")

    def netinfo_parse_time(self, time_str: str) -> datetime:
        return self.tz.localize(datetime.strptime(' '.join(time_str.split()), '%A, %B %d, %Y %I :%M %p')).astimezone()

    async def update_netinfo(self):
        async with self.bot.session.get('https://www.nintendo.co.jp/netinfo/en_US/status.json?callback=getJSON', timeout=45) as r:
            if r.status == 200:
                j = await r.json()
            else:
                self.netinfo_embed.description = "Failure when checking the Network Maintenance Information page."
                logger.warning("Status %s while trying to update netinfo.", r.status)
                return

        now = datetime.now(self.tz)

        embed = discord.Embed(title="Network Maintenance Information / Online Status",
                              url="https://www.nintendo.co.jp/netinfo/en_US/index.html",
                              timestamp=now)
        embed.set_footer(text="This information was last updated:")

        for status_type in ("operational_statuses", "temporary_maintenances"):
            descriptor = "Maintenance" if status_type == "temporary_maintenances" else "Status"

            for entry in j[status_type]:
                if "platform" in entry:
                    entry_desc = ', '.join(entry["platform"]).replace("nintendo", "Nintendo").replace("web", "Web")
                else:
                    entry_desc = 'No console specified.'

                begin = datetime(year=2000, month=1, day=1, tzinfo=self.tz)
                end = datetime(year=2099, month=1, day=1, tzinfo=self.tz)
                if "begin" in entry:
                    begin = self.netinfo_parse_time(entry["begin"])
                    entry_desc += '\nBegins: ' + format_dt(begin)
                if "end" in entry:
                    end = self.netinfo_parse_time(entry["end"])
                    entry_desc += '\nEnds: ' + format_dt(end)

                if now < end:
                    entry_name = "{} {}: {}".format(
                        "Current" if begin <= now else "Upcoming",
                        descriptor,
                        entry["software_title"].replace(' <br />\r\n', ', ')
                    )
                    if "services" in entry:
                        entry_name += ", " + ', '.join(entry["services"])
                    embed.add_field(name=entry_name, value=entry_desc, inline=False)
        if len(embed.fields) == 0:
            embed.description = "No ongoing or upcoming maintenances."
        self.netinfo_embed = embed

    @commands.command()
    @commands.cooldown(rate=1, per=60.0, type=commands.BucketType.channel)
    async def netinfo(self, ctx: KurisuContext):
        """Show the nintendo network status."""
        await ctx.send(embed=self.netinfo_embed)

    @commands.command()
    @commands.cooldown(rate=1, per=60.0, type=commands.BucketType.channel)
    async def netinfo_refresh(self, ctx: KurisuContext):
        """Refreshes the nintendo network status information."""
        await self.update_netinfo()
        embed = discord.Embed(title="Netinfo Refresh", color=discord.Color.blue())
        embed.description = "Refresh complete."
        await ctx.send(embed=embed)

    async def start_update_loop(self):
        # thanks Luc#5653
        await self.bot.wait_until_all_ready()
        await self.update_netinfo()  # Run once so it will always be available after restart
        while self.is_active:
            try:
                current_timestamp = datetime.now()

                for restriction in self.bot.restrictions.timed_restricions:
                    restriction_type = Restriction[restriction.type]
                    if current_timestamp > restriction.end_date:
                        member = self.bot.guild.get_member(restriction.user_id) or OptionalMember(
                            id=restriction.user_id)
                        if restriction_type is Restriction.Ban:
                            u = discord.Object(id=restriction.user_id)
                            try:
                                await self.bot.guild.unban(u)
                            except discord.errors.NotFound:
                                pass
                            msg = f"⚠️ **Ban expired**: {member.id}"
                            await self.bot.channels['mod-logs'].send(msg)
                        await self.bot.restrictions.remove_restriction(member, restriction_type)
                    elif not restriction.alerted:
                        warning_time_period = timedelta(minutes=30) if restriction.type is Restriction.Ban else timedelta(minutes=10)
                        warning_time = restriction.end_date - warning_time_period
                        if current_timestamp > warning_time:
                            await self.bot.restrictions.set_timed_restriction_alert(restriction.restriction_id)
                            await self.bot.channels['mods'].send(
                                f"**Note**: <@{restriction.user_id}> | restriction.user_id  {restriction_type.name}"
                                f" restriction will be removed "
                                f"in {((restriction.end_date - current_timestamp).seconds // 60) + 1} minutes.")

                for reminder_entries in self.extras.reminders.values():
                    for reminder in reminder_entries:
                        if current_timestamp <= reminder.date:
                            break
                        await self.extras.delete_reminder(reminder.id, reminder.author_id)
                        member = self.bot.guild.get_member(reminder.author_id)
                        if member:
                            msg = f"You asked to remind you of: {reminder.content}"
                            send = await send_dm_message(member, msg)
                            if not send:
                                await self.bot.channels['bot-cmds'].send(f"{msg}\n{member.mention}", allowed_mentions=AllowedMentions(users=[member]))

                if current_timestamp.minute == 0 and current_timestamp.hour != self.last_hour:
                    await self.bot.channels['helpers'].send(f"{self.bot.guild.name} has {self.bot.guild.member_count:,} members at this hour!")
                    self.last_hour = current_timestamp.hour

                if current_timestamp.minute % 30 == 0 and current_timestamp.second == 0:
                    self.bot.loop.create_task(self.update_netinfo())
            except Exception:
                logger.error("Ignoring exception in start_update_loop", exc_info=True)
            finally:
                await asyncio.sleep(1)


async def setup(bot):
    await bot.add_cog(Loop(bot))
