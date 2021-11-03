import asyncio
import disnake
import pytz
import logging

from datetime import datetime, timedelta
from disnake import AllowedMentions
from disnake.ext import commands
from utils import crud
from utils.utils import send_dm_message


logger = logging.getLogger(__name__)


class Loop(commands.Cog):
    """
    Loop events.
    """

    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.start_update_loop())

    def __unload(self):
        self.is_active = False

    is_active = True

    last_hour = datetime.now().hour

    warning_time_period_ban = timedelta(minutes=30)
    warning_time_period_mute = timedelta(minutes=10)
    warning_time_period_nohelp = timedelta(minutes=10)
    warning_time_period_notech = timedelta(minutes=10)
    warning_time_period_helpmute = timedelta(minutes=10)

    tz = pytz.timezone('US/Pacific')

    netinfo_embed = discord.Embed(description="The Network Maintenance Information page has not been successfully checked yet.")
    # netinfo_future_embed = discord.Embed(description="This needs to be set up")

    def netinfo_parse_time(self, timestr):
        return datetime.strptime(' '.join(timestr.split()), '%A, %B %d, %Y %I :%M %p').replace(tzinfo=self.tz)

    async def update_netinfo(self):
        async with self.bot.session.get('https://www.nintendo.co.jp/netinfo/en_US/status.json?callback=getJSON', timeout=45) as r:
            if r.status == 200:
                j = await r.json()
            else:
                # logging setup :)
                logger.warning("Status %s while trying to update netinfo.", r.status)
                return

        now = datetime.now(self.tz)

        embed = discord.Embed(title="Network Maintenance Information / Online Status",
                              url="https://www.nintendo.co.jp/netinfo/en_US/index.html",
                              description="All times are US/Pacific.")
        embed.set_footer(text=f"This information was last updated {now.strftime('%A, %B %d, %Y %I:%M %p')}.")

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
                    entry_desc += '\nBegins: ' + begin.strftime('%A, %B %d, %Y %I:%M %p')
                if "end" in entry:
                    end = self.netinfo_parse_time(entry["end"])
                    entry_desc += '\nEnds: ' + end.strftime('%A, %B %d, %Y %I:%M %p')

                if now < end:
                    entry_name = "{} {}: {}".format(
                        "Current" if begin <= now else "Upcoming",
                        descriptor,
                        entry["software_title"].replace(' <br />\r\n', ', ')
                    )
                    if "services" in entry:
                        entry_name += ", " + ', '.join(entry["services"])
                    embed.add_field(name=entry_name, value=entry_desc, inline=False)

        self.netinfo_embed = embed

    @commands.command()
    @commands.cooldown(rate=1, per=60.0, type=commands.BucketType.channel)
    async def netinfo(self, ctx):
        await ctx.send(embed=self.netinfo_embed)

    @commands.command()
    @commands.cooldown(rate=1, per=60.0, type=commands.BucketType.channel)
    async def netinfo_refresh(self, ctx):
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

                timebans = await crud.get_time_restrictions_by_type('timeban')
                timemutes = await crud.get_time_restrictions_by_type('timemute')
                timenohelps = await crud.get_time_restrictions_by_type('timenohelp')
                timenotechs = await crud.get_time_restrictions_by_type('timenotech')
                timehelpmutes = await crud.get_time_restrictions_by_type('timehelpmute')
                timedroles = await crud.get_timed_roles()
                reminder_entries = await crud.get_reminders()

                for timeban in timebans:
                    unban_time = timeban.end_date
                    if current_timestamp > unban_time:
                        user = await self.bot.fetch_user(timeban.user)
                        self.bot.actions.append("tbr:" + str(timeban.user))
                        try:
                            await self.bot.guild.unban(user)
                        except discord.errors.NotFound:
                            pass
                        msg = f"⚠️ **Ban expired**: {user.mention} | {user}"
                        await self.bot.channels['mod-logs'].send(msg)
                        await crud.remove_timed_restriction(user.id, 'timeban')
                    elif not timeban.alerted:
                        warning_time = unban_time - self.warning_time_period_ban
                        if current_timestamp > warning_time:
                            await crud.set_time_restriction_alert(timeban.user, 'timeban')
                            user = await self.bot.fetch_user(timeban.user)
                            await self.bot.channels['mods'].send(f"**Note**: {user.id} will be unbanned in {((unban_time - current_timestamp).seconds // 60) + 1} minutes.")

                for timemute in timemutes:
                    unmute_time = timemute.end_date
                    if current_timestamp > unmute_time:
                        await crud.remove_timed_restriction(timemute.user, "timemute")
                        await crud.remove_permanent_role(timemute.user, self.bot.roles['Muted'].id)
                        msg = f"🔈 **Mute expired**: <@{timemute.user}>"
                        await self.bot.channels['mod-logs'].send(msg)
                        member = self.bot.guild.get_member(timemute.user)
                        if member:
                            await member.remove_roles(self.bot.roles['Muted'])
                    elif not timemute.alerted:
                        warning_time = unmute_time - self.warning_time_period_mute
                        if current_timestamp > warning_time:
                            await crud.set_time_restriction_alert(timemute.user, 'timemute')
                            user = await self.bot.fetch_user(timemute.user)
                            await self.bot.channels['mods'].send(f"**Note**: <@{user.id}> will be unmuted in {((unmute_time - current_timestamp).seconds // 60) + 1} minutes.")

                for timenohelp in timenohelps:
                    if current_timestamp > timenohelp.end_date:
                        await crud.remove_timed_restriction(timenohelp.user, "timenohelp")
                        await crud.remove_permanent_role(timenohelp.user, self.bot.roles['No-Help'].id)
                        msg = f"⭕️ **No-Help Restriction expired**: <@{timenohelp.user}>"
                        await self.bot.channels['mod-logs'].send(msg)
                        await self.bot.channels['helpers'].send(msg)
                        member = self.bot.guild.get_member(timenohelp.user)
                        if member:
                            await member.remove_roles(self.bot.roles['No-Help'])
                    elif not timenohelp.alerted:
                        warning_time = timenohelp.end_date - self.warning_time_period_nohelp
                        if current_timestamp > warning_time:
                            await crud.set_time_restriction_alert(timenohelp.user, 'timenohelp')
                            await self.bot.channels['helpers'].send(f"**Note**: <@{timenohelp.user}> no-help restriction will expire in {((timenohelp.end_date - current_timestamp).seconds // 60) + 1} minutes.")

                for timehelpmute in timehelpmutes:
                    if current_timestamp > timehelpmute.end_date:
                        await crud.remove_timed_restriction(timehelpmute.user, "timehelpmute")
                        await crud.remove_permanent_role(timehelpmute.user, self.bot.roles['help-mute'].id)
                        msg = f"⭕️ **Help Mute expired**: <@{timehelpmute.user}>"
                        await self.bot.channels['mod-logs'].send(msg)
                        await self.bot.channels['helpers'].send(msg)
                        member = self.bot.guild.get_member(timehelpmute.user)
                        if member:
                            await member.remove_roles(self.bot.roles['help-mute'])
                    elif not timehelpmute.alerted:
                        warning_time = timehelpmute.end_date - self.warning_time_period_helpmute
                        if current_timestamp > warning_time:
                            await crud.set_time_restriction_alert(timehelpmute.user, 'timehelpmute')
                            await self.bot.channels['helpers'].send(f"**Note**: <@{timehelpmute.user}> help mute will expire in {((timehelpmute.end_date - current_timestamp).seconds // 60) + 1} minutes.")

                for timenotech in timenotechs:
                    if current_timestamp > timenotech.end_date:
                        await crud.remove_timed_restriction(timenotech.user, "timenotech")
                        await crud.remove_permanent_role(timenotech.user, self.bot.roles['No-Tech'].id)
                        msg = f"⭕️ **No-Tech Restriction expired**: <@{timenotech.user}>"
                        await self.bot.channels['mod-logs'].send(msg)
                        await self.bot.channels['helpers'].send(msg)
                        member = self.bot.guild.get_member(timenotech.user)
                        if member:
                            await member.remove_roles(self.bot.roles['No-Tech'])
                    elif not timenotech.alerted:
                        warning_time = timenotech.end_date - self.warning_time_period_notech
                        if current_timestamp > warning_time:
                            await crud.set_time_restriction_alert(timenotech.user, 'timenotech')
                            await self.bot.channels['helpers'].send(f"**Note**: <@{timenotech.user}> no-tech restriction will expire in {((timenotech.end_date - current_timestamp).seconds // 60) + 1} minutes.")

                for timedrole in timedroles:
                    if current_timestamp > timedrole.expiring_date:
                        await crud.remove_timed_role(timedrole.user_id, timedrole.role_id)
                        member = self.bot.guild.get_member(timedrole.user_id)
                        role = self.bot.guild.get_role(timedrole.role_id)
                        if member and role:
                            await member.remove_roles(role)
                        msg = f"⭕ **Timed Role Expired**: <@{timedrole.user_id}>"
                        await self.bot.channels['mod-logs'].send(msg)

                for reminder_entry in reminder_entries:
                    if current_timestamp <= reminder_entry.date:
                        break
                    await crud.remove_reminder(reminder_entry.id)
                    member = self.bot.guild.get_member(reminder_entry.author)
                    if member:
                        msg = f"You asked to remind you of: {reminder_entry.reminder}"
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


def setup(bot):
    bot.add_cog(Loop(bot))
