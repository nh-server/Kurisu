from __future__ import annotations

import aiohttp
import discord
import inspect
import os
import random
import re
import string
import sys

from datetime import timedelta, datetime
from discord import app_commands, TextChannel, __version__ as discordpy_version
from discord. app_commands import Transform
from discord.ext import commands
from discord.utils import format_dt, snowflake_time, MISSING
from math import ceil
from Levenshtein import jaro_winkler
from typing import Optional, TYPE_CHECKING
from utils.checks import is_staff, check_if_user_can_sr, check_staff, is_staff_app
from utils.converters import DateOrTimeToSecondsConverter, HackMessageTransformer
from utils.utils import gen_color, send_dm_message, KurisuCooldown
from utils.views import BasePaginator, SimpleVoteView, PaginatedEmbedView

if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.context import KurisuContext, GuildContext
    from utils.database import Reminder

python_version = sys.version.split()[0]


class TagsPaginator(BasePaginator):

    def __init__(self, tags: list[str], tags_per_page: int = 10, colour: Optional[discord.Color] = None):
        super().__init__(n_pages=ceil(len(tags) / tags_per_page))
        self.tags = tags
        self.tags_per_page = tags_per_page
        self.colour = colour or discord.Colour.purple()

    def current(self):
        if embed := self.pages.get(self.idx):
            return embed
        else:
            index = self.idx * self.tags_per_page
            embed = self.create_embed(tags=self.tags[index:index + self.tags_per_page])
            self.pages[self.idx] = embed
            return embed

    def create_embed(self, tags: list[str]):
        embed = discord.Embed(color=self.colour)
        embed.title = "Tags list"
        embed.description = '\n'.join(f'{n+(self.tags_per_page * self.idx)}. {tag}' for n, tag in enumerate(tags, start=1))

        if self.n_pages > 1:
            embed.title += f" [{self.idx + 1}/{self.n_pages}]"
        return embed


class RemindersPaginator(BasePaginator):

    def __init__(self, reminders: list[Reminder], colour: discord.Color = discord.Colour.purple()):
        super().__init__(n_pages=len(reminders))
        self.reminders = reminders
        self.colour = colour

    def current(self):
        if embed := self.pages.get(self.idx):
            return embed
        else:
            embed = self.create_embed(reminder=self.reminders[self.idx])
            self.pages[self.idx] = embed
            return embed

    def create_embed(self, reminder: Reminder):
        embed = discord.Embed(color=self.colour)
        embed.title = f"Reminder {self.idx + 1}"
        embed.add_field(name='Content', value=reminder.content, inline=False)
        embed.add_field(name='Set to', value=format_dt(reminder.date), inline=False)

        if self.n_pages > 1:
            embed.title += f" [{self.idx + 1}/{self.n_pages}]"
        return embed


async def tag_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    cog: Extras = interaction.client.get_cog('Extras')
    if current:
        # very crude search but does the job
        choices = []
        n = 0
        for tag_name in cog.extras.tags:
            if jaro_winkler(tag_name, current, score_cutoff=0.6):
                choices.append(app_commands.Choice(name=tag_name, value=tag_name))
                n = n + 1
            if n == 25:
                break
        return choices
    else:
        return [app_commands.Choice(name=tag_title, value=tag_title) for tag_title in list(cog.extras.tags.keys())[:25]]


