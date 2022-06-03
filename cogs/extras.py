from __future__ import annotations

import aiohttp
import datetime
import discord
import inspect
import os
import random
import re
import string
import sys

from discord import app_commands, TextChannel, __version__ as discordpy_version
from discord.ext import commands
from discord.utils import format_dt
from math import ceil
from typing import Union, Optional, TYPE_CHECKING
from utils import crud
from utils.checks import is_staff, check_if_user_can_sr, check_staff_id
from utils.converters import DateOrTimeToSecondsConverter
from utils.utils import gen_color, send_dm_message
from utils.views import BasePaginator, SimpleVoteView, PaginatedEmbedView

if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.models import Tag, RemindMeEntry
    from utils.context import KurisuContext, GuildContext

python_version = sys.version.split()[0]


class TagsPaginator(BasePaginator):

    def __init__(self, tags: list[Tag], tags_per_page: int = 10, colour: Optional[discord.Color] = None):
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

    def create_embed(self, tags: list[Tag]):
        embed = discord.Embed(color=self.colour)
        embed.title = "Tags list"
        embed.description = '\n'.join(f'{n+(self.tags_per_page * self.idx)}. {tag.title}' for n, tag in enumerate(tags, start=1))

        if self.n_pages > 1:
            embed.title += f" [{self.idx + 1}/{self.n_pages}]"
        return embed


class RemindersPaginator(BasePaginator):

    def __init__(self, reminders: list[RemindMeEntry], colour: discord.Color = None):
        super().__init__(n_pages=len(reminders))
        self.reminders = reminders
        self.colour = colour or discord.Colour.purple()

    def current(self):
        if embed := self.pages.get(self.idx):
            return embed
        else:
            embed = self.create_embed(reminder=self.reminders[self.idx])
            self.pages[self.idx] = embed
            return embed

    def create_embed(self, reminder: RemindMeEntry):
        embed = discord.Embed(color=self.colour)
        embed.title = f"Reminder {self.idx + 1}"
        embed.add_field(name='Content', value=reminder.reminder, inline=False)
        embed.add_field(name='Set to', value=format_dt(reminder.date), inline=False)

        if self.n_pages > 1:
            embed.title += f" [{self.idx + 1}/{self.n_pages}]"
        return embed


async def tag_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    cog = interaction.client.get_cog('Extras')  # type: ignore
    if current:
        # very crude search but does the job
        choices = []
        n = 0
        for tag_name in cog.tags.keys():
            if current in tag_name:
                choices.append(app_commands.Choice(name=tag_name, value=tag_name))
                n = n + 1
            if n == 25:
                break
        return choices
    else:
        return [app_commands.Choice(name=tag_title, value=tag_title) for tag_title in list(cog.tags.keys())[:25]]


