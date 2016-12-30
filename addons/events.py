import discord
import re
from discord.ext import commands
from sys import argv

class Logs:
    """
    Logs join and leave messages, bans and unbans, and member changes.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    async def on_message(self, message):
        if message.author == self.bot.server.me:  # don't process messages by the bot
            return
        contains_invite_link = "discordapp.com/invite" in message.content or "discord.gg" in message.content
        if contains_invite_link:
            await self.bot.send_message(self.bot.mods_channel, "✉️ **Invite posted**: {} posted an invite link in {}".format(message.author.mention, message.channel.mention))

def setup(bot):
    bot.add_cog(Logs(bot))
