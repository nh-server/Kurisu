import asyncio
import discord
import json
import re
from discord.ext import commands
from subprocess import call
from string import printable
from sys import argv
from urllib.parse import urlparse

class Events:
    """
    Special event handling.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    # don't add spaces or dashes to words
    piracy_tools = (
        'freeshop',
        'frepshop',
        'fr3eshop',
        'fr33shop',
        'fre3shop',
        'ciangel',
        'ciaangel',
        'tikdevil',
        'tikshop',
        'fr335h0p',
        'fr€€shop',
        'fr€€sh0p',
        'fr3esh0p',
        'fr//shop',
        'fr//sh0p',
        'free$hop',
        'fr$$hop',
        'friishop',
        'fr££shop',
        'fr£€shop',
        'fr£shop',
        'fr£eshop',
        'fre£shop',
        'fr€£shop',
        'threeshop',
        'thr33shop',
        'thr££shop',
        'thr£eshop',
        'thr33shop',
        'fr33sh0p',
        'fresh0p',
        'fr$shop',
        'freesho',
        'freeshoandp',
        'freeshothenp',
        'freeeshop',
        'makiedition',
        'makiversion',
        'makifbi',
        'utikdownloadhelper',
        'wiiuusbhelper',
        'w11uusbh3lper'
        'funkii',
        'funk11',
        'freeshp',
        'frees.hop',
        'fr*eeshop',
        'frappeshop',
        'frickshop',
        'usbheler',
        'frishop',
        'eshopfree',
        'erappêshop',
        'fręëšhøp',
        'feeshop',
        'fbimod',
        'freakshop',
        'fleashop',
        'ciangle',
        'fieashop',
    )

    # terms that should cause a notice but not auto-delete
    piracy_tools_alert = (
        'freshop',
    )

    drama_alert = (
        'attackhelicopter',
        'gender',
        'faggot',
        # 'retarded',
        # 'cunt',
        'tranny',
        'nigger',
        'incest',
    )

    ignored_file_extensions = (
        '.jpg',
        '.jpeg',
        '.gif',
        '.png',
        '.bmp',
        '.tiff',
        '.psd',
    )

    # unbanning stuff
    unbanning_stuff = (
        'unbanmii',
    )

    # I hate naming variables sometimes
    user_antispam = {}
    channel_antispam = {}
    help_notice_anti_repeat = []

    async def add_restriction(self, member, rst):
        with open("data/restrictions.json", "r") as f:
            rsts = json.load(f)
        if member.id not in rsts:
            rsts[member.id] = []
        if rst not in rsts[member.id]:
            rsts[member.id].append(rst)
        with open("data/restrictions.json", "w") as f:
            json.dump(rsts, f)

    async def scan_message(self, message, is_edit=False):
        embed = discord.Embed()
        embed.description = message.content
        if message.author.id in self.bot.watching:
            msg = "{} in {}".format(message.author.mention, message.channel.mention)
            if is_edit:
                msg += " (edited)"
            await self.bot.send_message(self.bot.watchlogs_channel, msg, embed=embed)
        is_help_channel = "assistance" in message.channel.name
        msg = ''.join(char for char in message.content.lower() if char in printable)
        msg_no_separators = re.sub('[ -]', '', msg)

        contains_invite_link = "discordapp.com/invite" in msg or "discord.gg" in msg or "join.skype.com" in msg
        contains_piracy_site_mention = any(x in msg for x in ('3dsiso', '3dschaos', 'wiiuiso', 'madloader', 'darkumbra', 'chaosgamez',))
        contains_piracy_url_mention = any(x in msg for x in ('3ds.titlekeys', 'wiiu.titlekeys', 'titlekeys.com', '95.183.50.10',))
        contains_piracy_tool_mention = any(x in msg_no_separators for x in self.piracy_tools)
        contains_piracy_tool_alert_mention = any(x in msg_no_separators for x in self.piracy_tools_alert)
        contains_piracy_site_mention_indirect = any(x in msg for x in ('iso site', 'chaos site',))
        contains_misinformation_url_mention = any(x in msg_no_separators for x in ('gudie.racklab', 'guide.racklab', 'gudieracklab', 'guideracklab', 'lyricly.github.io', 'lyriclygithub', 'strawpoii', 'hackinformer.com', 'switchthem.es',))
        contains_unbanning_stuff = any(x in msg_no_separators for x in self.unbanning_stuff)

        # contains_guide_mirror_mention = any(x in msg for x in ('3ds-guide.b4k.co',))
        contains_drama_alert = any(x in msg_no_separators for x in self.drama_alert)

        for f in message.attachments:
            if not f["filename"].lower().endswith(self.ignored_file_extensions):
                embed2 = discord.Embed(description="Size: {}\nDownload: [{}]({})".format(f["size"], self.bot.escape_name(f["filename"]), f["url"]))
                await self.bot.send_message(self.bot.messagelogs_channel, "📎 **Attachment**: {} uploaded to {}".format(message.author.mention, message.channel.mention), embed=embed2)
        if contains_invite_link:
            await self.bot.send_message(self.bot.messagelogs_channel, "✉️ **Invite posted**: {} posted an invite link in {}\n------------------\n{}".format(message.author.mention, message.channel.mention, message.content))
        if contains_misinformation_url_mention:
            try:
                await self.bot.delete_message(message)
            except discord.errors.NotFound:
                pass
            try:
                await self.bot.send_message(message.author, "Please read {}. This site may be misinterpreted as legitimate and cause users harm, therefore your message was automatically deleted.".format(self.bot.welcome_channel.mention), embed=embed)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await self.bot.send_message(self.bot.messagelogs_channel, "**Bad site**: {} mentioned a blocked site in {} (message deleted)".format(message.author.mention, message.channel.mention), embed=embed)
        if contains_drama_alert:
            #await self.bot.send_message(self.bot.messagelogs_channel, "✉️ **Potential drama/heated debate Warning**: {} posted a blacklisted word in {}\n------------------\n{}".format(message.author.mention, message.channel.mention, message.content))
            await self.bot.send_message(self.bot.messagelogs_channel, "**Potential drama/heated debate Warning**: {} posted a blacklisted word in {}".format(message.author.mention, message.channel.mention), embed=embed)
        if contains_piracy_tool_mention:
            try:
                await self.bot.delete_message(message)
            except discord.errors.NotFound:
                pass
            try:
                await self.bot.send_message(message.author, "Please read {}. You cannot mention tools used for piracy, therefore your message was automatically deleted.".format(self.bot.welcome_channel.mention), embed=embed)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await self.bot.send_message(self.bot.messagelogs_channel, "**Bad tool**: {} mentioned a piracy tool in {} (message deleted)".format(message.author.mention, message.channel.mention), embed=embed)
        if contains_piracy_tool_alert_mention:
            await self.bot.send_message(self.bot.messagelogs_channel, "**Bad tool**: {} likely mentioned a piracy tool in {}".format(message.author.mention, message.channel.mention), embed=embed)
        if contains_piracy_site_mention or contains_piracy_url_mention:
            try:
                await self.bot.delete_message(message)
            except discord.errors.NotFound:
                pass
            try:
                await self.bot.send_message(message.author, "Please read {}. You cannot mention sites used for piracy directly, therefore your message was automatically deleted.".format(self.bot.welcome_channel.mention), embed=embed)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await self.bot.send_message(self.bot.messagelogs_channel, "**Bad site**: {} mentioned a piracy site directly in {} (message deleted)".format(message.author.mention, message.channel.mention), embed=embed)
        elif contains_piracy_site_mention_indirect:
            if is_help_channel:
                try:
                    await self.bot.delete_message(message)
                except discord.errors.NotFound:
                    pass
                try:
                    await self.bot.send_message(message.author, "Please read {}. You cannot mention sites used for piracy in the help-and-questions channels directly or indirectly, therefore your message was automatically deleted.".format(self.bot.welcome_channel.mention), embed=embed)
                except discord.errors.Forbidden:
                    pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await self.bot.send_message(self.bot.messagelogs_channel, "**Bad site**: {} mentioned a piracy site indirectly in {}{}".format(message.author.mention, message.channel.mention, " (message deleted)" if is_help_channel else ""), embed=embed)
        if contains_unbanning_stuff:
            try:
                await self.bot.delete_message(message)
            except discord.errors.NotFound:
                pass
            try:
                await self.bot.send_message(message.author, "Please read {}. You cannot mention sites, programs or services used for unbanning, therefore your message was automatically deleted.".format(self.bot.welcome_channel.mention), embed=embed)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await self.bot.send_message(self.bot.messagelogs_channel, "**Bad site**: {} mentioned an unbanning site/service/program directly in {} (message deleted)".format(message.author.mention, message.channel.mention), embed=embed)

        # check for guide mirrors and post the actual link
        urls = re.findall(r'(https?://\S+)', msg)
        to_replace = []
        for url in urls:
            ps = urlparse(url)
            if ps.netloc.startswith('3ds-guide.b4k.co'):
                to_replace.append(ps._replace(netloc='3ds.guide').geturl())
        if to_replace:
            msg_user = "Please read {}. Guide mirrors may not be linked to, therefore your message was automatically deleted.\nPlease link to <https://3ds.guide> or <https://wiiu.guide> directly instead of mirrors of the sites.\n\nThe official equivalents of the links are:".format(self.bot.welcome_channel.mention)
            for url in to_replace:
                msg_user += '\n• ' + url
            try:
                await self.bot.delete_message(message)
            except discord.errors.NotFound:
                pass
            try:
                await self.bot.send_message(message.author, msg_user, embed=embed)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await self.bot.send_message(self.bot.messagelogs_channel, "**Bad site**: {} mentioned a blocked guide mirror in {} (message deleted)".format(message.author.mention, message.channel.mention), embed=embed)


    async def keyword_search(self, message):
        msg = ''.join(char for char in message.content.lower() if char in printable)
        if "wiiu" in message.channel.name and "download" in msg and "update" in msg and "manag" in msg:  # intentional typo in manage
            embed = discord.Embed(description="A failed update in Download Management does not mean there is an update and the system is trying to download it. This means your blocking method (DNS etc.) is working and the system can't check for an update.", color=discord.Color(0x009AC7))
            await self.bot.send_message(message.channel, message.author.mention, embed=embed)
        # search for terms that might indicate a question meant for the help channels
        help_embed = discord.Embed(description="Hello! If you are looking for help with setting up hacks for your 3DS or Wii U system, please ask your question in one of the assistance channels.\n\nFor 3DS, there is <#196635695958196224> or <#247557068490276864>. Ask in one of them.\n\nFor Wii U, go to <#279783073497874442>.\n\nThank you for stopping by!", color=discord.Color.green())
        help_embed.set_footer(text="This auto-response is under development. If you did not ask about the above, you don't need to do anything.")
        if message.author.id not in self.help_notice_anti_repeat:
            if message.channel.name == "hacking-general":
                if all(x in msg for x in ('help ', 'me',)):
                    await self.bot.send_message(message.channel, message.author.mention, embed=help_embed)
                    await self.bot.send_message(self.bot.mods_channel, "Auto-response test in {}".format(message.channel.mention))
                    self.help_notice_anti_repeat.append(message.author.id)
                    await asyncio.sleep(120)
                    try:
                        self.help_notice_anti_repeat.remove(message.author.id)
                    except ValueError:
                        pass

    async def user_spam_check(self, message):
        if message.author.id not in self.user_antispam:
            self.user_antispam[message.author.id] = []
        self.user_antispam[message.author.id].append(message)
        if len(self.user_antispam[message.author.id]) == 6:  # it can trigger it multiple times if I use >. it can't skip to a number so this should work
            await self.bot.add_roles(message.author, self.bot.muted_role)
            await self.add_restriction(message.author, "Muted")
            msg_user = "You were automatically muted for sending too many messages in a short period of time!\n\nIf you believe this was done in error, send a direct message to one of the staff in {}.".format(self.bot.welcome_channel.mention)
            try:
                await self.bot.send_message(message.author, msg_user)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            log_msg = "🔇 **Auto-muted**: {} muted for spamming | {}#{}\n🗓 __Creation__: {}\n🏷 __User ID__: {}".format(message.author.mention, message.author.name, message.author.discriminator, message.author.created_at, message.author.id)
            embed = discord.Embed(title="Deleted messages", color=discord.Color.gold())
            msgs_to_delete = self.user_antispam[message.author.id][:]  # clone list so nothing is removed while going through it
            for msg in msgs_to_delete:
                embed.add_field(name="#"+msg.channel.name, value="\u200b" + msg.content)  # added zero-width char to prevent an error with an empty string (lazy workaround)
            await self.bot.send_message(self.bot.modlogs_channel, log_msg, embed=embed)
            await self.bot.send_message(self.bot.mods_channel, log_msg + "\nSee {} for a list of deleted messages.".format(self.bot.modlogs_channel.mention))
            for msg in msgs_to_delete:
                try:
                    await self.bot.delete_message(msg)
                except discord.errors.NotFound:
                    pass  # don't fail if the message doesn't exist
        await asyncio.sleep(3)
        self.user_antispam[message.author.id].remove(message)
        try:
            if len(self.user_antispam[message.author.id]) == 0:
                self.user_antispam.pop(message.author.id)
        except KeyError:
            pass  # if the array doesn't exist, don't raise an error

    async def channel_spam_check(self, message):
        if message.channel.id not in self.channel_antispam:
            self.channel_antispam[message.channel.id] = []
        self.channel_antispam[message.channel.id].append(message)
        if len(self.channel_antispam[message.channel.id]) == 25:  # it can trigger it multiple times if I use >. it can't skip to a number so this should work
            overwrites_everyone = message.channel.overwrites_for(self.bot.everyone_role)
            overwrites_everyone.send_messages = False
            await self.bot.edit_channel_permissions(message.channel, self.bot.everyone_role, overwrites_everyone)
            msg_channel = "This channel has been automatically locked for spam. Please wait while staff review the situation."
            embed = discord.Embed(title="Deleted messages", color=discord.Color.gold())
            msgs_to_delete = self.user_antispam[message.author.id][:]  # clone list so nothing is removed while going through it
            for msg in msgs_to_delete:
                embed.add_field(name="@"+self.bot.escape_name(msg.author), value="\u200b" + msg.content)  # added zero-width char to prevent an error with an empty string (lazy workaround)
            await self.bot.send_message(message.channel, msg_channel)
            log_msg = "🔒 **Auto-locked**: {} locked for spam".format(message.channel.mention)
            await self.bot.send_message(self.bot.modlogs_channel, log_msg, embed=embed)
            await self.bot.send_message(self.bot.mods_channel, log_msg + " @here\nSee {} for a list of deleted messages.".format(self.bot.modlogs_channel.mention))
            msgs_to_delete = self.channel_antispam[message.channel.id][:]  # clone list so nothing is removed while going through it
            for msg in msgs_to_delete:
                try:
                    await self.bot.delete_message(msg)
                except discord.errors.NotFound:
                    pass  # don't fail if the message doesn't exist
        await asyncio.sleep(5)
        self.channel_antispam[message.channel.id].remove(message)
        try:
            if len(self.channel_antispam[message.channel.id]) == 0:
                self.channel_antispam.pop(message.channel.id)
        except KeyError:
            pass  # if the array doesn't exist, don't raise an error

    async def on_message(self, message):
        if message.channel.is_private:
            return
        if message.author.name == "GitHub" and message.author.discriminator == "0000":
            await self.bot.send_message(self.bot.helpers_channel, "Automatically pulling changes!")
            call(['git', 'pull'])
            await self.bot.close()
            return
        if message.channel.name.endswith('nofilter'):
            return
        await self.bot.wait_until_all_ready()
        if message.author == self.bot.server.me or self.bot.staff_role in message.author.roles or message.channel == self.bot.helpers_channel:  # don't process messages by the bot or staff or in the helpers channel
            return
        await self.scan_message(message)
        await self.keyword_search(message)
        self.bot.loop.create_task(self.user_spam_check(message))
        self.bot.loop.create_task(self.channel_spam_check(message))

    async def on_message_edit(self, message_before, message_after):
        if message_before.channel.name.endswith('nofilter'):
            return
        await self.bot.wait_until_all_ready()
        if message_after.author == self.bot.server.me or self.bot.staff_role in message_after.author.roles or message_after.channel == self.bot.helpers_channel:  # don't process messages by the bot or staff or in the helpers channel
            return
        await self.scan_message(message_after, is_edit=True)

def setup(bot):
    bot.add_cog(Events(bot))
