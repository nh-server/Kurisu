import asyncio
import discord
import re

from collections import deque
from discord.ext import commands
from urllib.parse import urlparse
from string import printable
from subprocess import call
from typing import List
from utils.checks import check_staff_id
from utils import crud, utils


class Events(commands.Cog):
    """
    Special event handling.
    """

    def __init__(self, bot):
        self.bot = bot

    def search_word(self, words: str, msg_no_sep: str, message: str) -> List[re.Match]:
        dect_words = []
        matches = []
        for word in words:
            if word in msg_no_sep:
                dect_words.append(word)
        if dect_words:
            for word in dect_words:
                if match := self.bot.wordfilter.word_exp[word].search(message):
                    matches.append(match)
        return matches

    def highlight_matches(self, matches: List[re.Match], message: str) -> str:
        msg = message
        for match in matches:
            a, b = match.span(0)
            msg = f"{msg[:a]}**{match.group(0)}**{msg[b:]}"
        return msg

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

    # I hate naming variables sometimes
    user_antispam = {}
    channel_antispam = {}
    help_notice_anti_repeat = []

    async def scan_message(self, message, is_edit=False):
        embed = discord.Embed()
        embed.description = message.content
        if await crud.is_watched(message.author.id):
            content = f"**Channel**:\n[#{message.channel.name}]({message.jump_url})\n"
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
        msg_no_separators = re.sub(r'[ *_\-~]', '', msg)

        contains_skype_link = "join.skype.com" in msg
        contains_piracy_site_mention = self.search_word(self.bot.wordfilter.filter['piracy site'], msg_no_separators, msg)
        contains_piracy_tool_mention = self.search_word(self.bot.wordfilter.filter['piracy tool'], msg_no_separators, msg)

        # modified regular expresion made by deme72
        res = re.findall(r'(?:(?:https?://)?(?:www.)?)(?:(?:youtube\.com/watch\?v=)|(?:youtu\.be/))([aA-zZ_\-\d]{11})', message.content)
        contains_video = any(res)
        contains_piracy_video_id = False if not contains_video else any(x for x in res if x in self.bot.wordfilter.filter['piracy video'])

        res = re.findall(r'(?:discordapp\.com/invite|discord\.gg)/([\w]+)', message.content)
        approved_invites = [x for x in self.bot.invitefilter.invites if x.code in res]
        contains_non_approved_invite = len(res) != len(approved_invites)

        contains_piracy_tool_alert_mention = self.search_word(self.bot.wordfilter.filter['piracy tool alert'], msg_no_separators, msg)
        contains_piracy_site_mention_indirect = any(x in msg for x in ('iso site', 'chaos site',))
        contains_misinformation_url_mention = any(x in msg_no_separators for x in ('gudie.racklab', 'guide.racklab', 'gudieracklab', 'guideracklab', 'lyricly.github.io', 'lyriclygithub', 'strawpoii', 'hackinformer.com', 'console.guide', 'jacksorrell.co.uk', 'jacksorrell.tv', 'nintendobrew.com', 'reinx.guide', 'NxpeNwz', 'scenefolks.com'))
        contains_unbanning_stuff = self.search_word(self.bot.wordfilter.filter['unbanning tool'], msg_no_separators, msg)
        contains_invite_link = contains_non_approved_invite or contains_skype_link or approved_invites
        # contains_guide_mirror_mention = any(x in msg for x in ('3ds-guide.b4k.co',))
        contains_drama_alert = self.search_word(self.bot.wordfilter.filter['drama'], msg_no_separators, msg)

        for f in message.attachments:
            if not f.filename.lower().endswith(self.ignored_file_extensions):
                embed2 = discord.Embed(description=f"Size: {f.size}\n"
                                                   f"Message: [{message.channel.name}]({message.jump_url})\n"
                                                   f"Download: [{f.filename}]({f.url})")
                await self.bot.channels['upload-logs'].send(f"📎 **Attachment**: {message.author.mention} "
                                                            f"uploaded to {message.channel.mention}", embed=embed2)
        if contains_invite_link:
            await self.bot.channels['message-logs'].send(
                f"✉️ **Invite posted**: {message.author.mention} posted an invite link in {message.channel.mention}"
                f" {'(message deleted)' if contains_non_approved_invite else ''}"
                f"\n------------------\n"
                f"{self.bot.escape_text(message.content)}")
            if contains_non_approved_invite:
                try:
                    await message.delete()
                except discord.NotFound:
                    pass
                try:
                    await message.author.send(
                        f"Please read {self.bot.channels['welcome-and-rules'].mention}. "
                        "Server invites must be approved by staff. To contact staff send a message to <@333857992170536961>.")
                except discord.errors.Forbidden:
                    pass
            if approved_invites:
                for invite in approved_invites:
                    if invite.is_temporary:
                        if invite.uses > 1:
                            await self.bot.invitefilter.set_uses(code=invite.code, uses=invite.uses - 1)
                        else:
                            await self.bot.invitefilter.delete(code=invite.code)

        if contains_misinformation_url_mention:
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
            await utils.send_dm_message(message.author,
                                        f"Please read {self.bot.channels['welcome-and-rules'].mention}. "
                                        f"This site may be misinterpreted as legitimate and cause users harm, therefore your message was automatically deleted.",
                                        embed=embed)
            await self.bot.channels['message-logs'].send(
                f"**Bad site**: {message.author.mention} mentioned a blocked site in {message.channel.mention} (message deleted)",
                embed=embed)
        if contains_drama_alert:
            embed.description = contains_drama_alert
            await self.bot.channels['message-logs'].send(
                f"**Potential drama/heated debate Warning**: {message.author.mention} posted a blacklisted word in {message.channel.mention}",
                embed=embed)
        if contains_piracy_tool_mention:
            embed.description = self.highlight_matches(contains_piracy_tool_mention, msg)
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
            await utils.send_dm_message(message.author,
                                        f"Please read {self.bot.channels['welcome-and-rules'].mention}. "
                                        f"You cannot mention tools used for piracy, therefore your message was automatically deleted.",
                                        embed=embed)
            await self.bot.channels['message-logs'].send(
                f"**Bad tool**: {message.author.mention} mentioned a piracy tool in {message.channel.mention} (message deleted)",
                embed=embed)
        if contains_piracy_video_id:
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
            await utils.send_dm_message(message.author,
                                        f"Please read {self.bot.channels['welcome-and-rules'].mention}. "
                                        f"You cannot link videos that mention piracy, therefore your message was automatically deleted.",
                                        embed=embed)
            await self.bot.channels['message-logs'].send(
                f"**Bad video**: {message.author.mention} linked a banned video in {message.channel.mention} (message deleted)",
                embed=embed)
        if contains_piracy_tool_alert_mention:
            embed.description = self.highlight_matches(contains_piracy_tool_alert_mention, msg)
            await self.bot.channels['message-logs'].send(
                f"**Bad tool**: {message.author.mention} likely mentioned a piracy tool in {message.channel.mention}",
                embed=embed)
        if contains_piracy_site_mention:
            embed.description = self.highlight_matches(contains_piracy_site_mention, msg)
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
            await utils.send_dm_message(message.author,
                                        f"Please read {self.bot.channels['welcome-and-rules'].mention}. "
                                        f"You cannot mention sites used for piracy directly, therefore your message was automatically deleted.",
                                        embed=embed)
            await self.bot.channels['message-logs'].send(
                f"**Bad site**: {message.author.mention} mentioned a piracy site directly in {message.channel.mention} (message deleted)",
                embed=embed)
        elif contains_piracy_site_mention_indirect:
            if is_help_channel:
                try:
                    await message.delete()
                except discord.errors.NotFound:
                    pass
                await utils.send_dm_message(message.author,
                                            f"Please read {self.bot.channels['welcome-and-rules'].mention}. "
                                            f"You cannot mention sites used for piracy in the help-and-questions channels directly or indirectly, "
                                            f"therefore your message was automatically deleted.",
                                            embed=embed)
            await self.bot.channels['message-logs'].send(
                f"**Bad site**: {message.author.mention} mentioned a piracy site indirectly in {message.channel.mention}{' (message deleted)' if is_help_channel else ''}",
                embed=embed)
        if contains_unbanning_stuff:
            embed.description = self.highlight_matches(contains_unbanning_stuff, msg)
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
            await utils.send_dm_message(message.author,
                                        f"Please read {self.bot.channels['welcome-and-rules'].mention}. "
                                        f"You cannot mention sites, programs or services used for unbanning, therefore your message was automatically deleted.",
                                        embed=embed)
            await self.bot.channels['message-logs'].send(
                f"**Bad site**: {message.author.mention} mentioned an unbanning site/service/program directly in {message.channel.mention} (message deleted)",
                embed=embed)
        if contains_video and message.channel in self.bot.assistance_channels:
            await self.bot.channels['message-logs'].send(
                f"▶️ **Video posted**: {message.author.mention} posted a video in {message.channel.mention}\n------------------\n{message.clean_content}")

        # check for guide mirrors and post the actual link
        urls = re.findall(r'(https?://\S+)', msg)
        to_replace = []
        for url in set(urls):
            ps = urlparse(url)
            if ps.netloc.startswith('3ds-guide.b4k.co'):
                to_replace.append(ps._replace(netloc='3ds.hacks.guide').geturl())
            elif ps.netloc.startswith('hax.b4k.co') and ps.path.startswith('/3ds/guide'):
                to_replace.append(ps._replace(netloc='3ds.guide', path=ps.query[2:], query='').geturl())
        if to_replace:
            msg_user = f"Please read {self.bot.channels['welcome-and-rules'].mention}. " \
                       f"Guide mirrors may not be linked to, therefore your message was automatically deleted.\n" \
                       f"Please link to <https://3ds.guide> or <https://wiiu.guide> directly instead of mirrors of the sites.\n\n" \
                       f"The official equivalents of the links are:"
            for url in to_replace:
                msg_user += '\n• ' + url
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
            await utils.send_dm_message(message.author, msg_user, embed=embed)
            await self.bot.channels['message-logs'].send(
                f"**Bad site**: {message.author.mention} mentioned a blocked guide mirror in {message.channel.mention} (message deleted)",
                embed=embed)

        # check for mention spam
        if len(message.mentions) >= 6 and not self.bot.roles['Helpers'] in message.author.roles:
            log_msg = f"🚫 **Auto-probate**: {message.author.mention} probated for mass user mentions | {message.author}\n" \
                      f"🗓 __Creation__: {message.author.created_at}\n🏷 __User ID__: {message.author.id}"
            embed = discord.Embed(title="Deleted message", color=discord.Color.gold())
            embed.add_field(name="#" + message.channel.name, value="\u200b" + message.content)
            await self.bot.channels['mod-logs'].send(log_msg, embed=embed)
            await self.bot.channels['mods'].send(
                f"{log_msg}\nSee {self.bot.channels['mod-logs'].mention} for the deleted message. @here",
                allowed_mentions=discord.AllowedMentions(everyone=True))
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
            await utils.send_dm_message(
                message.author, f"You were automatically placed under probation in {self.bot.guild.name} for mass user mentions.")
            await crud.add_permanent_role(message.author.id, self.bot.roles['Probation'].id)
            await message.author.add_roles(self.bot.roles['Probation'])

    async def user_spam_check(self, message):
        if message.author.id not in self.user_antispam:
            self.user_antispam[message.author.id] = []
        self.user_antispam[message.author.id].append(message)
        # it can trigger it multiple times if I use >. it can't skip to a number so this should work
        if len(self.user_antispam[message.author.id]) == 6:
            await message.author.add_roles(self.bot.roles['Muted'])
            await message.author.remove_roles(self.bot.roles['#elsewhere'], self.bot.roles['#art-discussion'])
            await crud.add_permanent_role(message.author.id, self.bot.roles['Muted'].id)
            msg_user = f"You were automatically muted for sending too many messages in a short period of time!\n\n" \
                       f"If you believe this was done in error, send a direct message to one of the staff in {self.bot.channels['welcome-and-rules'].mention}."
            await utils.send_dm_message(message.author, msg_user)
            log_msg = f"🔇 **Auto-muted**: {message.author.mention} muted for spamming | {message.author}\n🗓 __Creation__: {message.author.created_at}\n🏷 __User ID__: {message.author.id}"
            embed = discord.Embed(title="Deleted messages", color=discord.Color.gold())
            # clone list so nothing is removed while going through it
            msgs_to_delete = self.user_antispam[message.author.id][:]
            for msg in msgs_to_delete:
                embed.add_field(name="#" + msg.channel.name,
                                value="\u200b" + msg.content)  # added zero-width char to prevent an error with an empty string (lazy workaround)
            await self.bot.channels['mod-logs'].send(log_msg, embed=embed)
            await self.bot.channels['mods'].send(
                f"{log_msg}\nSee {self.bot.channels['mod-logs'].mention} for a list of deleted messages.")
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
        key = "p" + str(message.author.id)
        if key not in self.user_antispam:
            self.user_antispam[key] = deque()
        self.user_antispam[key].append((message, len(message.mentions)))
        _, user_mentions = zip(*self.user_antispam[key])
        if sum(user_mentions) > 6:
            await crud.add_permanent_role(message.author, self.bot.roles["Probation"].id)
            await message.author.add_roles(self.bot.roles['Probation'])
            msg_user = f"You were automatically placed under probation for mentioning too many users in a short period of time!\n\n" \
                       f"If you believe this was done in error, send a direct message to one of the staff in {self.bot.channels['welcome-and-rules'].mention}."
            await utils.send_dm_message(message.author, msg_user)
            log_msg = f"🚫 **Auto-probated**: {message.author.mention} probated for mass user mentions | {message.author}\n" \
                      f"🗓 __Creation__: {message.author.created_at}\n🏷 __User ID__: {message.author.id}"
            embed = discord.Embed(title="Deleted messages", color=discord.Color.gold())
            # clone list so nothing is removed while going through it
            msgs_to_delete = self.user_antispam[key].copy()
            for msg in msgs_to_delete:
                # added zero-width char to prevent an error with an empty string (lazy workaround)
                embed.add_field(name="#" + msg[0].channel.name, value="\u200b" + msg[0].content)
            await self.bot.channels['mod-logs'].send(log_msg, embed=embed)
            await self.bot.channels['mods'].send(
                f"{log_msg}\nSee {self.bot.channels['mod-logs'].mention} for a list of deleted messages. @here",
                allowed_mentions=discord.AllowedMentions(everyone=True))
            for msg in msgs_to_delete:
                try:
                    await msg[0].delete()
                except discord.errors.NotFound:
                    pass  # don't fail if the message doesn't exist
            self.user_antispam[key].clear()
        else:
            await asyncio.sleep(10)
            self.user_antispam[key].popleft()
        try:
            if len(self.user_antispam[key]) == 0:
                self.user_antispam.pop(key)
        except KeyError:
            pass  # if the array doesn't exist, don't raise an error

    async def channel_spam_check(self, message):
        if message.channel.id not in self.channel_antispam:
            self.channel_antispam[message.channel.id] = []
        self.channel_antispam[message.channel.id].append(message)
        # it can trigger it multiple times if I use >. it can't skip to a number so this should work
        if len(self.channel_antispam[message.channel.id]) == 22:
            await message.channel.set_permission(self.bot.guild.default_role, send_messages=False)
            msg_channel = "This channel has been automatically locked for spam. Please wait while staff review the situation."
            embed = discord.Embed(title="Deleted messages", color=discord.Color.gold())
            # msgs_to_delete = self.user_antispam[message.author.id][:]  # clone list so nothing is removed while going through it
            # for msg in msgs_to_delete:
            #     embed.add_field(name="@"+self.bot.help_command.remove_mentions(msg.author), value="\u200b" + msg.content)  # added zero-width char to prevent an error with an empty string (lazy workaround)
            await message.channel.send(msg_channel)
            log_msg = f"🔒 **Auto-locked**: {message.channel.mention} locked for spam"
            await self.bot.channels['mod-logs'].send(log_msg, embed=embed)
            await self.bot.channels['mods'].send(f"{log_msg} @here\nSee {self.bot.channels['mod-logs'].mention} for a list of deleted messages.",
                                                 allowed_mentions=discord.AllowedMentions(everyone=True))
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
        if not self.bot.IS_DOCKER:
            if message.author.name == "GitHub" and message.author.discriminator == "0000":
                if message.embeds[0].title.startswith('[Kurisu:port]'):
                    await self.bot.channels['helpers'].send("Automatically pulling changes!")
                    call(['git', 'pull'])
                    await self.bot.channels['helpers'].send("Restarting bot...")
                    await self.bot.close()
                return
        await self.bot.wait_until_all_ready()
        if message.author == message.guild.me or await check_staff_id('Helper', message.author.id) \
                or await crud.check_nofilter(message.channel):
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
        if await crud.check_nofilter(message_before.channel):
            return
        if message_after.author == self.bot.guild.me or await check_staff_id('Helper', message_after.author.id) \
                or await crud.check_nofilter(message_after.channel):
            return
        if message_before.content == message_after.content:
            return
        await self.scan_message(message_after, is_edit=True)


def setup(bot):
    bot.add_cog(Events(bot))