class Extras(commands.Cog):
    """
    Extra things.
    """
    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.emoji = discord.PartialEmoji.from_str('🎲')
        self.banned_tag_names = []
        self.tags: dict[str, Tag] = {}
        self.nick_pattern = re.compile("^[a-z]{2,}.*$", re.RegexFlag.IGNORECASE)
        self.bot.loop.create_task(self.init())

    async def init(self):
        await self.bot.wait_until_all_ready()
        for view in await crud.get_vote_views('extras'):
            v = SimpleVoteView(view.author_id, options=view.options.split('|'), custom_id=view.id, start=view.start, staff_only=view.staff_only)
            self.bot.add_view(v, message_id=view.message_id)

        self.tags = {tag.title: tag for tag in await crud.get_tags()}

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
        embed.set_thumbnail(url="https://i.imgur.com/hjVY4Et.jpg")
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
        await ctx.send(f"Uptime: {datetime.datetime.now() - self.bot.startup}")

    @commands.guild_only()
    @is_staff("SuperOP")
    @commands.command(hidden=True, aliases=['copyrole', 'crp'])
    async def copyroleperms(self, ctx: GuildContext, role: discord.Role, src_channel: Union[discord.TextChannel, discord.VoiceChannel], des_channels: commands.Greedy[Union[discord.TextChannel, discord.VoiceChannel]]):
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
    async def copychannelperms(self, ctx: GuildContext, src_channel: Union[discord.TextChannel, discord.VoiceChannel], des_channels: commands.Greedy[Union[discord.TextChannel, discord.VoiceChannel]]):
        """Copy channel overwrites from a channel to channels"""
        if any(type(c) != type(src_channel) for c in des_channels):
            return await ctx.send("Voice channels and text channel permissions are incompatible!")
        overwrites = src_channel.overwrites
        for c in des_channels:
            await c.edit(overwrites=overwrites)  # type: ignore
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
    @app_commands.describe(channel_name="Channel to toggle")
    @commands.hybrid_command(hidden=True)
    async def togglechannel(self, ctx: GuildContext, channel_name: str):
        """Enable or disable access to specific channels."""

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

    @check_if_user_can_sr()
    @commands.guild_only()
    @commands.command(aliases=['ref'])
    async def reference(self, ctx: GuildContext, message: discord.Message, ref_text: bool = True, ref_image: bool = True, ref_author: bool = False):
        """Creates a embed with the contents of message. Trusted, Helpers, Staff, Retired Staff, Verified only."""
        await ctx.message.delete()
        msg_reference = ctx.message.reference or None
        mention_author = any(ctx.message.mentions)
        ref_author = ref_author if await check_staff_id('Helper', ctx.author.id) else True
        if isinstance(message.channel, discord.abc.PrivateChannel):
            return await ctx.send("Message can't be from a DM.")

        if not isinstance(message.channel, discord.abc.GuildChannel):
            return await ctx.send("Failed to fetch channel information.")

        # xnoeproofing™
        if not message.channel.permissions_for(ctx.author).read_messages:
            return await ctx.send("bad xnoe, bad", delete_after=10)

        embed = discord.Embed(colour=gen_color(message.author.id), timestamp=message.created_at)
        if ref_text and message.content:
            embed.description = message.content
        file = None
        if ref_image and len(message.attachments) > 0 and message.attachments[0].height and message.attachments[0].content_type and message.attachments[0].content_type.startswith("image/"):
            file = await message.attachments[0].to_file()
            embed.set_image(url=f"attachment://{file.filename}")
        if embed.description is None and embed.image is None:
            return await ctx.send("No information to reference!", delete_after=10)
        embed.set_author(name=message.author, icon_url=message.author.display_avatar.url, url=message.jump_url)
        embed.set_footer(text=f"in {message.channel.name}{f'. Ref by {ctx.author}' if ref_author else ''}")
        await ctx.send(file=file, embed=embed, reference=msg_reference, mention_author=mention_author)

    @reference.error
    async def reference_handler(self, ctx: GuildContext, error):
        if isinstance(error, (commands.ChannelNotFound, commands.MessageNotFound, commands.GuildNotFound)):
            await ctx.send(f"{ctx.author.mention} Message not found!", delete_after=10)
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(f"You can't use {ctx.command.name}.", delete_after=10)
        else:
            await ctx.send(error, delete_after=10)

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

    @commands.cooldown(rate=1, per=300.0, type=commands.BucketType.member)
    @commands.command()
    async def remindme(self, ctx: KurisuContext, remind_in: int = commands.parameter(converter=DateOrTimeToSecondsConverter), *, reminder: str):
        """Sends a reminder after a set time, just for you. Max reminder size is 800 characters.\n\nTime format: #d#h#m#s."""
        if remind_in < 30 or remind_in > 3.154e+7:
            return await ctx.send("You can't set a reminder for less than 30 seconds or for more than a year.")
        if len(reminder) > 800:
            return await ctx.send("The reminder is too big! (Longer than 800 characters)")
        timestamp = datetime.datetime.now()
        delta = datetime.timedelta(seconds=remind_in)
        reminder_time = timestamp + delta
        await crud.add_reminder(reminder_time, ctx.author.id, reminder)
        await ctx.send(f"I will send you a reminder on {format_dt(reminder_time, style='F')}.")

    @commands.command()
    async def listreminders(self, ctx: KurisuContext):
        """Lists pending reminders."""
        reminders = await crud.get_user_reminders(ctx.author.id)
        if not reminders:
            return await ctx.send("You don't have any reminders scheduled.")
        color = gen_color(ctx.author.id)
        view = PaginatedEmbedView(paginator=RemindersPaginator(reminders, color), author=ctx.author)
        view.message = await ctx.send(embed=view.paginator.current(), view=view)

    @commands.command()
    async def unremindme(self, ctx: KurisuContext, number: int):
        """Removes a pending reminder."""
        reminders = await crud.get_user_reminders(ctx.author.id)
        if not reminders:
            return await ctx.send("You don't have any reminders scheduled.")
        if len(reminders) < number or number < 1:
            return await ctx.send("Invalid reminder number.")
        await crud.remove_reminder(reminders[number - 1].id)
        await ctx.send(f"Deleted reminder {number} successfully!")

    @commands.group(invoke_without_command=True)
    async def tag(self, ctx: KurisuContext, tag_name: str = ""):
        """Command group for commands related to tags."""
        if tag_name:
            if tag := self.tags.get(tag_name):
                await ctx.send(tag.content, reference=ctx.message.reference)
            elif tags := await crud.search_tags(tag_name, limit=5):
                embed = discord.Embed(
                    description='\n'.join(f'{n}. {tag.title}' for n, tag in enumerate(tags, start=1)),
                    color=gen_color(ctx.author.id))
                await ctx.send("Tag not found, similar tags:", embed=embed)
            else:
                await ctx.send("There is no tag with this name or with a similar name.")
        else:
            await ctx.send_help(ctx.command)

    @app_commands.autocomplete(tag_name=tag_autocomplete)
    @app_commands.command(name='tag')
    async def tag_app_command(self, interaction: discord.Interaction, tag_name: str):
        """Looks up a tag by name"""
        if tag := self.tags.get(tag_name):
            await interaction.response.send_message(tag.content)
        else:
            await interaction.response.send_message("This tag doesn't exist!", ephemeral=True)

    @is_staff('Helper')
    @tag.command(name='create')
    async def create_tag(self, ctx: KurisuContext, title: str, *, content: str):
        """Creates a tag. Max content size is 2000 characters. Helpers+ only."""
        if self.tags.get(title):
            return await ctx.send("This tag already exists!")
        if title in self.banned_tag_names:
            return await ctx.send("You can't use this name for a tag!")
        if len(content) > 2000:
            return await ctx.send("A tag contents can't be bigger than 2000 characters.")
        tag = await crud.create_tag(title=title, content=content, author=ctx.author.id)
        self.tags[tag.title] = tag
        await ctx.send("Tag created successfully")

    @tag.command(name='search')
    async def search_tags(self, ctx: KurisuContext, query: str):
        """Search tags by title. Returns first 10 results."""
        if tags := await crud.search_tags(query):
            embed = discord.Embed(description='\n'.join(f'{n}. {tag.title}' for n, tag in enumerate(tags, start=1)), color=gen_color(ctx.author.id))
            await ctx.send(embed=embed)
        else:
            await ctx.send("No tags found.")

    @tag.command(name='list')
    async def list_tags(self, ctx: KurisuContext):
        """Lists the title of all existent tags."""
        if self.tags:
            colour = gen_color(ctx.author.id)
            view = PaginatedEmbedView(paginator=TagsPaginator(tags=list(self.tags.values()),
                                                              tags_per_page=10, colour=colour), author=ctx.author)
            view.message = await ctx.send(embed=view.paginator.current(), view=view)
        else:
            await ctx.send("There are no tags.")

    @is_staff('Helper')
    @tag.command(name='edit')
    async def edit_tag(self, ctx: KurisuContext, tag_name: str, *, content: str):
        """Edits a tag. Helpers+ only."""
        if not (await crud.get_tag(tag_name)):
            return await ctx.send("This tag doesn't exists!")
        if len(content) > 2000:
            return await ctx.send("A tag contents can't be bigger than 2000 characters.")
        # if tag.author != ctx.author.id:
        #     if await check_staff_id('Helper', ctx.author.id):
        #         await crud.change_tag_ownership(tag_name, ctx.author.id)
        #     else:
        #         return await ctx.send("You can't edit a tag that isn't yours.")
        edited_tag = await crud.edit_tag(title=tag_name, content=content)
        if edited_tag is not None:
            self.tags[edited_tag.title] = edited_tag
            await ctx.send("Tag edited successfully.")
        else:
            await ctx.send("Failed to edit tag.")

    @is_staff('Helper')
    @tag.command(name='delete')
    async def delete_tag(self, ctx: KurisuContext, *, tag_name: str):
        """Deletes a tag. Helpers+ only."""
        if not (await crud.get_tag(tag_name)):
            return await ctx.send("This tag doesn't exists!")
        # if tag.author != ctx.author.id and not (await check_staff_id('Helper', ctx.author.id)):
        #     return await ctx.send("You can't delete a tag that isn't yours.")
        await crud.delete_tag(title=tag_name)
        del self.tags[tag_name]
        await ctx.send("Tag deleted successfully.")

    @is_staff('OP')
    @app_commands.default_permissions(ban_members=True)
    @app_commands.describe(name="Name of the vote",
                           description="Description of the vote",
                           options="Options for the vote separated by \'|\'",
                           staff_only="If only staff is allowed to vote.")
    @app_commands.guild_only
    @app_commands.command()
    async def simplevote(self,
                         interaction: discord.Interaction,
                         name: str,
                         description: str,
                         options: str = "Yes|No",
                         staff_only: bool = False):
        """Creates a simple vote, only the who made the vote can stop it. OP+ only."""
        options_parsed = options.split('|')
        view = SimpleVoteView(interaction.user.id, options_parsed, interaction.id, start=discord.utils.utcnow(), staff_only=staff_only)
        embed = discord.Embed(title=name, description=description)
        await interaction.response.send_message(embed=embed, view=view)
        msg = await interaction.original_message()
        await crud.add_vote_view(view_id=interaction.id, identifier='extras',
                                 author_id=interaction.user.id, options=options,
                                 start=datetime.datetime.utcnow(), message_id=msg.id, staff_only=staff_only)

    @is_staff('OP')
    @commands.guild_only()
    @commands.command()
    async def addemoji(self, ctx: GuildContext, name: str, emoji: Union[str, discord.PartialEmoji], *roles: discord.Role):
        """Add a emoji to the server. OP+ only."""
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
        guild_emoji = await ctx.guild.create_custom_emoji(name=name, image=emoji_bytes, roles=roles, reason="Probably nothing good.")
        await ctx.send(f"Added emoji {guild_emoji if guild_emoji.is_usable() else name} successfully!")


async def setup(bot):
    await bot.add_cog(Extras(bot))
