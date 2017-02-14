import asyncio
import copy
import discord
import sys
import time
import datetime
import traceback
from discord.ext import commands
from sys import argv

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
                        self.bot.actions.append("tbr:"+ban[0])
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
            except Exception as e:
                print('Ignoring exception in start_update_loop', file=sys.stderr)
                traceback.print_tb(e.__traceback__)
                print('{0.__class__.__name__}: {0}'.format(e), file=sys.stderr)
            finally:
                await asyncio.sleep(1)

def setup(bot):
    bot.add_cog(Loop(bot))
