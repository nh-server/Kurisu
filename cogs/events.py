from __future__ import annotations

import asyncio
import discord
import re
import random

from collections import deque
from discord.ext import commands
from string import printable
from subprocess import call
from typing import TYPE_CHECKING
from utils.checks import check_staff_id
from utils import crud, utils

if TYPE_CHECKING:
    from kurisu import Kurisu


class Events(commands.Cog):
    """
    Special event handling.
    """

    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot

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
    userbot_yeeter: dict[int, list] = {}
    channel_antispam: dict[int, list] = {}

    async def userbot_yeeter_pop(self, message: discord.Message):
        await asyncio.sleep(20)
        self.userbot_yeeter[message.author.id].remove(message.channel)
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
        embed = discord.Embed(color=utils.gen_color(message.id))
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
        msg = ''.join(char for char in message.content.lower() if char in printable)
        msg_no_separators = re.sub(r'[ *_\-~]', '', msg)

        log_msg, wf_matches = self.bot.wordfilter.search_word(msg)
        lf_matches = self.bot.levenshteinfilter.search_site(msg, 'scamming site')
        contains_video, contains_piracy_video = self.bot.wordfilter.search_video(msg)
        approved_invites, non_approved_invites = self.bot.invitefilter.search_invite(message.content)
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
                f"{self.bot.escape_text(message.content)}")
            if non_approved_invites:
                try:
                    await message.delete()
                except discord.NotFound:
                    pass
                try:
                    await message.author.send(
                        f"Please read {self.bot.channels['welcome-and-rules'].mention}. "
                        f"Server invites must be approved by staff. To contact staff send a message to <@333857992170536961>.")
                except discord.errors.Forbidden:
                    pass
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

        if wf_matches['piracy tool']:
            embed.description = log_msg
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
            await utils.send_dm_message(message.author,
                                        f"Please read {self.bot.channels['welcome-and-rules'].mention}. "
                                        f"You cannot mention tools used for piracy directly or indirectly, "
                                        f"therefore your message was automatically deleted.",
                                        embed=embed)
            await self.bot.channels['message-logs'].send(
                f"**Bad tool**: {message.author.mention} mentioned a piracy tool in {message.channel.mention} (message deleted)",
                embed=embed)

        if lf_matches:
            embed.description = msg
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
            await self.bot.channels['message-logs'].send(
                f"**Scamming Site**: {message.author.mention} likely mentioned a scamming site in {message.channel.mention} (message deleted)",
                embed=embed)

        if contains_piracy_video:
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
        if wf_matches['piracy tool alert']:
            embed.description = log_msg
            await self.bot.channels['message-logs'].send(
                f"**Bad tool**: {message.author.mention} likely mentioned a piracy tool in {message.channel.mention}",
                embed=embed)
        if wf_matches['piracy site']:
            embed.description = log_msg
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
            await utils.send_dm_message(message.author,
                                        f"Please read {self.bot.channels['welcome-and-rules'].mention}. "
                                        f"You cannot mention sites used for piracy directly or indirectly, "
                                        f"therefore your message was automatically deleted.",
                                        embed=embed)
            await self.bot.channels['message-logs'].send(
                f"**Bad site**: {message.author.mention} mentioned a piracy site directly in {message.channel.mention} (message deleted)",
                embed=embed)

        if wf_matches['unbanning tool']:
            embed.description = log_msg
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

        if lf_matches or wf_matches['scamming site']:
            if message.author.id not in self.userbot_yeeter:
                self.userbot_yeeter[message.author.id] = []
            if message.channel not in self.userbot_yeeter[message.author.id]:
                self.userbot_yeeter[message.author.id].append(message.channel)
                if len(self.userbot_yeeter[message.author.id]) == 2:
                    msg = ("You have been banned from Nintendo Homebrew for linking scamming sites in multiple channels. "
                           "If you think this is a mistake contact ❅FrozenFire❆#0700 on discord or send a email to staff@nintendohomebrew.com")
                    await utils.send_dm_message(message.author, msg)
                    self.bot.actions.append('wb:' + str(message.author.id))
                    await message.author.ban(reason="Linking scamming links in multiple channels.")
                    try:
                        await message.delete()
                    except discord.errors.NotFound:
                        pass
                    return
                else:
                    self.bot.loop.create_task(self.userbot_yeeter_pop(message))

        if wf_matches['scamming site']:
            embed.description = log_msg
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
            await crud.add_permanent_role(message.author.id, self.bot.roles['Probation'].id)
            await message.author.add_roles(self.bot.roles['Probation'])
            await utils.send_dm_message(message.author,
                                        f"Please read {self.bot.channels['welcome-and-rules'].mention}. "
                                        f"You have been probated for posting a link to a scamming site.",
                                        embed=embed)
            await self.bot.channels['message-logs'].send(
                f"**Bad site**: {message.author.mention} mentioned a scamming site in {message.channel.mention} (message deleted, user probated)",
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
            msg_user = "You were automatically muted for sending too many messages in a short period of time!\n\n" \
                       "If you believe this was done in error, send a direct message (DM) to <@!333857992170536961> to contact staff."
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
            msg_user = "You were automatically placed under probation for mentioning too many users in a short period of time!\n\n" \
                       "If you believe this was done in error, send a direct message (DM) to <@!333857992170536961> to contact staff."
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


async def setup(bot):
    await bot.add_cog(Events(bot))
