import asyncio
import copy
import discord
import feedparser
import sys
import time
import datetime
import traceback
import os
import json
from discord.ext import commands
from urllib.parse import urlparse, parse_qs

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

    is_active = True

    last_hour = datetime.datetime.now().hour

    warning_time_period = datetime.timedelta(minutes=30)

    async def start_update_loop(self):
        # thanks Luc#5653
        await self.bot.wait_until_all_ready()
        while self.is_active:
            try:
                timestamp = datetime.datetime.now()
                timebans = copy.copy(self.bot.timebans)
                for ban in timebans.items():
                    if timestamp > ban[1][1]:
                        self.bot.actions.append("tbr:" + ban[0])
                        await self.bot.unban(self.bot.server, ban[1][0])
                        msg = "⚠️ **Ban expired**: {} | {}#{}".format(ban[1][0].mention, self.bot.escape_name(ban[1][0].name), ban[1][0].discriminator)
                        await self.bot.send_message(self.bot.modlogs_channel, msg)
                        self.bot.timebans.pop(ban[0])
                    elif not ban[1][2]:
                        warning_time = ban[1][1] - self.warning_time_period
                        if timestamp > warning_time:
                            ban[1][2] = True
                            await self.bot.send_message(self.bot.mods_channel, "**Note**: {} will be unbanned in {} minutes.".format(self.bot.escape_name(ban[1][0]), ((ban[1][1] - timestamp).seconds // 60) + 1))

                if timestamp.minute == 0 and timestamp.hour != self.last_hour:
                    await self.bot.send_message(self.bot.helpers_channel, "{} has {:,} members at this hour!".format(self.bot.server.name, self.bot.server.member_count))
                    self.last_hour = timestamp.hour

                if (timestamp.minute - 1) % 5 == 0 and timestamp.second == 0:
                    # ugly but it works
                    ninupdates_feed = feedparser.parse('https://yls8.mtheall.com/ninupdates/feed.php')
                    for entry in ninupdates_feed['entries']:
                        system, ver = entry['title'].split()
                        reporturl = entry['link']
                        reporturl_date = parse_qs(urlparse(reporturl).query)['date'][0]
                        reportpath = 'data/ninupdates/{}.json'.format(system)
                        to_write = {'reportdate': reporturl_date}
                        if not os.path.isfile(reportpath):
                            to_write['ver'] = ver
                            with open(reportpath, 'w') as f:
                                json.dump(to_write, f)
                        else:
                            with open(reportpath, 'r') as f:
                                oldver = json.load(f)
                            if oldver['reportdate'] != reporturl_date:
                                # "Reminder to not update until confirmed safe or known broken features are fixed."
                                if reporturl_date == ver:
                                    await self.bot.send_message(self.bot.announcements_channel, '⏬ System updated detected for {}\n<{}>'.format(system, reporturl))
                                    to_write['ver'] = reporturl_date
                                else:
                                    await self.bot.send_message(self.bot.announcements_channel, '⏬ System updated detected for {}: {}\n<{}>'.format(system, ver, reporturl))
                                    to_write['ver'] = ver
                                with open(reportpath, 'w') as f:
                                    json.dump(to_write, f)
                            elif oldver['reportdate'] == oldver['ver'] and len(ver) != 17:
                                # lazy method of seeing if an update + vernumber was found before the bot caught the update in the first place
                                await self.bot.send_message(self.bot.announcements_channel, 'ℹ️ New update version for {}: {} ({})'.format(system, ver, reporturl_date))
                                to_write['ver'] = ver
                                with open(reportpath, 'w') as f:
                                    json.dump(to_write, f)

            except Exception as e:
                print('Ignoring exception in start_update_loop', file=sys.stderr)
                traceback.print_tb(e.__traceback__)
                print('{0.__class__.__name__}: {0}'.format(e), file=sys.stderr)
            finally:
                await asyncio.sleep(1)

def setup(bot):
    bot.add_cog(Loop(bot))
