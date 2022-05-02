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

from discord import TextChannel, __version__ as discordpy_version
from disnake.ext.commands import Param
from discord.ext import commands
from typing import Union, TYPE_CHECKING
from utils import crud, utils
from utils.checks import is_staff, check_if_user_can_sr, check_staff_id
from utils.utils import gen_color, dtm_to_discord_timestamp

if TYPE_CHECKING:
    from kurisu import Kurisu

python_version = sys.version.split()[0]


class Extras(commands.Cog):
    """
    Extra things.
    """
    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.emoji = discord.PartialEmoji.from_str('🎲')
        self.nick_pattern = re.compile("^[a-z]{2,}.*$", re.RegexFlag.IGNORECASE)
        self.bot.loop.create_task(self.init())

    async def init(self):
        await self.bot.wait_until_all_ready()
        for view in await crud.get_vote_views('SimpleVoteView'):
            v = utils.SimpleVoteView(view.author_id, options=view.options.split('|'), custom_id=view.id, start=view.start)
            self.bot.add_view(v, message_id=view.message_id)
            v.message_id = view.message_id

    prune_key = "nokey"

    def check_nickname(self, nickname):
        if match := self.nick_pattern.fullmatch(nickname):
            return len(nickname) <= 32
        else:
            return match

    @commands.command(hidden=True)
    async def env(self, ctx: commands.Context):
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
    async def kurisu(self, ctx: commands.Context):
        """About Kurisu"""
        embed = discord.Embed(title="Kurisu", color=discord.Color.green())
        embed.set_author(name="Maintained by Nintendo Homebrew helpers and staff")
        embed.set_thumbnail(url="https://i.imgur.com/hjVY4Et.jpg")
        embed.url = "https://github.com/nh-server/Kurisu"
        embed.description = "Kurisu, the Nintendo Homebrew Discord bot!"
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def membercount(self, ctx: commands.Context):
        """Prints the member count of the server."""
        await ctx.send(f"{ctx.guild.name} has {ctx.guild.member_count:,} members!")

    @commands.command()
    async def uptime(self, ctx: commands.Context):
        """Print total uptime of the bot."""
        await ctx.send(f"Uptime: {datetime.datetime.now() - self.bot.startup}")

    @commands.guild_only()
    @is_staff("SuperOP")
    @commands.command(hidden=True, aliases=['copyrole', 'crp'])
    async def copyroleperms(self, ctx: commands.Context, role: discord.Role, src_channel: Union[discord.TextChannel, discord.VoiceChannel], des_channels: commands.Greedy[Union[discord.TextChannel, discord.VoiceChannel]]):
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
    async def copychannelperms(self, ctx: commands.Context, src_channel: Union[discord.TextChannel, discord.VoiceChannel], des_channels: commands.Greedy[Union[discord.TextChannel, discord.VoiceChannel]]):
        """Copy channel overwrites from a channel to channels"""
        if any(type(c) != type(src_channel) for c in des_channels):
            return await ctx.send("Voice channels and text channel permissions are incompatible!")
        overwrites = src_channel.overwrites
        for c in des_channels:
            await c.edit(overwrites=overwrites)
        await ctx.send("Changed permissions successfully!")

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command(hidden=True)
    async def userroles(self, ctx: commands.Context, u: discord.Member = None):
        """Gets user roles and their id. Staff only."""
        if not u:
            u = ctx.author
        msg = f"{u}'s Roles:\n\n"
        for role in u.roles:
            if role.is_default():
                continue
            msg += f"{role} = {role.id}\n"
        await ctx.author.send(msg)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command(hidden=True)
    async def serverroles(self, ctx: commands.Context, exp: str):
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
    async def embedtext(self, ctx: commands.Context, *, text):
        """Embed content."""
        await ctx.send(embed=discord.Embed(description=text))

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def estprune(self, ctx: commands.Context, days=30):
        """Estimate count of members that would be pruned based on the amount of days. Staff only."""
        if ctx.guild.member_count > 100000:
            return await ctx.send("The server has too many members, the command would fail!")
        if days > 30:
            await ctx.send("Maximum 30 days")
            return
        if days < 1:
            await ctx.send("Minimum 1 day")
            return

        msg = await ctx.send("I'm figuring this out!")
        async with ctx.channel.typing():
            count = await ctx.guild.estimate_pruned_members(days=days)
            await msg.edit(content=f"{count:,} members inactive for {days} day(s) would be kicked from {ctx.guild.name}!")

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def activecount(self, ctx: commands.Context, days=30):
        """Shows the number of members active in the past amount of days. Staff only."""
        if ctx.guild.member_count > 100000:
            return await ctx.send("The server has too many members, the command would fail!")
        if days > 30:
            await ctx.send("Maximum 30 days")
            return
        if days < 1:
            await ctx.send("Minimum 1 day")
            return
        msg = await ctx.send("I'm figuring this out!")
        async with ctx.channel.typing():
            count = await ctx.guild.estimate_pruned_members(days=days)
            if days == 1:
                await msg.edit(content=f"{ctx.guild.member_count - count:,} members were active today in {ctx.guild.name}!")
            else:
                await msg.edit(content=f"{ctx.guild.member_count - count:,} members were active in the past {days} days in {ctx.guild.name}!")

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def prune30(self, ctx: commands.Context, key=""):
        """Prune members that are inactive for 30 days. Staff only."""
        if self.bot.pruning > 0:
            await ctx.send("Pruning is already in progress.")
            return
        if key != self.prune_key:
            if key != "":
                await ctx.send("That's not the correct key.")
            self.prune_key = ''.join(random.sample(string.ascii_letters, 8))
            await ctx.send(
                f"Are you sure you want to prune members inactive for 30 days?\nTo see how many members get kicked, use `.estprune`.\nTo confirm the prune, use the command `.prune30 {self.prune_key}`.")
            return
        self.prune_key = ''.join(random.sample(string.ascii_letters, 8))
        await ctx.send("Starting pruning!")
        count = await ctx.guild.prune_members(days=30)
        self.bot.pruning = count
        await self.bot.channels['mods'].send(f"{count:,} are currently being kicked from {ctx.guild.name}!")
        msg = f"👢 **Prune**: {ctx.author.mention} pruned {count:,} members"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("HalfOP")
    @commands.command()
    async def disableleavelogs(self, ctx: commands.Context):
        """DEBUG COMMAND"""
        self.bot.pruning = True
        await ctx.send("disable")

    @is_staff("HalfOP")
    @commands.command()
    async def enableleavelogs(self, ctx: commands.Context):
        """DEBUG COMMAND"""
        self.bot.pruning = False
        await ctx.send("enable")

    @commands.command(name="32c3")
    async def _32c3(self, ctx: commands.Context):
        """Console Hacking 2015"""
        await ctx.send("https://www.youtube.com/watch?v=bZczf57HSag")

    @commands.command(name="33c3")
    async def _33c3(self, ctx: commands.Context):
        """Nintendo Hacking 2016"""
        await ctx.send("https://www.youtube.com/watch?v=8C5cn_Qj0G8")

    @commands.command(name="34c3")
    async def _34c3(self, ctx: commands.Context):
        """Console Security - Switch"""
        await ctx.send("https://www.youtube.com/watch?v=Ec4NgWRE8ik")

    @is_staff("Owner")
    @commands.guild_only()
    @commands.command(hidden=True)
    async def dumpchannel(self, ctx: commands.Context, channel: TextChannel, limit=100):
        """Dump 100 messages from a channel to a file."""
        await ctx.send(f"Dumping {limit} messages from {channel.mention}")
        os.makedirs(f"#{channel.name}-{channel.id}", exist_ok=True)
        async for message in channel.history(limit=limit):
            with open(f"#{channel.name}-{channel.id}/{message.id}.txt", "w") as f:
                f.write(message.content)
        await ctx.send("Done!")

    @commands.guild_only()
    @commands.command(hidden=True)
    async def togglechannel(self, ctx: commands.Context, channel_name: str):
        """Enable or disable access to specific channels."""
        await ctx.message.delete()
        author = ctx.author
        if ctx.channel != self.bot.channels['bot-cmds']:
            return await ctx.send(f"{ctx.author.mention}: .togglechannel can only be used in {self.bot.channels['bot-cmds'].mention}.", delete_after=10)

        if channel_name == "elsewhere":
            if self.bot.roles['#elsewhere'] in author.roles:
                await author.remove_roles(self.bot.roles['#elsewhere'])
                await utils.send_dm_message(author, "Access to #elsewhere removed.")
            elif self.bot.roles['No-elsewhere'] not in author.roles:
                await author.add_roles(self.bot.roles['#elsewhere'])
                await utils.send_dm_message(author, "Access to #elsewhere granted.")
            else:
                await utils.send_dm_message(author, "Your access to elsewhere is restricted, contact staff to remove it.")
        elif channel_name == "artswhere":
            if self.bot.roles['#art-discussion'] in author.roles:
                await author.remove_roles(self.bot.roles['#art-discussion'])
                await utils.send_dm_message(author, "Access to #art-discussion removed.")
            elif self.bot.roles['No-art'] not in author.roles:
                await author.add_roles(self.bot.roles['#art-discussion'])
                await utils.send_dm_message(author, "Access to #art-discussion granted.")
            else:
                await utils.send_dm_message(author, "Your access to #art-discussion is restricted, contact staff to remove it.")
        else:
            await utils.send_dm_message(author, f"{channel_name} is not a valid toggleable channel.")

    @commands.guild_only()
    @commands.slash_command(name="togglechannel")
    async def togglechannel_sc(self, inter: discord.CommandInteraction, channel_name: str = Param(description="Channel to toggle")):
        """Enable or disable access to specific channels."""

        author = inter.author

        if channel_name == "elsewhere":
            if self.bot.roles['#elsewhere'] in author.roles:
                await author.remove_roles(self.bot.roles['#elsewhere'])
                await inter.send("Access to #elsewhere removed.", ephemeral=True)
            elif self.bot.roles['No-elsewhere'] not in author.roles:
                await author.add_roles(self.bot.roles['#elsewhere'])
                await inter.send("Access to #elsewhere granted.", ephemeral=True)
            else:
                await inter.send("Your access to elsewhere is restricted, contact staff to remove it.", ephemeral=True)
        elif channel_name == "artswhere":
            if self.bot.roles['#art-discussion'] in author.roles:
                await author.remove_roles(self.bot.roles['#art-discussion'])
                await utils.send_dm_message(author, "Access to #art-discussion removed.", ephemeral=True)
            elif self.bot.roles['No-art'] not in author.roles:
                await author.add_roles(self.bot.roles['#art-discussion'])
                await inter.send("Access to #art-discussion granted.", ephemeral=True)
            else:
                await inter.send("Your access to #art-discussion is restricted, contact staff to remove it.", ephemeral=True)
        else:
            await inter.send(f"{channel_name} is not a valid toggleable channel.", ephemeral=True)

    @check_if_user_can_sr()
    @commands.guild_only()
    @commands.command(aliases=['ref'])
    async def reference(self, ctx: commands.Context, message: discord.Message, ref_text: bool = True, ref_image: bool = True, ref_author: bool = False):
        """Creates a embed with the contents of message. Trusted, Helpers, Staff, Retired Staff, Verified only."""
        await ctx.message.delete()
        msg_reference = ctx.message.reference or None
        mention_author = any(ctx.message.mentions)
        ref_author = ref_author if await check_staff_id('Helper', ctx.author.id) else True
        if isinstance(message.channel, discord.DMChannel):
            return await ctx.send("Message can't be from a DM.")
        # xnoeproofing™
        if not message.channel.permissions_for(ctx.author).read_messages:
            return await ctx.send("bad xnoe, bad", delete_after=10)

        embed = discord.Embed(colour=gen_color(message.author.id), timestamp=message.created_at)
        if ref_text and message.content:
            embed.description = message.content
        if ref_image and len(message.attachments) > 0 and message.attachments[0].height and message.attachments[0].content_type.startswith("image/"):
            file = await message.attachments[0].to_file()
            embed.set_image(file=file)
        if embed.description == discord.Embed.Empty and not embed.image.__dict__:
            return await ctx.send("No information to reference!", delete_after=10)
        embed.set_author(name=message.author, icon_url=message.author.display_avatar.url, url=message.jump_url)
        embed.set_footer(text=f"in {message.channel.name}{f'. Ref by {ctx.author}' if ref_author else ''}")
        await ctx.send(embed=embed, reference=msg_reference, mention_author=mention_author)

    @reference.error
    async def reference_handler(self, ctx: commands.Context, error):
        if isinstance(error, (commands.ChannelNotFound, commands.MessageNotFound, commands.GuildNotFound)):
            await ctx.send(f"{ctx.author.mention} Message not found!", delete_after=10)
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(f"You can't use {ctx.command.name}.", delete_after=10)
        else:
            await ctx.send(error, delete_after=10)

    @commands.dm_only()
    @commands.cooldown(rate=1, per=21600.0, type=commands.BucketType.member)
    @commands.command()
    async def nickme(self, ctx: commands.Context, *, nickname):
        """Change your nickname. Nitro Booster and crc only. Works only in DMs. 6 Hours Cooldown."""
        member = self.bot.guild.get_member(ctx.author.id)
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
    async def remindme(self, ctx: commands.Context, remind_in: utils.DateOrTimeConverter, *, reminder: str):
        """Sends a reminder after a set time, just for you. Max reminder size is 800 characters.\n\nTime format: #d#h#m#s."""
        if remind_in < 30 or remind_in > 3.154e+7:
            return await ctx.send("You can't set a reminder for less than 30 seconds or for more than a year.")
        if len(reminder) > 800:
            return await ctx.send("The reminder is too big! (Longer than 800 characters)")
        timestamp = datetime.datetime.now()
        delta = datetime.timedelta(seconds=remind_in)
        reminder_time = timestamp + delta
        await crud.add_reminder(reminder_time, ctx.author.id, reminder)
        await ctx.send(f"I will send you a reminder on {dtm_to_discord_timestamp(reminder_time, date_format='F')}.")

    @commands.command()
    async def listreminders(self, ctx: commands.Context):
        """Lists pending reminders."""
        reminders = await crud.get_user_reminders(ctx.author.id)
        if not reminders:
            return await ctx.send("You don't have any reminders scheduled.")
        embeds = []
        color = utils.gen_color(ctx.author.id)
        for n, reminder in enumerate(reminders, start=1):
            embed = discord.Embed(title=f"Reminder {n}", color=color)
            embed.add_field(name='Content', value=reminder.reminder, inline=False)
            embed.add_field(name='Set to', value=utils.dtm_to_discord_timestamp(reminder.date), inline=False)
            embeds.append(embed)
        view = utils.PaginatedEmbedView(embeds, author=ctx.author)
        view.message = await ctx.send(embed=embeds[0], view=view)

    @commands.command()
    async def unremindme(self, ctx: commands.Context, number: int):
        """Removes a pending reminder."""
        reminders = await crud.get_user_reminders(ctx.author.id)
        if not reminders:
            return await ctx.send("You don't have any reminders scheduled.")
        if len(reminders) < number or number < 1:
            return await ctx.send("Invalid reminder number.")
        await crud.remove_reminder(reminders[number - 1].id)
        await ctx.send(f"Deleted reminder {number} successfully!")

    @commands.group(invoke_without_command=True)
    async def tag(self, ctx: commands.Context, title: str = ""):
        """Command group for commands related to tags."""
        if title:
            if tag := await crud.get_tag(title):
                return await ctx.send(tag.content)
            else:
                await ctx.send("This tag doesn't exist!")
        else:
            await ctx.send_help(ctx.command)

    @is_staff('Helper')
    @tag.command()
    async def create(self, ctx: commands.Context, title: str, *, content: str):
        """Creates a tag. Max content size is 2000 characters. Helpers+ only."""
        if await crud.get_tag(title):
            return await ctx.send("This tag already exists!")
        if len(content) > 2000:
            return await ctx.send("The tag contents are too big! (Longer than 2000 characters)")
        await crud.create_tag(title=title, content=content, author=ctx.author.id)
        await ctx.send("Tag created successfully")

    @tag.command()
    async def search(self, ctx: commands.Context, query: str):
        """Search tags by title. Returns first 10 results."""
        if tags := await crud.search_tags(query):
            embed = discord.Embed(description='\n'.join(f'{n}. {tag.title}' for n, tag in enumerate(tags, start=1)), color=gen_color(ctx.author.id))
            await ctx.send(embed=embed)
        else:
            await ctx.send("No tags found.")

    @tag.command()
    async def list(self, ctx: commands.Context):
        """Lists the title of all existent tags."""
        if tags := await crud.get_tags():
            embeds = []
            n = 1
            color = gen_color(ctx.author.id)
            for x in [tags[i:i + 10] for i in range(0, len(tags), 10)]:
                embed = discord.Embed(description='\n'.join(f'{n}. {tag.title}' for n, tag in enumerate(x, start=n)), color=color)
                n += len(x)
                embeds.append(embed)
            view = utils.PaginatedEmbedView(embeds=embeds, author=ctx.author)
            view.message = await ctx.send(embed=view.embeds[0], view=view)
        else:
            await ctx.send("There are no tags.")

    @is_staff('Helper')
    @tag.command()
    async def delete(self, ctx: commands.Context, *, title: str):
        """Deletes a tag. Helpers+ only."""
        if not (await crud.get_tag(title)):
            return await ctx.send("This tag doesn't exists!")
        await crud.delete_tag(title=title)
        await ctx.send("Tag deleted successfully")

    @is_staff('OP')
    @commands.slash_command()
    async def simplevote(self,
                         interaction: discord.CommandInteraction,
                         name: str = Param(desc="Name of the vote"),
                         description: str = Param(desc="Description of the vote"),
                         options: str = Param(desc="Options for the vote separated by \'|\'", default="Yes|No")):
        """Creates a simple vote, only the who made the vote can stop it. OP+ only."""
        options_parsed = options.split('|')
        view = utils.SimpleVoteView(interaction.user.id, options_parsed, interaction.id, start=discord.utils.utcnow())
        embed = discord.Embed(title=name, description=description)
        await interaction.response.send_message(embed=embed, view=view)
        msg = await interaction.original_message()
        view.message_id = msg.id
        await crud.add_vote_view(view_id=interaction.id, identifier='extras', author_id=interaction.user.id, options=options, start=datetime.datetime.utcnow(), message_id=msg.id)

    @is_staff('OP')
    @commands.guild_only()
    @commands.command()
    async def addemoji(self, ctx: commands.Context, name: str, emoji: Union[str, discord.PartialEmoji], *roles: discord.Role):
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


def setup(bot):
    bot.add_cog(Extras(bot))
