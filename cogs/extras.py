import datetime
import discord
import inspect
import os
import random
import re
import string
import sys

from discord import TextChannel, __version__ as discordpy_version
from discord.ext import commands
from typing import Union
from utils import crud
from utils.checks import is_staff
from utils.utils import parse_time, gen_color, dtm_to_discord_timestamp

python_version = sys.version.split()[0]


class Extras(commands.Cog):
    """
    Extra things.
    """
    def __init__(self, bot):
        self.bot = bot
        self.nick_pattern = re.compile("^[a-z]{2,}.*$", re.RegexFlag.IGNORECASE)

    prune_key = "nokey"

    def check_nickname(self, nickname):
        if match := self.nick_pattern.fullmatch(nickname):
            return len(nickname) <= 32
        else:
            return match

    @commands.command(hidden=True)
    async def env(self, ctx):
        msg = f'''
        Python {python_version}
        discord.py {discordpy_version}
        Is Docker: {bool(self.bot.IS_DOCKER)}
        Commit: {self.bot.commit}
        Branch: {self.bot.branch}
        '''
        await ctx.send(inspect.cleandoc(msg))

    @commands.command(aliases=['about'])
    async def kurisu(self, ctx):
        """About Kurisu"""
        embed = discord.Embed(title="Kurisu", color=discord.Color.green())
        embed.set_author(name="Maintained by Nintendo Homebrew helpers and staff")
        embed.set_thumbnail(url="http://i.imgur.com/hjVY4Et.jpg")
        embed.url = "https://github.com/nh-server/Kurisu"
        embed.description = "Kurisu, the Nintendo Homebrew Discord bot!"
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def membercount(self, ctx):
        """Prints the member count of the server."""
        await ctx.send(f"{ctx.guild.name} has {ctx.guild.member_count:,} members!")

    @commands.command()
    async def uptime(self, ctx):
        """Print total uptime of the bot."""
        await ctx.send(f"Uptime: {datetime.datetime.now() - self.bot.startup}")

    @commands.guild_only()
    @is_staff("SuperOP")
    @commands.command(hidden=True, aliases=['copyrole', 'crp'])
    async def copyroleperms(self, ctx, role: discord.Role, src_channel: Union[discord.TextChannel, discord.VoiceChannel], des_channels: commands.Greedy[Union[discord.TextChannel, discord.VoiceChannel]]):
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
    async def copychannelperms(self, ctx, src_channel: Union[discord.TextChannel, discord.VoiceChannel], des_channels: commands.Greedy[Union[discord.TextChannel, discord.VoiceChannel]]):
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
    async def userroles(self, ctx, u: discord.Member = None):
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
    async def serverroles(self, ctx, exp: str):
        """Gets the server roles and their id by regex. Staff only."""
        msg = f"Server roles matching `{exp}`:\n\n"
        for role in ctx.guild.roles:
            if bool(re.search(exp, role.name, re.IGNORECASE)):
                msg += f"{role.name} = {role.id}\n"
        await ctx.author.send(msg)

    @is_staff("OP")
    @commands.command(hidden=True)
    async def embedtext(self, ctx, *, text):
        """Embed content."""
        await ctx.send(embed=discord.Embed(description=text))

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def estprune(self, ctx, days=30):
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
    async def activecount(self, ctx, days=30):
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
    async def prune30(self, ctx, key=""):
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
    async def disableleavelogs(self, ctx):
        """DEBUG COMMAND"""
        self.bot.pruning = True
        await ctx.send("disable")

    @is_staff("HalfOP")
    @commands.command()
    async def enableleavelogs(self, ctx):
        """DEBUG COMMAND"""
        self.bot.pruning = False
        await ctx.send("enable")

    @commands.command(name="32c3")
    async def _32c3(self, ctx):
        """Console Hacking 2015"""
        await ctx.send("https://www.youtube.com/watch?v=bZczf57HSag")

    @commands.command(name="33c3")
    async def _33c3(self, ctx):
        """Nintendo Hacking 2016"""
        await ctx.send("https://www.youtube.com/watch?v=8C5cn_Qj0G8")

    @commands.command(name="34c3")
    async def _34c3(self, ctx):
        """Console Security - Switch"""
        await ctx.send("https://www.youtube.com/watch?v=Ec4NgWRE8ik")

    @is_staff("Owner")
    @commands.guild_only()
    @commands.command(hidden=True)
    async def dumpchannel(self, ctx, channel: TextChannel, limit=100):
        """Dump 100 messages from a channel to a file."""
        await ctx.send(f"Dumping {limit} messages from {channel.mention}")
        os.makedirs(f"#{channel.name}-{channel.id}", exist_ok=True)
        async for message in channel.history(limit=limit):
            with open(f"#{channel.name}-{channel.id}/{message.id}.txt", "w") as f:
                f.write(message.content)
        await ctx.send("Done!")

    @commands.guild_only()
    @commands.command(hidden=True)
    async def togglechannel(self, ctx, channelname):
        """Enable or disable access to specific channels."""
        await ctx.message.delete()
        author = ctx.author
        if ctx.channel != self.bot.channels['bot-cmds']:
            return await ctx.send(f"{ctx.author.mention}: .togglechannel can only be used in {self.bot.channels['bot-cmds'].mention}.", delete_after=10)
        try:
            if channelname == "elsewhere":
                if self.bot.roles['#elsewhere'] in author.roles:
                    await author.remove_roles(self.bot.roles['#elsewhere'])
                    await author.send("Access to #elsewhere removed.")
                elif self.bot.roles['No-elsewhere'] not in author.roles:
                    await author.add_roles(self.bot.roles['#elsewhere'])
                    await author.send("Access to #elsewhere granted.")
                else:
                    await author.send("Your access to elsewhere is restricted, contact staff to remove it.")
            elif channelname == "artswhere":
                if self.bot.roles['#art-discussion'] in author.roles:
                    await author.remove_roles(self.bot.roles['#art-discussion'])
                    await author.send("Access to #art-discussion removed.")
                elif self.bot.roles['No-art'] not in author.roles:
                    await author.add_roles(self.bot.roles['#art-discussion'])
                    await author.send("Access to #art-discussion granted.")
                else:
                    await author.send("Your access to #art-discussion is restricted, contact staff to remove it.")
            else:
                await author.send(f"{channelname} is not a valid toggleable channel.")
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @commands.dm_only()
    @commands.cooldown(rate=1, per=21600.0, type=commands.BucketType.member)
    @commands.command()
    async def nickme(self, ctx, *, nickname):
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
    async def remindme(self, ctx, remind_in: str, *, reminder: str):
        """Sends a reminder after a set time, just for you. Max reminder size is 800 characters.\n\nTime format: #d#h#m#s."""
        if (seconds := parse_time(remind_in)) == -1:
            return await ctx.send("💢 I don't understand your time format.")
        if seconds < 30 or seconds > 3.154e+7:
            return await ctx.send("You can't set a reminder for less than 30 seconds or for more than a year.")
        if len(reminder) > 800:
            return await ctx.send("The reminder is too big! (Longer than 800 characters)")
        timestamp = datetime.datetime.now()
        delta = datetime.timedelta(seconds=seconds)
        reminder_time = timestamp + delta
        await crud.add_reminder(reminder_time, ctx.author.id, reminder)
        await ctx.send(f"I will send you a reminder on {dtm_to_discord_timestamp(reminder_time, format='F')}.")

    @commands.group(invoke_without_command=True)
    async def tag(self, ctx, title: str = ""):
        """Command group for commands related to tags."""
        if ctx.invoked_subcommand is None:
            if title:
                if tag := await crud.get_tag(title):
                    return await ctx.send(tag.content)
                else:
                    await ctx.send("This tag doesn't exist!")
            else:
                await ctx.send_help(ctx.command)

    @is_staff('Helper')
    @tag.command()
    async def create(self, ctx, title: str, *, content: str):
        """Creates a tag. Max content size is 2000 characters. Helpers+ only."""
        if await crud.get_tag(title):
            return await ctx.send("This tag already exists!")
        if len(content) > 2000:
            return await ctx.send("The tag contents are too big! (Longer than 2000 characters)")
        await crud.create_tag(title=title, content=content, author=ctx.author.id)
        await ctx.send("Tag created successfully")

    @tag.command()
    async def search(self, ctx, query: str):
        """Search tags by title. Returns first 10 results."""
        if tags := await crud.search_tags(query):
            embed = discord.Embed(description='\n'.join(f'{n}. {tag.title}' for n, tag in enumerate(tags, start=1)), color=gen_color(ctx.author.id))
            await ctx.send(embed=embed)
        else:
            await ctx.send("No tags found.")

    @tag.command()
    async def list(self, ctx):
        """Lists the title of all existent tags."""
        if tags := await crud.get_tags():
            embed = discord.Embed(description='\n'.join(f'{n}. {tag.title}' for n, tag in enumerate(tags, start=1)), color=gen_color(ctx.author.id))
            await ctx.send(embed=embed)
        else:
            await ctx.send("There are no tags.")

    @is_staff('Helper')
    @tag.command()
    async def delete(self, ctx, *, title: str):
        """Deletes a tag. Helpers+ only."""
        if not (await crud.get_tag(title)):
            return await ctx.send("This tag doesn't exists!")
        await crud.delete_tag(title=title)
        await ctx.send("Tag deleted successfully")


def setup(bot):
    bot.add_cog(Extras(bot))
