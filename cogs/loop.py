import asyncio
import discord
import sys
import traceback
import json
import requests
import pytz
from datetime import datetime, timedelta
from discord.ext import commands
from cogs.database import DatabaseCog


class Loop(DatabaseCog):
    """
    Loop events.
    """
    def __init__(self, bot):
        DatabaseCog.__init__(self, bot)
        bot.loop.create_task(self.start_update_loop())

    def __unload(self):
        self.is_active = False

    is_active = True

    last_hour = datetime.now().hour

    warning_time_period_ban = timedelta(minutes=30)
    warning_time_period_mute = timedelta(minutes=10)
    warning_time_period_nohelp = timedelta(minutes=10)

    tz = pytz.timezone('US/Pacific')

    netinfo_embed = discord.Embed(description="The Network Maintenance Information page has not been successfully checked yet.")
    # netinfo_future_embed = discord.Embed(description="This needs to be set up")

    def netinfo_parse_time(self, timestr):
        return datetime.strptime(' '.join(timestr.split()), '%A, %B %d, %Y %I :%M %p').replace(tzinfo=self.tz)

    async def update_netinfo(self):
        r = requests.get('https://www.nintendo.co.jp/netinfo/en_US/status.json?callback=getJSON')
        j = json.loads(r.text[8:-2])
        now = datetime.now(self.tz)
        embed = discord.Embed(title="Network Maintenance Information / Online Status",
                              url="https://www.nintendo.co.jp/netinfo/en_US/index.html",
                              description="All times are US/Pacific.")
        embed.set_footer(text=f"This information was last updated {now.strftime('%A, %B %d, %Y %I:%M %p')}.")
        for m in j["operational_statuses"]:
            begin = self.netinfo_parse_time(m["begin"])
            if "end" in m:
                end = self.netinfo_parse_time(m["end"])
            else:
                end = datetime(year=2099, month=1, day=1, tzinfo=self.tz)
            if begin <= now < end:
                m_desc = ', '.join(m["platform"])
                m_desc += '\nBegins: ' + begin.strftime('%A, %B %d, %Y %I:%M %p')
                if end.year != 2099:
                    m_desc += '\nEnds: ' + end.strftime('%A, %B %d, %Y %I:%M %p')
                embed.add_field(name=f'Current Status: {m["software_title"].replace(" <br /> ", ", ")}, {", ".join(m["services"])}',
                                value=m_desc, inline=False)
        for m in j["temporary_maintenances"]:
            begin = self.netinfo_parse_time(m["begin"])
            if "end" in m:
                end = self.netinfo_parse_time(m["end"])
            else:
                end = datetime(year=2099, month=1, day=1, tzinfo=self.tz)
            if begin <= now < end:
                m_desc = ', '.join(m["platform"])
                m_desc += '\nBegins: ' + begin.strftime('%A, %B %d, %Y %I:%M %p')
                if end.year != 2099:
                    m_desc += '\nEnds: ' + end.strftime('%A, %B %d, %Y %I:%M %p')
                embed.add_field(name='Current Maintenance: {}, {}'.format(m["software_title"].replace(' <br />\r\n', ', '), ', '.join(m["services"])),
                                value=m_desc, inline=False)
        self.netinfo_embed = embed

    @commands.command()
    @commands.cooldown(rate=1, per=60.0, type=commands.BucketType.channel)
    async def netinfo(self, ctx):
        await ctx.send(embed=self.netinfo_embed)

    async def start_update_loop(self):
        # thanks Luc#5653
        await self.bot.wait_until_all_ready()
        while self.is_active:
            try:
                timestamp = datetime.now()
                for ban in await self.get_time_restrictions_by_type('timeban'):
                    unban_time = datetime.strptime(ban[1], "%Y-%m-%d %H:%M:%S")
                    if timestamp > unban_time:
                        user = await self.bot.fetch_user(ban[0])
                        self.bot.actions.append("tbr:" + str(ban[0]))
                        await self.bot.guild.unban(user)
                        msg = f"⚠️ **Ban expired**: {user.mention} | {user}"
                        await self.bot.channels['mod-logs'].send(msg)
                        await self.remove_timed_restriction(user.id, 'timeban')
                    elif not ban[3]:
                        warning_time = unban_time - self.warning_time_period_ban
                        if timestamp > warning_time:
                            await self.set_time_restriction_alert(ban[0], 'timeban')
                            user = await self.bot.fetch_user(ban[0])
                            await self.bot.channels['mods'].send(f"**Note**: {user.id} will be unbanned in {((unban_time - timestamp).seconds // 60) + 1} minutes.")
                for mute in await self.get_time_restrictions_by_type('timemute'):
                    unmute_time = datetime.strptime(mute[1], "%Y-%m-%d %H:%M:%S")
                    if timestamp > unmute_time:
                        await self.remove_timed_restriction(mute[0], "timemute")
                        await self.remove_restriction(mute[0], self.bot.roles['Muted'])
                        msg = f"🔈 **Mute expired**: <@{mute[0]}>"
                        await self.bot.channels['mod-logs'].send(msg)
                        member = self.bot.guild.get_member(mute[0])
                        if member:
                            await member.remove_roles(self.bot.roles['Muted'])
                    elif not mute[3]:
                        warning_time = unmute_time - self.warning_time_period_mute
                        if timestamp > warning_time:
                            await self.set_time_restriction_alert(mute[0], 'timemute')
                            user = await self.bot.fetch_user(mute[0])
                            await self.bot.channels['mods'].send(f"**Note**: <@{user.id}> will be unmuted in {((unmute_time - timestamp).seconds // 60) + 1} minutes.")

                for nohelp in await self.get_time_restrictions_by_type('timenohelp'):
                    help_time = datetime.strptime(nohelp[1], "%Y-%m-%d %H:%M:%S")
                    if timestamp > help_time:
                        await self.remove_timed_restriction(nohelp[0], "timenohelp")
                        await self.remove_restriction(nohelp[0], self.bot.roles['No-Help'])
                        msg = f"⭕️ **No-Help Restriction expired**: <@{nohelp[0]}>"
                        await self.bot.channels['mod-logs'].send(msg)
                        await self.bot.channels['helpers'].send(msg)
                        member = self.bot.guild.get_member(nohelp[0])
                        if member:
                            await member.remove_roles(self.bot.roles['No-Help'])
                    elif not nohelp[1][1]:
                        warning_time = help_time - self.warning_time_period_nohelp
                        if timestamp > warning_time:
                            await self.set_time_restriction_alert(nohelp[0], 'timenohelp')
                            await self.bot.channels['helpers'].send(f"**Note**: <@{nohelp[0]}> no-help restriction will expire in {((help_time - timestamp).seconds // 60) + 1} minutes.")

                if timestamp.minute == 0 and timestamp.hour != self.last_hour:
                    await self.bot.channels['helpers'].send(f"{self.bot.guild.name} has {self.bot.guild.member_count:,} members at this hour!")
                    self.last_hour = timestamp.hour

                # if timestamp.minute % 30 == 0 and timestamp.second == 0:
                #    self.bot.loop.create_task(self.update_netinfo())

            except Exception as e:
                print('Ignoring exception in start_update_loop', file=sys.stderr)
                traceback.print_tb(e.__traceback__)
                print(f'{e.__class__.__name__}: {e}', file=sys.stderr)
            finally:
                await asyncio.sleep(1)


def setup(bot):
    bot.add_cog(Loop(bot))
