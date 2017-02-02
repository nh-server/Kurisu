import asyncio
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

    cooldown = 30
    is_active = True

    last_hour = datetime.datetime.now().hour

    async def start_update_loop(self):
        # thanks Luc | ルカリオ#5653
        await self.bot.wait_until_ready()
        while self.is_active:
            try:
                # print("loop")
                timestamp = datetime.datetime.now()
                if timestamp.minute == 0 and timestamp.hour != self.last_hour:
                    await self.bot.send_message(self.bot.helpers_channel, "{} has {:,} members at this hour!".format(self.bot.server.name, self.bot.server.member_count))
                    self.last_hour = timestamp.hour
                #for user_id, times in self.bot.timedbans.items():
                #    pass
            except Exception as e:
                print('Ignoring exception in start_update_loop', file=sys.stderr)
                traceback.print_tb(e.__traceback__)
                print('{0.__class__.__name__}: {0}'.format(e), file=sys.stderr)
            finally:
                await asyncio.sleep(self.cooldown)

def setup(bot):
    bot.add_cog(Loop(bot))
