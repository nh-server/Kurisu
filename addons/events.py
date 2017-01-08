import discord
import re
from discord.ext import commands
from sys import argv

class Events:
    """
    Special event handling.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    piracy_tools = [
        'freeshop',
        'free shop',
        'fr3eshop',
        'fr33shop',
        'fre3shop',
        'ciangel',
        'cia angel',
        'tikdevil',
        'tikshop',
        'FR335H0P',
        'fr€€shop',
        'fr€€sh0p',
        'fr3e sh0p',
    ]

    async def scan_message(self, message):
        if message.author == self.bot.server.me or self.bot.staff_role in message.author.roles or message.channel == self.bot.helpers_channel:  # don't process messages by the bot or staff or in the helpers channel
            return
        embed = discord.Embed()
        embed.description = message.content
        if message.author.id in self.bot.watching:
            await self.bot.send_message(self.bot.messagelogs_channel, "**Watch log**: {} in {}".format(message.author.mention, message.channel.mention), embed=embed)
        is_help_channel = message.channel.name[0:5] == "help-"
        msg = message.content.lower()
        contains_invite_link = "discordapp.com/invite" in msg or "discord.gg" in msg
        # special check for a certain thing
        contains_fs_repo_url = re.match('(.*)notabug\.org\/(.*)\/freeshop(.*)', msg, re.IGNORECASE)
        contains_piracy_site_mention = any(x in msg for x in ('3dsiso', '3dschaos'))
        contains_piracy_url_mention = any(x in msg for x in ('3ds.titlekeys', 'wiiu.titlekeys', 'titlekeys.com'))
        contains_piracy_tool_mention = any(x in msg for x in self.piracy_tools)
        contains_piracy_site_mention_indirect = any(x in msg for x in ('iso site', 'chaos site'))
        if contains_invite_link:
            await self.bot.send_message(self.bot.messagelogs_channel, "✉️ **Invite posted**: {} posted an invite link in {}\n------------------\n{}".format(message.author.mention, message.channel.mention, message.content))
        if contains_fs_repo_url != None:
            try:
                await self.bot.delete_message(message)
            except discord.errors.NotFound:
                pass
            await self.bot.send_message(message.author, "Please read #welcome-and-rules. You cannot link to tools used for piracy, therefore your message was automatically deleted.", embed=embed)
            await self.bot.send_message(self.bot.messagelogs_channel, "**Bad URL**: {} posted a freeShop Repo URL in {} (message deleted)".format(message.author.mention, message.channel.mention), embed=embed)
        if contains_piracy_tool_mention:
            try:
                await self.bot.delete_message(message)
            except discord.errors.NotFound:
                pass
            await self.bot.send_message(message.author, "Please read #welcome-and-rules. You cannot mention tools used for piracy, therefore your message was automatically deleted.", embed=embed)
            await self.bot.send_message(self.bot.messagelogs_channel, "**Bad tool**: {} mentioned a piracy tool in {} (message deleted)".format(message.author.mention, message.channel.mention), embed=embed)
        if contains_piracy_site_mention or contains_piracy_url_mention:
            try:
                await self.bot.delete_message(message)
            except discord.errors.NotFound:
                pass
            await self.bot.send_message(message.author, "Please read #welcome-and-rules. You cannot mention sites used for piracy directly, therefore your message was automatically deleted.", embed=embed)
            await self.bot.send_message(self.bot.messagelogs_channel, "**Bad site**: {} mentioned a piracy site directly in {} (message deleted)".format(message.author.mention, message.channel.mention), embed=embed)
        elif contains_piracy_site_mention_indirect:
            if is_help_channel:
                try:
                    await self.bot.delete_message(message)
                except discord.errors.NotFound:
                    pass
                await self.bot.send_message(message.author, "Please read #welcome-and-rules. You cannot mention sites used for piracy in the help-and-questions channels directly or indirectly, therefore your message was automatically deleted.", embed=embed)
            await self.bot.send_message(self.bot.messagelogs_channel, "**Bad site**: {} mentioned a piracy site indirectly in {}{}".format(message.author.mention, message.channel.mention, " (message deleted)" if is_help_channel else ""), embed=embed)

    async def on_message(self, message):
        await self.bot.wait_until_ready()
        await self.scan_message(message)

    async def on_message_edit(self, message_before, message_after):
        await self.bot.wait_until_ready()
        await self.scan_message(message_after)

def setup(bot):
    bot.add_cog(Events(bot))
