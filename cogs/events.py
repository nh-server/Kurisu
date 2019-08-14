import asyncio
import discord
import re

from collections import deque
from cogs.checks import check_staff_id
from cogs.database import DatabaseCog
from discord.ext import commands
from subprocess import call
from string import printable
from urllib.parse import urlparse


class Events(DatabaseCog):
    """
    Special event handling.
    """

    def __init__(self, bot):
        super().__init__(bot)
        self.bot.temp_guilds = {}

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
        'usbh3lper',
        'funkii',
        'funkey',
        'funk11',
        'freeshp',
        'frees.hop',
        'fr*eeshop',
        'frappeshop',
        'frickshop',
        'usbheler',
        'usbhelper',
        'frishop',
        'eshopfree',
        'erappêshop',
        'fręëšhøp',
        'fbimod',
        'freakshop',
        'fleashop',
        'ciangle',
        'fieashop',
        'fefosheep',
        'freebrew',
        'villain3ds',
        'vi11ain3ds',
        'vi1lain3ds',
        'vil1ain3ds',
        'villian3ds',
        'vi11ian3ds',
        'vi1lian3ds',
        'vil1ian3ds',
        'cdnfx',
        'exhop',
        'exshop',
        'enxhop',
        'goodshop',
        'exnhop',  # typo of the above, not sure how common
        'enxshop',  # also typo
        'cdnsp',
        'wareznx',
        'wareznext',
        'softcobra',
        'uwizard',
        'jnustool',
        'nusgrabber',
        'fr33$h0p',
        'fshop',  # common outright bypass, but not sure if it will interact with legitimate words
        'free.shop',
        'fréeshop',
        'freéshop',
        'frééshop',
        'frèeshop',
        'freèshop',
        'frèèshop',
        'freêshop',
        'frêeshop',
        'frêêshop',
        'stargatenx',
        'homebrewgeneralshop',
        'hbgshop',
        '/hbg/shop',
        '\hbg\shop',
        'hbgsh0p',
        'stargate',
        'freestore',
        'sxinstaller',

        #'sxos',
    )

    # use the full ID, including capitalization and dashes
    piracy_video_ids = (
        'VWFe_n7AhKs',
    )

    # terms that should cause a notice but not auto-delete
    piracy_tools_alert = (
        'freshop',
        'feeshop',
        'notabug',
        #'sx',
        #'tx',
        'sxos',
        'operationidroid',
        'hbg',
    )

    drama_alert = ()

    ignored_file_extensions = (
        '.jpg',
        '.jpeg',
        '.gif',
        '.png',
        '.bmp',
        '.tiff',
        '.psd',
        '.sed',
    )

    # unbanning stuff
    unbanning_stuff = (
        'unbanmii',
        'easymode9',
    )

    # piracy sites
    piracy_sites = (
        '3dsiso',
        '3dschaos',
        'wiiuiso',
        'madloader',
        'darkumbra',
        'chaosgamez',
        'maxconsole',
        'emuparadise',
        'loveroms',
        'coolrom',
        'romsmania',
        'completeroms',
        'romhustler',
        'doperoms',
        'freeroms',
        'portableroms',
        'portalroms',
        'romulation',
        'emulator.games',
        '3dscia',
        'darksoftware',
        'ziperto',
        'cdromance',
        'emurom',
        'r/3dspiracy',
        'r/wiiupiracy',
        'pokemoner',
        'ndspassion',
        'inmortalgamespro',
        'romsmode',
        'arcadepunks',
        'romstorage',
        'enikon',
        'vimm',
        'r/roms',
        'xecuterrocks',
    )

    approved_guilds = (
        'C29hYvh',  # Nintendo Homebrew
        'ZdqEhed',  # Reswitched
        'qgEeK3E',  # Famicomunnity
        'yqSut8c',  # TWL Mode Hacking!
        'EZSxqRr',  # ACNL Modding
    )

    # I hate naming variables sometimes
    user_antispam = {}
    channel_antispam = {}
    help_notice_anti_repeat = []

    async def scan_message(self, message, is_edit=False):
        embed = discord.Embed()
        embed.description = message.content
        if await self.is_watched(message.author.id):
            content = f"**Channel**:\n[#{message.channel.name}](https://discordapp.com/channels/{str(message.guild.id)}/{message.channel.id}/{message.id})\n"
            msg = message.author.mention
            if message.attachments:
                content += "**Images**:\n"
                for c, f in enumerate(message.attachments):
                    if f.filename.lower().endswith(self.ignored_file_extensions):
                        content += f"[[{c + 1}]]({f.url}) "
                        if f == message.attachments[-1]:
                            content += "\n"
            if message.content:
                content += "**Message**:\n"
            embed.description = content + embed.description
            if is_edit:
                msg += " (edited)"
            await self.bot.channels['watch-logs'].send(msg, embed=embed)
        is_help_channel = message.channel in self.bot.assistance_channels
        msg = ''.join(char for char in message.content.lower() if char in printable)
        msg_no_separators = re.sub('[ \*_\-~]', '', msg)

        contains_invite_link = "discordapp.com/invite" in msg or "discord.gg" in msg or "join.skype.com" in msg
        contains_piracy_site_mention = any(x in msg for x in self.piracy_sites)
        contains_piracy_url_mention = any(x in msg for x in ('3ds.titlekeys', 'wiiu.titlekeys', 'titlekeys.com', '95.183.50.10',))
        contains_piracy_tool_mention = any(x in msg_no_separators for x in self.piracy_tools)

        # modified regular expresion made by deme72
        res = re.findall('(?:https?://)?(?:(?:(?:www\.)?youtube\.com(?:/(?:watch\?.*?v=([^&\s]+)(?:[^\s]))))|(?:youtu\.be/([^\s]+)))', message.content)
        contains_video = any(res)
        contains_piracy_video_id = False if not contains_video else any(x or y for x, y in res if x in self.piracy_video_ids or y in self.piracy_video_ids)

        res = re.findall('(?:discordapp\.com/invite|discord\.gg)/([\w]+)', message.content)
        temp_guilds = [x for x in res if x in self.bot.temp_guilds]
        contains_non_approved_invite = not all(x in self.approved_guilds or x in self.bot.temp_guilds for x in res)

        contains_piracy_tool_alert_mention = any(x in msg_no_separators for x in self.piracy_tools_alert)
        contains_piracy_site_mention_indirect = any(x in msg for x in ('iso site', 'chaos site',))
        contains_misinformation_url_mention = any(x in msg_no_separators for x in ('gudie.racklab', 'guide.racklab', 'gudieracklab', 'guideracklab', 'lyricly.github.io', 'lyriclygithub', 'strawpoii', 'hackinformer.com', 'console.guide', 'jacksorrell.co.uk', 'jacksorrell.tv', 'nintendobrew.com', 'reinx.guide', 'NxpeNwz', 'scenefolks.com'))
        contains_unbanning_stuff = any(x in msg_no_separators for x in self.unbanning_stuff)

        # contains_guide_mirror_mention = any(x in msg for x in ('3ds-guide.b4k.co',))
        contains_drama_alert = any(x in msg_no_separators for x in self.drama_alert)

        for f in message.attachments:
            if not f.filename.lower().endswith(self.ignored_file_extensions):
                embed2 = discord.Embed(description=f"Size: {f.size}\nMessage: [{message.channel.name}]({message.jump_url})\nDownload: [{f.filename}]({f.url})")
                await self.bot.channels['upload-logs'].send(f"📎 **Attachment**: {message.author.mention} uploaded to {message.channel.mention}", embed=embed2)
        if contains_invite_link:
            await self.bot.channels['message-logs'].send(f"✉️ **Invite posted**: {message.author.mention} posted an invite link in {message.channel.mention} {'(message deleted)' if contains_non_approved_invite else ''}\n------------------\n{self.bot.escape_text(message.content)}")
            if contains_non_approved_invite:
                try:
                    await message.delete()
                except discord.NotFound:
                    pass

                try:
                    await message.author.send(f"Please read {self.bot.channels['welcome-and-rules'].mention}. Server invites must be approved by staff. To contact staff send a message to <@333857992170536961>.")
                except discord.errors.Forbidden:
                    pass
            if temp_guilds:
                for guild in temp_guilds:
                    try:
                        self.bot.temp_guilds[guild] -= 1
                    except KeyError:
                        continue
                    if self.bot.temp_guilds[guild] <= 0:
                        del self.bot.temp_guilds[guild]

        if contains_misinformation_url_mention:
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
            try:
                await message.author.send(f"Please read {self.bot.channels['welcome-and-rules'].mention}. This site may be misinterpreted as legitimate and cause users harm, therefore your message was automatically deleted.", embed=embed)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await self.bot.channels['message-logs'].send(f"**Bad site**: {message.author.mention} mentioned a blocked site in {message.channel.mention} (message deleted)", embed=embed)
        if contains_drama_alert:
            await self.bot.channels['message-logs'].send(f"**Potential drama/heated debate Warning**: {message.author.mention} posted a blacklisted word in {message.channel.mention}", embed=embed)
        if contains_piracy_tool_mention:
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
            try:
                await message.author.send(f"Please read {self.bot.channels['welcome-and-rules'].mention}. You cannot mention tools used for piracy, therefore your message was automatically deleted.", embed=embed)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await self.bot.channels['message-logs'].send(f"**Bad tool**: {message.author.mention} mentioned a piracy tool in {message.channel.mention} (message deleted)", embed=embed)
        if contains_piracy_video_id:
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
            try:
                await message.author.send(f"Please read {self.bot.channels['welcome-and-rules'].mention}. You cannot link videos that mention piracy, therefore your message was automatically deleted.", embed=embed)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await self.bot.channels['message-logs'].send(f"**Bad video**: {message.author.mention} linked a banned video in {message.channel.mention} (message deleted)", embed=embed)
        if contains_piracy_tool_alert_mention:
            await self.bot.channels['message-logs'].send(f"**Bad tool**: {message.author.mention} likely mentioned a piracy tool in {message.channel.mention}", embed=embed)
        if contains_piracy_site_mention or contains_piracy_url_mention:
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
            try:
                await message.author.send(f"Please read {self.bot.channels['welcome-and-rules'].mention}. You cannot mention sites used for piracy directly, therefore your message was automatically deleted.", embed=embed)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await self.bot.channels['message-logs'].send(f"**Bad site**: {message.author.mention} mentioned a piracy site directly in {message.channel.mention} (message deleted)", embed=embed)
        elif contains_piracy_site_mention_indirect:
            if is_help_channel:
                try:
                    await message.delete()
                except discord.errors.NotFound:
                    pass
                try:
                    await message.author.send(f"Please read {self.bot.channels['welcome-and-rules'].mention}. You cannot mention sites used for piracy in the help-and-questions channels directly or indirectly, therefore your message was automatically deleted.", embed=embed)
                except discord.errors.Forbidden:
                    pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await self.bot.channels['message-logs'].send(f"**Bad site**: {message.author.mention} mentioned a piracy site indirectly in {message.channel.mention}{' (message deleted)' if is_help_channel else ''}", embed=embed)
        if contains_unbanning_stuff:
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
            try:
                await message.author.send(f"Please read {self.bot.channels['welcome-and-rules'].mention}. You cannot mention sites, programs or services used for unbanning, therefore your message was automatically deleted.", embed=embed)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await self.bot.channels['message-logs'].send(f"**Bad site**: {message.author.mention} mentioned an unbanning site/service/program directly in {message.channel.mention} (message deleted)", embed=embed)
        if contains_video and message.channel in self.bot.assistance_channels:
            await self.bot.channels['message-logs'].send(f"▶️ **Video posted**: {message.author.mention} posted a video in {message.channel.mention}\n------------------\n{message.clean_content}")

        # check for guide mirrors and post the actual link
        urls = re.findall(r'(https?://\S+)', msg)
        to_replace = []
        for url in urls:
            ps = urlparse(url)
            if ps.netloc.startswith('3ds-guide.b4k.co'):
                to_replace.append(ps._replace(netloc='3ds.hacks.guide').geturl())
            elif ps.netloc.startswith('hax.b4k.co') and ps.path.startswith('/3ds/guide'):
                to_replace.append(ps._replace(netloc='3ds.guide', path=ps.query[2:], query='').geturl())
        if to_replace:
            msg_user = f"Please read {self.bot.channels['welcome-and-rules'].mention}. Guide mirrors may not be linked to, therefore your message was automatically deleted.\nPlease link to <https://3ds.guide> or <https://wiiu.guide> directly instead of mirrors of the sites.\n\nThe official equivalents of the links are:"
            for url in to_replace:
                msg_user += '\n• ' + url
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
            try:
                await message.author.send(msg_user, embed=embed)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await self.bot.channels['message-logs'].send(
                f"**Bad site**: {message.author.mention} mentioned a blocked guide mirror in {message.channel.mention} (message deleted)", embed=embed)

        # check for mention spam
        if len(message.mentions) >= 6 and not self.bot.roles['Helpers'] in message.author.roles:
            log_msg = f"🚫 **Auto-probate**: {message.author.mention} probated for mass user mentions | {message.author}\n🗓 __Creation__: {message.author.created_at}\n🏷 __User ID__: {message.author.id}"
            embed = discord.Embed(title="Deleted message", color=discord.Color.gold())
            embed.add_field(name="#" + message.channel.name,
                            value="\u200b" + message.content)
            await self.bot.channels['mod-logs'].send(log_msg, embed=embed)
            await self.bot.channels['mods'].send(log_msg + f"\nSee {self.bot.channels['mod-logs'].mention} for the deleted message. @here")
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
            try:
                await message.author.send(f"You were automatically placed under probation in {self.bot.guild.name} for mass user mentions.")
            except discord.errors.Forbidden:
                pass
            await self.add_restriction(message.author.id, self.bot.roles['Probation'])
            await message.author.add_roles(self.bot.roles['Probation'])

    async def user_spam_check(self, message):
        if message.author.id not in self.user_antispam:
            self.user_antispam[message.author.id] = []
        self.user_antispam[message.author.id].append(message)
        if len(self.user_antispam[message.author.id]) == 6:  # it can trigger it multiple times if I use >. it can't skip to a number so this should work
            await message.author.add_roles(self.bot.roles['Muted'])
            await self.add_restriction(message.author.id, self.bot.roles['Muted'])
            msg_user = f"You were automatically muted for sending too many messages in a short period of time!\n\nIf you believe this was done in error, send a direct message to one of the staff in {self.bot.channels['welcome-and-rules'].mention}."
            try:
                await message.author.send(msg_user)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            log_msg = f"🔇 **Auto-muted**: {message.author.mention} muted for spamming | {message.author}\n🗓 __Creation__: {message.author.created_at}\n🏷 __User ID__: {message.author.id}"
            embed = discord.Embed(title="Deleted messages", color=discord.Color.gold())
            msgs_to_delete = self.user_antispam[message.author.id][:]  # clone list so nothing is removed while going through it
            for msg in msgs_to_delete:
                embed.add_field(name="#"+msg.channel.name, value="\u200b" + msg.content)  # added zero-width char to prevent an error with an empty string (lazy workaround)
            await self.bot.channels['mod-logs'].send(log_msg, embed=embed)
            await self.bot.channels['mods'].send(log_msg + f"\nSee {self.bot.channels['mod-logs'].mention} for a list of deleted messages.")
            for msg in msgs_to_delete:
                try:
                    await msg.delete()
                except discord.errors.NotFound:
                    pass  # don't fail if the message doesn't exist
        await asyncio.sleep(3)
        self.user_antispam[message.author.id].remove(message)
        try:
            if len(self.user_antispam[message.author.id]) == 0:
                self.user_antispam.pop(message.author.id)
        except KeyError:
            pass  # if the array doesn't exist, don't raise an error

    async def user_ping_check(self, message):
        if "p" + str(message.author.id) not in self.user_antispam:
            self.user_antispam["p" + str(message.author.id)] = deque()
        self.user_antispam["p" + str(message.author.id)].append((message, len(message.mentions)))
        _, user_mentions = zip(*self.user_antispam["p" + str(message.author.id)])
        if sum(user_mentions) > 6:
            await self.add_restriction(message.author, self.bot.roles["Probation"])
            await message.author.add_roles(self.bot.roles['Probation'])
            msg_user = f"You were automatically placed under probation for mentioning too many users in a short period of time!\n\nIf you believe this was done in error, send a direct message to one of the staff in {self.bot.channels['welcome-and-rules'].mention}."
            try:
                await message.author.send(msg_user)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            log_msg = f"🚫 **Auto-probated**: {message.author.mention} probated for mass user mentions | {message.author}\n🗓 __Creation__: {message.author.created_at}\n🏷 __User ID__: {message.author.id}"
            embed = discord.Embed(title="Deleted messages", color=discord.Color.gold())
            msgs_to_delete = self.user_antispam["p" + message.author.id].copy()  # clone list so nothing is removed while going through it
            for msg in msgs_to_delete:
                embed.add_field(name="#"+msg[0].channel.name, value="\u200b" + msg[0].content)  # added zero-width char to prevent an error with an empty string (lazy workaround)
            await self.bot.channels['mod-logs'].send(log_msg, embed=embed)
            await self.bot.channels['mods'].send(log_msg + f"\nSee {self.bot.channels['mod-logs'].mention} for a list of deleted messages. @here")
            for msg in msgs_to_delete:
                try:
                    await msg[0].delete()
                except discord.errors.NotFound:
                    pass  # don't fail if the message doesn't exist
            self.user_antispam["p" + message.author.id].clear()
        else:
            await asyncio.sleep(10)
            self.user_antispam["p" + str(message.author.id)].popleft()
        try:
            if len(self.user_antispam["p" + str(message.author.id)]) == 0:
                self.user_antispam.pop("p" + str(message.author.id))
        except KeyError:
            pass  # if the array doesn't exist, don't raise an error

    async def channel_spam_check(self, message):
        if message.channel.id not in self.channel_antispam:
            self.channel_antispam[message.channel.id] = []
        self.channel_antispam[message.channel.id].append(message)
        if len(self.channel_antispam[message.channel.id]) == 22:  # it can trigger it multiple times if I use >. it can't skip to a number so this should work
            await message.channel.set_permission(self.bot.guild.default_role, send_messages=False)
            msg_channel = "This channel has been automatically locked for spam. Please wait while staff review the situation."
            embed = discord.Embed(title="Deleted messages", color=discord.Color.gold())
            # msgs_to_delete = self.user_antispam[message.author.id][:]  # clone list so nothing is removed while going through it
            # for msg in msgs_to_delete:
            #     embed.add_field(name="@"+self.bot.help_command.remove_mentions(msg.author), value="\u200b" + msg.content)  # added zero-width char to prevent an error with an empty string (lazy workaround)
            await message.channel.send(msg_channel)
            log_msg = f"🔒 **Auto-locked**: {message.channel.mention} locked for spam"
            await self.bot.channels['mod-logs'].send(log_msg, embed=embed)
            await self.bot.channels['mods'].send(f"{log_msg} @here\nSee {self.bot.channels['mod-logs'].mention} for a list of deleted messages.")
            # msgs_to_delete = self.channel_antispam[message.channel.id][:]  # clone list so nothing is removed while going through it
            # for msg in msgs_to_delete:
            #     try:
            #         await self.bot.delete_message(msg)
            #     except discord.errors.NotFound:
            #         pass  # don't fail if the message doesn't exist
        await asyncio.sleep(5)
        self.channel_antispam[message.channel.id].remove(message)
        try:
            if len(self.channel_antispam[message.channel.id]) == 0:
                self.channel_antispam.pop(message.channel.id)
        except KeyError:
            pass  # if the array doesn't exist, don't raise an error

    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.abc.PrivateChannel):
            return
        if message.author.name == "GitHub" and message.author.discriminator == "0000":
            if message.embeds[0].title.startswith('[Kurisu:port]'):
                await self.bot.channels['helpers'].send("Automatically pulling changes!")
                call(['git', 'pull'])
                await self.bot.channels['helpers'].send("Restarting bot...")
                await self.bot.close()
            return
        await self.bot.wait_until_all_ready()
        if message.author == message.guild.me or await check_staff_id(self, 'Helper', message.author.id) or await self.check_nofilter(message.channel):  # don't process messages by the bot or staff or in the helpers channel
            return
        await self.scan_message(message)
        self.bot.loop.create_task(self.user_ping_check(message))
        self.bot.loop.create_task(self.user_spam_check(message))
        self.bot.loop.create_task(self.channel_spam_check(message))

    @commands.Cog.listener()
    async def on_message_edit(self, message_before, message_after):
        if isinstance(message_before.channel, discord.abc.PrivateChannel):
            return
        await self.bot.wait_until_all_ready()
        try:
            if await self.check_nofilter(message_before.channel):
                return
            if message_after.author == self.bot.guild.me or await check_staff_id(self, 'Helper', message_after.author.id) or await self.check_nofilter(message_after.channel):  # don't process messages by the bot or staff or in the helpers channel
                return
            if message_before.content == message_after.content:
                return
            await self.scan_message(message_after, is_edit=True)
        except AttributeError:
            pass  # I need to figure this out eventually. at the moment there's no real harm doing this.


def setup(bot):
    bot.add_cog(Events(bot))
