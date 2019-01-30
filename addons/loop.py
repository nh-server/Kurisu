import asyncio
import copy
import discord
import sys
import traceback
import json
import requests
import pytz
from datetime import datetime, timedelta
from discord.ext import commands

class Loop:
    """
    Loop events.
    """
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.start_update_loop())
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    def __unload(self):
        self.is_active = False

    async def remove_restriction_id(self, member_id, rst):
        with open("data/restrictions.json", "r") as f:
            rsts = json.load(f)
        if member_id not in rsts:
            rsts[member_id] = []
        if rst in rsts[member_id]:
            rsts[member_id].remove(rst)
        with open("data/restrictions.json", "w") as f:
            json.dump(rsts, f)

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
        embed.set_footer(text="This information was last updated {}.".format(now.strftime('%A, %B %d, %Y %I:%M %p')))
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
                embed.add_field(name='Current Status: {}, {}'.format(m["software_title"].replace(' <br /> ', ', '), ', '.join(m["services"])),
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
    async def netinfo(self):
        await self.bot.say(embed=self.netinfo_embed)

    async def start_update_loop(self):
        # thanks Luc#5653
        await self.bot.wait_until_all_ready()
        while self.is_active:
            try:
                timestamp = datetime.now()
                timebans = copy.copy(self.bot.timebans)
                timemutes = copy.copy(self.bot.timemutes)
                timenohelp = copy.copy(self.bot.timenohelp)
                for ban in timebans.items():
                    if timestamp > ban[1][1]:
                        self.bot.actions.append("tbr:" + ban[0])
                        await self.bot.unban(self.bot.server, ban[1][0])
                        msg = "⚠️ **Ban expired**: {} | {}#{}".format(ban[1][0].mention, self.bot.escape_name(ban[1][0].name), ban[1][0].discriminator)
                        await self.bot.send_message(self.bot.modlogs_channel, msg)
                        self.bot.timebans.pop(ban[0])
                    elif not ban[1][2]:
                        warning_time = ban[1][1] - self.warning_time_period_ban
                        if timestamp > warning_time:
                            ban[1][2] = True
                            await self.bot.send_message(self.bot.mods_channel, "**Note**: {} will be unbanned in {} minutes.".format(self.bot.escape_name(ban[1][0]), ((ban[1][1] - timestamp).seconds // 60) + 1))

                for mute in timemutes.items():
                    if timestamp > mute[1][0]:
                        await self.remove_restriction_id(mute[0], "Muted")
                        msg = "🔈 **Mute expired**: <@{}>".format(mute[0])
                        await self.bot.send_message(self.bot.modlogs_channel, msg)
                        self.bot.timemutes.pop(mute[0])
                        member = discord.utils.get(self.bot.server.members, id=mute[0])
                        if member:
                            await self.bot.remove_roles(member, self.bot.muted_role)
                        with open("data/timemutes.json", "r") as f:
                            timemutes_j = json.load(f)
                        try:
                            timemutes_j.pop(mute[0])
                            with open("data/timemutes.json", "w") as f:
                                json.dump(timemutes_j, f)
                        except KeyError:
                            pass
                    elif not mute[1][1]:
                        warning_time = mute[1][0] - self.warning_time_period_mute
                        if timestamp > warning_time:
                            mute[1][1] = True
                            await self.bot.send_message(self.bot.mods_channel, "**Note**: <@{}> will be unmuted in {} minutes.".format(mute[0], ((mute[1][0] - timestamp).seconds // 60) + 1))

                for nohelp in timenohelp.items():
                    if timestamp > nohelp[1][0]:
                        await self.remove_restriction_id(nohelp[0], "No-Help")
                        msg = "⭕️ **No-Help Restriction expired**: <@{}>".format(nohelp[0])
                        await self.bot.send_message(self.bot.modlogs_channel, msg)
                        await self.bot.send_message(self.bot.helpers_channel, msg)
                        self.bot.timenohelp.pop(nohelp[0])
                        member = discord.utils.get(self.bot.server.members, id=nohelp[0])
                        if member:
                            await self.bot.remove_roles(member, self.bot.nohelp_role)
                        with open("data/timenohelp.json", "r") as f:
                            timenohelp_j = json.load(f)
                        try:
                            timenohelp_j.pop(nohelp[0])
                            with open("data/timenohelp.json", "w") as f:
                                json.dump(timenohelp_j, f)
                        except KeyError:
                            pass
                    elif not nohelp[1][1]:
                        warning_time = nohelp[1][0] - self.warning_time_period_nohelp
                        if timestamp > warning_time:
                            nohelp[1][1] = True
                            await self.bot.send_message(self.bot.helpers_channel, "**Note**: <@{}> no-help restriction will expire in {} minutes.".format(nohelp[0], ((nohelp[1][0] - timestamp).seconds // 60) + 1))

                if timestamp.minute == 0 and timestamp.hour != self.last_hour:
                    await self.bot.send_message(self.bot.helpers_channel, "{} has {:,} members at this hour!".format(self.bot.server.name, self.bot.server.member_count))
                    self.last_hour = timestamp.hour

                if timestamp.minute % 30 == 0 and timestamp.second == 0:
                    self.bot.loop.create_task(self.update_netinfo())

            except Exception as e:
                print('Ignoring exception in start_update_loop', file=sys.stderr)
                traceback.print_tb(e.__traceback__)
                print('{0.__class__.__name__}: {0}'.format(e), file=sys.stderr)
            finally:
                await asyncio.sleep(1)

def setup(bot):
    bot.add_cog(Loop(bot))
