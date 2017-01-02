import discord
import re
from discord.ext import commands
from sys import argv

class Events:
    """
    Logs join and leave messages, bans and unbans, and member changes.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    async def on_message(self, message):
        if message.author == self.bot.server.me:  # don't process messages by the bot
            return
        msg = message.content.lower()
        contains_invite_link = "discordapp.com/invite" in msg or "discord.gg" in msg
        # special check for a certain thing
        contains_fs_url = re.match('(.*)notabug\.org\/(.*)\/freeshop(.*)', msg, re.IGNORECASE)
        if contains_invite_link:
            await self.bot.send_message(self.bot.mods_channel, "✉️ **Invite posted**: {} posted an invite link in {}".format(message.author.mention, message.channel.mention))
        if contains_fs_url != None:
            await self.bot.delete_message(message)
            await self.bot.send_message(self.bot.mods_channel, "**Bad URL**: {} posted a freeShop URL in {} (message deleted)".format(message.author.mention, message.channel.mention))

def setup(bot):
    bot.add_cog(Events(bot))
