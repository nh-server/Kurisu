from __future__ import annotations

import asyncio
import datetime
import discord
import re
import random

from collections import deque
from discord.ext import commands
from string import printable
from subprocess import call
from typing import TYPE_CHECKING
from utils.checks import check_staff
from utils.utils import send_dm_message, gen_color
from utils import Restriction
from utils.database import FilterKind

if TYPE_CHECKING:
    from kurisu import Kurisu
    from typing import Deque


class Events(commands.Cog):
    """
    Special event handling.
    """

    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.configuration = bot.configuration
        self.filters = self.bot.filters

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
    user_ping_antispam: dict[int, Deque[tuple[discord.Message, int]]] = {}
    user_message_antispam: dict[int, list[discord.Message]] = {}
    userbot_yeeter: dict[int, list[discord.abc.MessageableChannel]] = {}
    channel_antispam: dict[int, list[discord.Message]] = {}
    invite_antispam: dict[int, list[discord.Message]] = {}

    async def userbot_yeeter_pop(self, message: discord.Message):
        await asyncio.sleep(20)
        self.userbot_yeeter[message.author.id].remove(message.channel)
        try:
            if len(self.userbot_yeeter[message.author.id]) == 0:
                self.userbot_yeeter.pop(message.author.id)
        except KeyError:
            pass

    async def invite_spam_pop(self, message: discord.Message):
        await asyncio.sleep(20)
        self.invite_antispam[message.author.id].remove(message)
        try:
            if len(self.userbot_yeeter[message.author.id]) == 0:
                self.userbot_yeeter.pop(message.author.id)
        except KeyError:
            pass

    async def scan_message(self, message: discord.Message, is_edit=False):
        # Some assumptions that should be true always
        assert isinstance(message.channel, (discord.TextChannel, discord.VoiceChannel, discord.Thread))
        assert isinstance(message.author, discord.Member)
        random.seed(message.id)
        embed = discord.Embed(color=gen_color(message.id))
        embed.description = message.content
        if message.author.id in self.configuration.watch_list:
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
        msg = ''.join(char for char in message.content.lower() if char in printable)
        msg_no_separators = re.sub(r'[ *_\-~]', '', msg)

        filter_result = self.filters.match_filtered_words(msg_no_separators) | self.filters.match_levenshtein_words(message.content)
        contains_video = any(re.findall(r'((?:https?://)?(?:www.)?)(?:(youtube\.com/watch\?v=)|(youtu\.be/))([aA-zZ_\-\d]{11})', message.content))
        approved_invites, non_approved_invites = self.filters.search_invite(message.content)
        contains_misinformation_url_mention = any(x in msg_no_separators for x in ('gudie.racklab', 'guide.racklab', 'gudieracklab', 'guideracklab', 'lyricly.github.io', 'lyriclygithub', 'strawpoii', 'hackinformer.com', 'console.guide', 'jacksorrell.co.uk', 'jacksorrell.tv', 'nintendobrew.com', 'reinx.guide', 'NxpeNwz', 'scenefolks.com', 'rentry.co'))
        contains_invite_link = approved_invites or non_approved_invites

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
                f" {'(message deleted)' if non_approved_invites else ''}"
                f"\n------------------\n"
                f"{self.bot.escape_text(message.content)}", suppress_embeds=any(non_approved_invites))
            if non_approved_invites:
                try:
                    await message.delete()
                except discord.NotFound:
                    pass
                if message.author.id not in self.invite_antispam:
                    self.invite_antispam[message.author.id] = []
                self.invite_antispam[message.author.id].append(message)
                if len(self.invite_antispam[message.author.id]) > 3:
                    await send_dm_message(message.author, "You have been kicked from Nintendo Homebrew for spamming invites to non approved servers.")
                    try:
                        self.bot.actions.append(f"wk:{message.author.id}")
                        await message.author.kick(reason="Spamming server invites.")
                    except (discord.Forbidden, discord.NotFound):
                        self.bot.actions.remove(f"wk:{message.author.id}")
                else:
                    self.bot.loop.create_task(self.invite_spam_pop(message))
                    try:
                        await message.author.send(
                            f"Please read {self.bot.channels['welcome-and-rules'].mention}. "
                            f"Server invites must be approved by staff. To contact staff send a message to <@333857992170536961>.")
                    except discord.errors.Forbidden:
                        pass
            # if the message was deleted don't reduce approved invites uses
            else:
                for invite in approved_invites:
                    if invite.uses != -1:
                        if invite.uses > 1:
                            await self.filters.update_invite_use(invite.code)
                        else:
                            await self.filters.delete_approved_invite(invite.code)

        if contains_misinformation_url_mention:
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
            await send_dm_message(message.author,
                                  f"Please read {self.bot.channels['welcome-and-rules'].mention}. "
                                  f"This site may be misinterpreted as legitimate and cause users harm, therefore your message was automatically deleted.",
                                  embed=embed)
            await self.bot.channels['message-logs'].send(
                f"**Bad site**: {message.author.mention} mentioned a blocked site in {message.channel.mention} (message deleted)",
                embed=embed)

        if FilterKind.PiracyTool in filter_result:
            embed.description = message.content
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
            await send_dm_message(message.author,
                                  f"Please read {self.bot.channels['welcome-and-rules'].mention}. "
                                  f"You cannot mention tools used for piracy directly or indirectly, "
                                  f"therefore your message was automatically deleted.",
                                  embed=embed)
            await self.bot.channels['message-logs'].send(
                f"**Bad tool**: {message.author.mention} mentioned a piracy tool (`{filter_result[FilterKind.PiracyTool]}`) in {message.channel.mention} (message deleted)",
                embed=embed)

        if FilterKind.PiracyVideo in filter_result:
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
            await send_dm_message(message.author,
                                  f"Please read {self.bot.channels['welcome-and-rules'].mention}. "
                                  f"You cannot link videos that mention piracy, therefore your message was automatically deleted.",
                                  embed=embed)
            await self.bot.channels['message-logs'].send(
                f"**Bad video**: {message.author.mention} linked a banned video (`{filter_result[FilterKind.PiracyVideo]}`) in {message.channel.mention} (message deleted)",
                embed=embed)

        if FilterKind.PiracyToolAlert in filter_result:
            embed.description = message.content
            await self.bot.channels['message-logs'].send(
                f"**Bad tool**: {message.author.mention} likely mentioned a piracy tool (`{filter_result[FilterKind.PiracyToolAlert]}`) in {message.channel.mention}",
                embed=embed)

        if FilterKind.PiracySite in filter_result:
            embed.description = message.content
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
            await send_dm_message(message.author,
                                  f"Please read {self.bot.channels['welcome-and-rules'].mention}. "
                                  f"You cannot mention sites used for piracy directly or indirectly, "
                                  f"therefore your message was automatically deleted.",
                                  embed=embed)
            await self.bot.channels['message-logs'].send(
                f"**Bad site**: {message.author.mention} mentioned a piracy site directly (`{filter_result[FilterKind.PiracySite]}`) in {message.channel.mention} (message deleted)",
                embed=embed)

        if FilterKind.UnbanningTool in filter_result:
            embed.description = message.content
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
            await send_dm_message(message.author,
                                  f"Please read {self.bot.channels['welcome-and-rules'].mention}. "
                                  f"You cannot mention sites, programs or services used for unbanning, therefore your message was automatically deleted.",
                                  embed=embed)
            await self.bot.channels['message-logs'].send(
                f"**Bad site**: {message.author.mention} mentioned an unbanning site/service/program directly (`{filter_result[FilterKind.UnbanningTool]}`) in {message.channel.mention} (message deleted)",
                embed=embed)

        if contains_video and message.channel in self.bot.assistance_channels:
            await self.bot.channels['message-logs'].send(
                f"▶️ **Video posted**: {message.author.mention} posted a video in {message.channel.mention}\n------------------\n{message.clean_content}")

        if FilterKind.ScammingSite in filter_result:
            embed.description = message.content

            try:
                await message.delete()
            except discord.errors.NotFound:
                pass

            if message.author.id not in self.userbot_yeeter:
                self.userbot_yeeter[message.author.id] = []
            if message.channel not in self.userbot_yeeter[message.author.id]:
                self.userbot_yeeter[message.author.id].append(message.channel)
                if len(self.userbot_yeeter[message.author.id]) == 2:
                    msg = ("You have been banned from Nintendo Homebrew for linking scamming sites in multiple channels. "
                           "If you think this is a mistake contact ❅FrozenFire❆#0700 on discord or send a email to staff@nintendohomebrew.com")
                    await send_dm_message(message.author, msg)
                    self.bot.actions.append(f'wb:{message.author.id}')
                    await message.author.ban(reason="Linking scamming links in multiple channels.", delete_message_days=0)
                    try:
                        await message.delete()
                    except discord.errors.NotFound:
                        pass
                    return
                else:
                    self.bot.loop.create_task(self.userbot_yeeter_pop(message))
            await self.bot.restrictions.add_restriction(message.author, Restriction.Probation, reason="Linking scamming site")
            try:
                await message.author.add_roles(self.bot.roles['Probation'])
            except discord.NotFound:
                # Sometimes they get banned before the bot can apply the role
                pass
            await send_dm_message(message.author,
                                  f"Please read {self.bot.channels['welcome-and-rules'].mention}. "
                                  f"You have been probated for posting a link to a scamming site.",
                                  embed=embed)
            await self.bot.channels['message-logs'].send(
                f"**Bad site**: {message.author.mention} mentioned a scamming site (`{filter_result[FilterKind.ScammingSite]}`) in {message.channel.mention} (message deleted, user probated)",
                embed=embed)
            await self.bot.channels['mods'].send(
                f"🔇 **Auto-probated**: {message.author.mention} probated for linking scamming site | {message.author}\n"
                f"🗓 __Creation__: {message.author.created_at}\n"
                f"🏷__User ID__: {message.author.id}\n"
                f"See {self.bot.channels['message-logs'].mention} for the deleted message. @here",
                allowed_mentions=discord.AllowedMentions(everyone=True))

        # check for mention spam
        if len(message.mentions) >= 6:
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
            await send_dm_message(
                message.author, f"You were automatically placed under probation in {self.bot.guild.name} for mass user mentions.")
            await self.bot.restrictions.add_restriction(message.author, Restriction.Probation, reason="Mention spam")
            await message.author.add_roles(self.bot.roles['Probation'])

    async def user_spam_check(self, message: discord.Message):
        assert isinstance(message.author, discord.Member)
        assert isinstance(message.channel, (discord.abc.GuildChannel, discord.Thread))
        if message.author.id not in self.user_message_antispam:
            self.user_message_antispam[message.author.id] = []
        self.user_message_antispam[message.author.id].append(message)
        # it can trigger it multiple times if I use >. it can't skip to a number so this should work
        if len(self.user_message_antispam[message.author.id]) == 6:
            try:
                await message.author.timeout(datetime.timedelta(days=2))
            except discord.Forbidden:
                # If the bot can't time out the member it's quite likely they shouldn't be timed out for this anyway
                return
            msg_user = "You were automatically timed-out for sending too many messages in a short period of time!\n\n" \
                       "If you believe this was done in error, send a direct message (DM) to <@!333857992170536961> to contact staff."
            await send_dm_message(message.author, msg_user)
            log_msg = f"🔇 **Auto-timeout**: {message.author.mention} timed out for spamming | {message.author}\n🗓 __Creation__: {message.author.created_at}\n🏷 __User ID__: {message.author.id}"
            embed = discord.Embed(title="Deleted messages", color=discord.Color.gold())
            # clone list so nothing is removed while going through it
            msgs_to_delete = self.user_message_antispam[message.author.id][:]
            for msg in msgs_to_delete:
                assert isinstance(msg.channel, (discord.abc.GuildChannel, discord.Thread))
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
        self.user_message_antispam[message.author.id].remove(message)
        try:
            if len(self.user_message_antispam[message.author.id]) == 0:
                self.user_message_antispam.pop(message.author.id)
        except KeyError:
            pass  # if the array doesn't exist, don't raise an error

    async def user_ping_check(self, message: discord.Message):
        assert isinstance(message.author, discord.Member)
        key = message.author.id
        if key not in self.user_ping_antispam:
            self.user_ping_antispam[key] = deque()
        self.user_ping_antispam[key].append((message, len(message.mentions)))
        user_mentions: tuple[int]
        _, user_mentions = zip(*self.user_ping_antispam[key])  # type: ignore # type checker can't infer correct type
        if sum(user_mentions) > 6:
            await self.bot.restrictions.add_restriction(message.author, Restriction.Probation, reason="User ping check")
            msg_user = ("You were automatically placed under probation "
                        "for mentioning too many users in a short period of time!\n\n"
                        "If you believe this was done in error, send a direct "
                        "message (DM) to <@!333857992170536961> to contact staff.")
            await send_dm_message(message.author, msg_user)
            log_msg = f"🚫 **Auto-probated**: {message.author.mention} probated for mass user mentions | {message.author}\n" \
                      f"🗓 __Creation__: {message.author.created_at}\n🏷 __User ID__: {message.author.id}"
            embed = discord.Embed(title="Deleted messages", color=discord.Color.gold())
            # clone list so nothing is removed while going through it
            msgs_to_delete = self.user_ping_antispam[key].copy()
            for msg in msgs_to_delete:
                assert isinstance(msg[0].channel, (discord.abc.GuildChannel, discord.Thread))
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
            self.user_ping_antispam[key].clear()
        else:
            await asyncio.sleep(10)
            self.user_ping_antispam[key].popleft()
        try:
            if len(self.user_ping_antispam[key]) == 0:
                self.user_ping_antispam.pop(key)
        except KeyError:
            pass  # if the array doesn't exist, don't raise an error

    async def channel_spam_check(self, message: discord.Message):
        assert isinstance(message.channel, (discord.abc.GuildChannel, discord.Thread))
        if message.channel.id not in self.channel_antispam:
            self.channel_antispam[message.channel.id] = []
        self.channel_antispam[message.channel.id].append(message)
        # it can trigger it multiple times if I use >. it can't skip to a number so this should work
        if len(self.channel_antispam[message.channel.id]) == 22:
            if isinstance(message.channel, (discord.VoiceChannel, discord.TextChannel)):
                await message.channel.set_permissions(self.bot.guild.default_role, send_messages=False)
                msg_channel = "This channel has been automatically locked for spam. Please wait while staff review the situation."
                await message.channel.send(msg_channel)
            embed = discord.Embed(title="Deleted messages", color=discord.Color.gold())
            # msgs_to_delete = self.channel_antispam[message.author.id][:]  # clone list so nothing is removed while going through it
            # for msg in msgs_to_delete:
            #     embed.add_field(name="@"+self.bot.help_command.remove_mentions(msg.author), value="\u200b" + msg.content)  # added zero-width char to prevent an error with an empty string (lazy workaround)
            log_msg = f"🔒 **Auto-locked**: {message.channel.mention} locked for spam"
            await self.bot.channels['mod-logs'].send(log_msg, embed=embed)
            await self.bot.channels['mods'].send(f"{log_msg} @here\nSee {self.bot.channels['mod-logs'].mention} for a list of deleted messages.",
                                                 allowed_mentions=discord.AllowedMentions(everyone=True))
            msgs_to_delete = self.channel_antispam[message.channel.id][:]  # clone list so nothing is removed while going through it
            for msg in msgs_to_delete:
                try:
                    await msg.delete()
                except discord.errors.NotFound:
                    pass  # don't fail if the message doesn't exist
        await asyncio.sleep(5)
        self.channel_antispam[message.channel.id].remove(message)
        try:
            if len(self.channel_antispam[message.channel.id]) == 0:
                self.channel_antispam.pop(message.channel.id)
        except KeyError:
            pass  # if the array doesn't exist, don't raise an error

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None or message.author.bot:
            return
        if not self.bot.IS_DOCKER:
            if message.author.name == "GitHub" and message.author.discriminator == "0000":
                if message.embeds and message.embeds[0].title and message.embeds[0].title.startswith('[Kurisu:port]'):
                    await self.bot.channels['helpers'].send("Automatically pulling changes!")
                    call(['git', 'pull'])
                    await self.bot.channels['helpers'].send("Restarting bot...")
                    await self.bot.close()
                return
        await self.bot.wait_until_all_ready()
        if message.author == message.guild.me or check_staff(self.bot, 'Helper', message.author.id) \
                or message.channel.id in self.bot.configuration.nofilter_list:
            return
        await self.scan_message(message)
        self.bot.loop.create_task(self.user_ping_check(message))
        self.bot.loop.create_task(self.user_spam_check(message))
        self.bot.loop.create_task(self.channel_spam_check(message))

    @commands.Cog.listener()
    async def on_message_edit(self, message_before: discord.Message, message_after: discord.Message):
        if message_after.guild is None or message_after.author.bot:
            return
        await self.bot.wait_until_all_ready()
        if message_after.author == message_after.guild.me or check_staff(self.bot, 'Helper', message_after.author.id) \
                or message_after.channel.id in self.bot.configuration.nofilter_list:
            return
        if message_before.content == message_after.content:
            return
        await self.scan_message(message_after, is_edit=True)


async def setup(bot):
    await bot.add_cog(Events(bot))