class Extras(commands.GroupCog):
    """
    Extra things.
    """
    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.emoji = discord.PartialEmoji.from_str('🎲')
        self.banned_tag_names = []
        self.nick_pattern = re.compile("^[a-z]{2,}.*$", re.RegexFlag.IGNORECASE)
        self.extras = self.bot.extras
        self.bot.loop.create_task(self.init())

    async def init(self):
        await self.bot.wait_until_all_ready()

        async for view in self.extras.get_voteviews('extras'):
            v = SimpleVoteView(self.bot, author_id=view[3], options=view[4].split('|'), custom_id=view[0], start=view[5], staff_only=view[6])
            self.bot.add_view(v, message_id=view[1])

        for cmd in self.tag.walk_commands():
            self.banned_tag_names.append(cmd.name)
            self.banned_tag_names.extend(cmd.aliases)

    prune_key = "nokey"

    def check_nickname(self, nickname):
        if match := self.nick_pattern.fullmatch(nickname):
            return len(nickname) <= 32
        else:
            return match

    @commands.command(hidden=True)
    async def env(self, ctx: KurisuContext):
        """Sends the bot environment"""
        msg = f'''
        Python {python_version}
        discord.py {discordpy_version}
        Is Docker: {bool(self.bot.IS_DOCKER)}
        Commit: {self.bot.commit}
        Branch: {self.bot.branch}
        '''
        await ctx.send(inspect.cleandoc(msg))

    @commands.command(aliases=['about'])
    async def kurisu(self, ctx: KurisuContext):
        """About Kurisu"""
        embed = discord.Embed(title="Kurisu", color=discord.Color.green())
        embed.set_author(name="Maintained by Nintendo Homebrew helpers and staff")
        embed.set_thumbnail(url="https://nintendohomebrew.com/assets/img/nhmemes/kurisu.jpg")
        embed.url = "https://github.com/nh-server/Kurisu"
        embed.description = "Kurisu, the Nintendo Homebrew Discord bot!"
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def membercount(self, ctx: GuildContext):
        """Prints the member count of the server."""
        await ctx.send(f"{ctx.guild.name} has {ctx.guild.member_count:,} members!")

    @commands.command()
    async def uptime(self, ctx: KurisuContext):
        """Print total uptime of the bot."""
        await ctx.send(f"Uptime: {datetime.now(self.bot.tz) - self.bot.startup}")

    @commands.guild_only()
    @is_staff("SuperOP")
    @commands.command(hidden=True, aliases=['copyrole', 'crp'])
    async def copyroleperms(self, ctx: GuildContext, role: discord.Role, src_channel: discord.TextChannel | discord.VoiceChannel, des_channels: commands.Greedy[discord.TextChannel | discord.VoiceChannel]):
        """Copy role overwrites from a channel to channels"""
        if any(type(c) != type(src_channel) for c in des_channels):
            return await ctx.send("Voice channels and text channel permissions are incompatible!")
        role_overwrites = src_channel.overwrites_for(role)
        for c in des_channels:
            await c.set_permissions(role, overwrite=role_overwrites)
        await ctx.send("Changed permissions successfully!")

    @commands.guild_only()
    @is_staff("SuperOP")
    @commands.command(hidden=True, aliases=['ccp'])
    async def copychannelperms(self, ctx: GuildContext, src_channel: discord.TextChannel | discord.VoiceChannel | discord.ForumChannel, des_channels: commands.Greedy[discord.TextChannel | discord.VoiceChannel | discord.ForumChannel]):
        """Copy channel overwrites from a channel to channels"""
        overwrites = src_channel.overwrites
        for c in des_channels:
            await c.edit(overwrites=overwrites)
        await ctx.send("Changed permissions successfully!")

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command(hidden=True)
    async def userroles(self, ctx: GuildContext, u: discord.Member = commands.Author):
        """Gets user roles and their id. Staff only."""
        msg = f"{u}'s Roles:\n\n"
        for role in u.roles:
            if role.is_default():
                continue
            msg += f"{role} = {role.id}\n"
        await ctx.author.send(msg)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command(hidden=True)
    async def serverroles(self, ctx: GuildContext, exp: str):
        """Gets the server roles and their id by regex. Staff only."""
        msg = f"Server roles matching `{exp}`:\n\n"
        try:
            reg_expr = re.compile(exp, re.IGNORECASE)
        except re.error:
            return await ctx.send("Invalid regex expression.")
        for role in ctx.guild.roles:
            if bool(reg_expr.search(role.name)):
                msg += f"{role.name} = {role.id}\n"
        await ctx.author.send(msg)

    @is_staff("OP")
    @commands.command(hidden=True)
    async def embedtext(self, ctx: KurisuContext, *, text):
        """Embed content."""
        await ctx.send(embed=discord.Embed(description=text))

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def prune30(self, ctx: GuildContext, key=""):
        """Prune members that are inactive for 30 days. Staff only."""
        if self.bot.pruning > 0:
            await ctx.send("Pruning is already in progress.")
            return
        if key != self.prune_key:
            if key != "":
                await ctx.send("That's not the correct key.")
            self.prune_key = ''.join(random.sample(string.ascii_letters, 8))
            await ctx.send(f"Are you sure you want to prune members inactive for 30 days?\n"
                           "To see how many members get kicked, use `.estprune`.\n"
                           f"To confirm the prune, use the command `.prune30 {self.prune_key}`.")
            return
        self.prune_key = ''.join(random.sample(string.ascii_letters, 8))
        await ctx.send("Starting pruning!")
        await ctx.guild.prune_members(days=30, compute_prune_count=False)
        self.bot.pruning = True
        await self.bot.channels['mods'].send(f"Prune started in {ctx.guild.name}!")
        msg = f"👢 **Prune**: {ctx.author.mention} started a prune."
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("HalfOP")
    @commands.command()
    async def disableleavelogs(self, ctx: KurisuContext):
        """DEBUG COMMAND"""
        self.bot.pruning = True
        await ctx.send("disable")

    @is_staff("HalfOP")
    @commands.command()
    async def enableleavelogs(self, ctx: KurisuContext):
        """DEBUG COMMAND"""
        self.bot.pruning = False
        await ctx.send("enable")

    @commands.command(name="32c3")
    async def _32c3(self, ctx: KurisuContext):
        """Console Hacking 2015"""
        await ctx.send("https://www.youtube.com/watch?v=bZczf57HSag")

    @commands.command(name="33c3")
    async def _33c3(self, ctx: KurisuContext):
        """Nintendo Hacking 2016"""
        await ctx.send("https://www.youtube.com/watch?v=8C5cn_Qj0G8")

    @commands.command(name="34c3")
    async def _34c3(self, ctx: KurisuContext):
        """Console Security - Switch"""
        await ctx.send("https://www.youtube.com/watch?v=Ec4NgWRE8ik")

    @is_staff("Owner")
    @commands.guild_only()
    @commands.command(hidden=True)
    async def dumpchannel(self, ctx: GuildContext, channel: TextChannel, limit=100):
        """Dump 100 messages from a channel to a file."""
        await ctx.send(f"Dumping {limit} messages from {channel.mention}")
        os.makedirs(f"#{channel.name}-{channel.id}", exist_ok=True)
        async for message in channel.history(limit=limit):
            with open(f"#{channel.name}-{channel.id}/{message.id}.txt", "w") as f:
                f.write(message.content)
        await ctx.send("Done!")

    @commands.guild_only()
    @commands.hybrid_command(hidden=True)
    async def togglechannel(self, ctx: GuildContext, channel_name: str):
        """Enable or disable access to specific channels.

        Args:
            channel_name: Name of the channel to toggle.
        """

        if not ctx.interaction:
            await ctx.message.delete()

        author = ctx.author

        if not ctx.interaction and ctx.channel != self.bot.channels['bot-cmds']:
            return await ctx.send(f"{ctx.author.mention}: .togglechannel can only be used in {self.bot.channels['bot-cmds'].mention}.", delete_after=10)

        if channel_name == "elsewhere":
            if self.bot.roles['#elsewhere'] in author.roles:
                await author.remove_roles(self.bot.roles['#elsewhere'])
                await ctx.send("Access to #elsewhere removed.", ephemeral=True, delete_after=10)
            elif self.bot.roles['No-elsewhere'] not in author.roles:
                await author.add_roles(self.bot.roles['#elsewhere'])
                await ctx.send("Access to #elsewhere granted.", ephemeral=True, delete_after=10)
            else:
                await send_dm_message(ctx.author, "Your access to elsewhere is restricted, contact staff to remove it.")
        elif channel_name == "artswhere":
            if self.bot.roles['#art-discussion'] in author.roles:
                await author.remove_roles(self.bot.roles['#art-discussion'])
                await ctx.send("Access to #art-discussion removed.", ephemeral=True, delete_after=10)
            elif self.bot.roles['No-art'] not in author.roles:
                await author.add_roles(self.bot.roles['#art-discussion'])
                await ctx.send("Access to #art-discussion granted.", ephemeral=True, delete_after=10)
            else:
                await ctx.send("Your access to #art-discussion is restricted, contact staff to remove it.", ephemeral=True, delete_after=10)
        else:
            await ctx.send(f"{channel_name} is not a valid toggleable channel.", ephemeral=True, delete_after=10)

    def check_message(self, message: discord.Message, author) -> Optional[str]:

        if not isinstance(message.channel, discord.abc.GuildChannel):
            return "Failed to fetch channel information."

        # xnoeproofing™
        if not message.channel.permissions_for(author).read_messages:
            return "bad xnoe, bad"

    async def create_ref(self, message: discord.Message, author: discord.Member, ref_text: bool, ref_image: bool, ref_author: bool) -> tuple[Optional[discord.Embed], Optional[discord.File]]:

        assert isinstance(message.channel, discord.abc.GuildChannel)

        embed = discord.Embed(colour=gen_color(message.author.id), timestamp=message.created_at)
        if ref_text and message.content:
            embed.description = message.content
        file = None
        # Attachments including content_type was added at a later date, so it can't be relied on for old attachments.
        if ref_image and len(message.attachments) > 0 and message.attachments[0].height and message.attachments[0].filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
            file = await message.attachments[0].to_file()
            embed.set_image(url=f"attachment://{file.filename}")
        if embed.description is None and embed.image.proxy_url is None:
            return None, None
        embed.set_author(name=message.author, icon_url=message.author.display_avatar.url, url=message.jump_url)
        embed.set_footer(text=f"in {message.channel.name}{f'. Ref by {author}' if ref_author else ''}")
        return embed, file

    @check_if_user_can_sr()
    @commands.guild_only()
    @commands.command(name='reference', aliases=['ref'])
    async def reference_message(self, ctx: GuildContext, message: discord.Message, ref_text: bool = True, ref_image: bool = True, ref_author: bool = False):
        """Creates an embed with the contents of message."""

        await ctx.message.delete()
        if error := self.check_message(message, ctx.author):
            return await ctx.send(error, delete_after=10)
        mention_author = any(ctx.message.mentions)
        ref_author = ref_author if check_staff(ctx.bot, 'Helper', ctx.author.id) else True
        embed, file = await self.create_ref(message, ctx.author, ref_text, ref_image, ref_author)

        if embed is None:
            return await ctx.send("No information to reference!", delete_after=10)

        await ctx.send(file=file, embed=embed, reference=ctx.message.reference, mention_author=mention_author)

    @reference_message.error
    async def reference_handler(self, ctx: GuildContext, error):
        if isinstance(error, (commands.ChannelNotFound, commands.MessageNotFound, commands.GuildNotFound)):
            await ctx.send(f"{ctx.author.mention} Message not found!", delete_after=10)
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(f"You can't use {ctx.command.name}.", delete_after=10)
        else:
            await ctx.send(error, delete_after=10)

    @check_if_user_can_sr()
    @app_commands.guild_only
    @app_commands.command(name='reference')
    async def reference_message_app(self, interaction: discord.Interaction, message: Transform[discord.Message, HackMessageTransformer], ref_text: bool = True, ref_image: bool = True):
        """Creates an embed with the contents of message.

        Args:
            message: Message to reference.
            ref_text: Copy message content from the message.
            ref_image: Copy image attachment from the message.
        """

        assert isinstance(interaction.user, discord.Member)

        if error := self.check_message(message, interaction.user):
            return await interaction.response.send_message(error, ephemeral=True)
        embed, file = await self.create_ref(message, interaction.user, ref_text, ref_image, False)

        if embed is None:
            return await interaction.response.send_message("No information to reference!", ephemeral=True)

        await interaction.response.send_message(file=file or MISSING, embed=embed)

    @commands.dm_only()
    @commands.cooldown(rate=1, per=21600.0, type=commands.BucketType.member)
    @commands.command()
    async def nickme(self, ctx: KurisuContext, *, nickname: str):
        """Change your nickname. Nitro Booster and crc only. Works only in DMs. 6 Hours Cooldown."""
        member = self.bot.guild.get_member(ctx.author.id)

        if member is None:
            return await ctx.send("Somehow you aren't in the server.")

        if self.bot.roles['crc'] not in member.roles and not member.premium_since:
            await ctx.send("This command can only be used by Nitro Boosters and members of crc!")
            ctx.command.reset_cooldown(ctx)
        elif self.check_nickname(nickname):
            try:
                await member.edit(nick=nickname)
                await ctx.send(f"Your nickname is now `{nickname}`!")
            except discord.errors.Forbidden:
                await ctx.send("💢  I can't change your nickname! (Permission Error)")
        else:
            await ctx.send("The nickname doesn't comply with our nickname policy or it's too long!")
            ctx.command.reset_cooldown(ctx)

    @commands.dynamic_cooldown(KurisuCooldown(1, 300.0), commands.BucketType.member)
    @commands.hybrid_command()
    async def remindme(self, ctx: KurisuContext, remind_in: int = commands.parameter(converter=DateOrTimeToSecondsConverter), *, reminder: str):
        """Sends a reminder after a set time, just for you. Max reminder size is 800 characters.

        Args:
            remind_in: Time to remind you in can be in a #d#h#m#s format or a YYYY-MM-DD HH:MM:SS format.
            reminder: Contents of the reminders. Max 800 characters.
        """
        if remind_in < 30 or remind_in > 3.154e+7:
            return await ctx.send("You can't set a reminder for less than 30 seconds or for more than a year.")
        if len(reminder) > 800:
            return await ctx.send("The reminder is too big! (Longer than 800 characters)")
        timestamp = datetime.now(self.bot.tz)
        delta = timedelta(seconds=remind_in)
        reminder_time = timestamp + delta
        await self.extras.add_reminder(reminder_time, ctx.author, reminder)
        await ctx.send(f"I will send you a reminder on {format_dt(reminder_time, style='F')}.", ephemeral=True)

    @commands.command()
    async def listreminders(self, ctx: KurisuContext):
        """Lists pending reminders."""
        reminders = self.extras.reminders.get(ctx.author.id)
        if not reminders:
            return await ctx.send("You don't have any reminders scheduled.")
        color = gen_color(ctx.author.id)
        view = PaginatedEmbedView(paginator=RemindersPaginator(reminders, color), author=ctx.author)
        view.message = await ctx.send(embed=view.paginator.current(), view=view)

    @commands.command()
    async def unremindme(self, ctx: KurisuContext, number: int):
        """Removes a pending reminder."""
        reminders = self.extras.reminders.get(ctx.author.id)
        if not reminders:
            return await ctx.send("You don't have any reminders scheduled.")
        if len(reminders) < number or number < 1:
            return await ctx.send("Invalid reminder number.")
        reminder = reminders[number - 1]
        await self.extras.delete_reminder(reminder.id, reminder.author_id)
        await ctx.send(f"Deleted reminder {number} successfully!")

    @commands.group(invoke_without_command=True)
    async def tag(self, ctx: KurisuContext, tag_name: str = ""):
        """Command group for commands related to tags."""
        if tag_name:
            if tag := self.extras.tags.get(tag_name):
                await ctx.send(tag.content, reference=ctx.message.reference)
            elif tags_titles := self.bot.extras.search_tags(tag_name, limit=5):
                embed = discord.Embed(
                    description='\n'.join(f'{n}. {tag_title}' for n, tag_title in enumerate(tags_titles, start=1)),
                    color=gen_color(ctx.author.id))
                await ctx.send("Tag not found, similar tags:", embed=embed)
            else:
                await ctx.send("There is no tag with this name or with a similar name.")
        else:
            await ctx.send_help(ctx.command)

    @app_commands.autocomplete(tag_name=tag_autocomplete)
    @app_commands.command(name='tag')
    async def tag_app_command(self, interaction: discord.Interaction, tag_name: str):
        """Looks up a tag by name.

        Args:
            tag_name: Name of the tag.
        """

        if tag := self.extras.tags.get(tag_name):
            await interaction.response.send_message(tag.content)
        else:
            await interaction.response.send_message("This tag doesn't exist!", ephemeral=True)

    @is_staff('Helper')
    @tag.command(name='create')
    async def create_tag(self, ctx: KurisuContext, title: str, *, content: str):
        """Creates a tag. Max content size is 2000 characters. Helpers+ only."""
        if self.extras.tags.get(title):
            return await ctx.send("This tag already exists!")
        if title in self.banned_tag_names:
            return await ctx.send("You can't use this name for a tag!")
        if len(content) > 2000:
            return await ctx.send("A tag contents can't be bigger than 2000 characters.")
        res = await self.extras.add_tag(title=title, content=content, author=ctx.author.id)
        if res:
            await ctx.send("Tag created successfully")
        else:
            await ctx.send("Failed to create tag")

    @is_staff('Helper')
    @tag.command(name='add_alias')
    async def add_alias(self, ctx: KurisuContext, tag_name: str, *, alias: str):
        """Creates an alias for a tag. Helpers+ only."""
        if not (tag := self.extras.tags.get(tag_name)):
            return await ctx.send("This tag doesn't exists!")
        if self.extras.tags.get(alias):
            return await ctx.send("This alias is already in use!")
        if alias in self.banned_tag_names:
            return await ctx.send("You can't use this alias for a tag!")

        await self.extras.add_tag_alias(tag, alias)
        await ctx.send(f"Added alias `{alias}` to tag {tag.title}.")

    @is_staff('Helper')
    @tag.command(name='delete_alias')
    async def delete_alias(self, ctx: KurisuContext, alias: str):
        """Deletes an alias for a tag. Helpers+ only."""
        if not (tag := self.extras.tags.get(alias)):
            return await ctx.send("This alias doesn't exists!")
        if tag.title == alias:
            return await ctx.send("This name is not an alias.")

        await self.extras.delete_tag_alias(tag, alias)
        await ctx.send(f"Delete alias `{alias}` from tag {tag.title}.")

    @tag.command(name='search')
    async def search_tags(self, ctx: KurisuContext, query: str):
        """Search tags by title. Returns first 10 results."""
        if tags := self.extras.search_tags(query):
            embed = discord.Embed(description='\n'.join(f'{n}. {tag}' for n, tag in enumerate(tags, start=1)), color=gen_color(ctx.author.id))
            await ctx.send(embed=embed)
        else:
            await ctx.send("No tags found.")

    @tag.command(name='info')
    async def tag_info(self, ctx: KurisuContext, tag_name: str):
        """Displays information about a tag."""
        if tag := self.extras.tags.get(tag_name):
            embed = discord.Embed(title=f"Tag {tag_name}", color=gen_color(tag.id))
            embed.add_field(name="ID", value=str(tag.id), inline=False)
            if tag.aliases:
                embed.add_field(name="Aliases", value=", ".join(tag.aliases), inline=False)
            author = self.bot.guild.get_member(tag.author_id)
            embed.add_field(name="Author", value=author.mention if author else str(tag.author_id), inline=False)
            embed.add_field(name="Creation Date", value=format_dt(snowflake_time(tag.id)), inline=False)
            await ctx.send(embed=embed, reference=ctx.message.reference)
        elif tags_titles := self.bot.extras.search_tags(tag_name, limit=5):
            embed = discord.Embed(
                description='\n'.join(f'{n}. {tag_title}' for n, tag_title in enumerate(tags_titles, start=1)),
                color=gen_color(ctx.author.id))
            await ctx.send("Tag not found, similar tags:", embed=embed)
        else:
            await ctx.send("There is no tag with this name or with a similar name.")

    @tag.command(name='list')
    async def list_tags(self, ctx: KurisuContext):
        """Lists the title of all existent tags."""
        if self.extras.tags:
            colour = gen_color(ctx.author.id)
            view = PaginatedEmbedView(paginator=TagsPaginator(tags=list(self.extras.tags.keys()),
                                                              tags_per_page=10, colour=colour), author=ctx.author)
            view.message = await ctx.send(embed=view.paginator.current(), view=view)
        else:
            await ctx.send("There are no tags.")

    @is_staff('Helper')
    @tag.command(name='edit')
    async def edit_tag(self, ctx: KurisuContext, tag_name: str, *, content: str):
        """Edits a tag. Helpers+ only."""
        if not self.extras.tags.get(tag_name):
            return await ctx.send("This tag doesn't exists!")
        if len(content) > 2000:
            return await ctx.send("A tag contents can't be bigger than 2000 characters.")
        # if tag.author != ctx.author.id:
        #     if await check_staff_id('Helper', ctx.author.id):
        #         await crud.change_tag_ownership(tag_name, ctx.author.id)
        #     else:
        #         return await ctx.send("You can't edit a tag that isn't yours.")
        edited_tag = await self.extras.update_tag(title=tag_name, content=content)
        if edited_tag is not None:
            await ctx.send("Tag edited successfully.")
        else:
            await ctx.send("Failed to edit tag.")

    @is_staff('Helper')
    @tag.command(name='delete')
    async def delete_tag(self, ctx: KurisuContext, *, tag_name: str):
        """Deletes a tag. Helpers+ only."""
        if not self.extras.tags.get(tag_name):
            return await ctx.send("This tag doesn't exists!")
        # if tag.author != ctx.author.id and not (await check_staff_id('Helper', ctx.author.id)):
        #     return await ctx.send("You can't delete a tag that isn't yours.")
        await self.extras.delete_tag(tag_name)
        await ctx.send("Tag deleted successfully.")

    @is_staff_app('OP')
    @app_commands.guild_only
    @app_commands.command()
    async def simplevote(self,
                         interaction: discord.Interaction,
                         name: str,
                         description: str,
                         options: str = "Yes|No",
                         staff_only: bool = False):
        """Creates a simple vote, only who made the vote can stop it. OP+ only.

        Args:
            name: Name of the vote.
            description: Description of the vote.
            options: Options for the vote separated by | .
            staff_only: If only staff is allowed to vote.
        """
        options_parsed = options.split('|')
        view = SimpleVoteView(self.bot, interaction.user.id, options_parsed, interaction.id, start=discord.utils.utcnow(), staff_only=staff_only)
        embed = discord.Embed(title=name, description=description)
        await interaction.response.send_message(embed=embed, view=view)
        msg = await interaction.original_response()
        await self.extras.add_voteview(view_id=interaction.id, identifier='extras',
                                       author_id=interaction.user.id, options=options,
                                       start=datetime.now(self.bot.tz), message_id=msg.id, staff_only=staff_only)

    @is_staff('OP')
    @commands.guild_only()
    @commands.command()
    async def addemoji(self, ctx: GuildContext, name: str, emoji: discord.PartialEmoji | str, *roles: discord.Role):
        """Add an emoji to the server. OP+ only."""
        if isinstance(emoji, discord.PartialEmoji):
            emoji_bytes = await emoji.read()
        else:
            try:
                async with self.bot.session.get(emoji, timeout=45) as r:
                    if r.status == 200:
                        if r.headers["Content-Type"] in ('image/jpeg', 'image/png', 'image/gif'):
                            emoji_bytes = await r.read()
                        else:
                            return await ctx.send("Only `.jpeg`, `.png` and `.gif` images can used for emojis.")
                    else:
                        return await ctx.send("Failed to fetch image.")
            except aiohttp.InvalidURL:
                return await ctx.send("Invalid url.")
        try:
            guild_emoji = await ctx.guild.create_custom_emoji(name=name, image=emoji_bytes, roles=roles, reason="Probably nothing good.")
        except discord.HTTPException as e:
            return await ctx.send(e.text)
        await ctx.send(f"Added emoji {guild_emoji if guild_emoji.is_usable() else name} successfully!")

    @commands.guild_only()
    @commands.hybrid_command()
    async def servericon(self, ctx: GuildContext):
        """Sends embed with the server's icon."""
        if ctx.guild.icon is None:
            return await ctx.send("This server has no icon set.", ephemeral=True)
        embed = discord.Embed(title=f"{ctx.guild.name} Icon")
        embed.set_image(url=ctx.guild.icon.url)
        await ctx.send(embed=embed, ephemeral=True)

    @commands.guild_only()
    @commands.command(name='close', aliases=['solved'])
    async def close_thread(self, ctx: GuildContext):
        """Closes and locks a thread. Thread owner or staff only."""
        await ctx.message.delete()
        if not isinstance(ctx.channel, discord.Thread):
            return await ctx.send("You can only close threads.", delete_after=10)
        if ctx.channel.owner is not ctx.author and not check_staff(ctx.bot, 'Helper', ctx.author.id):
            return await ctx.send("Only the thread owner or staff can close a thread.", delete_after=10)
        await ctx.send("Thread has been marked as solved.")
        await ctx.channel.edit(archived=True, locked=True)


async def setup(bot):
    await bot.add_cog(Extras(bot))
