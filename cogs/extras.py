import datetime
import disnake
import inspect
import os
import re
import sys

from disnake import TextChannel, __version__ as disnake_version
from disnake.ext import commands
from disnake.ext.commands import Param
from typing import Union, Literal
from utils.checks import is_staff
from utils import crud
from utils.utils import parse_time, gen_color

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

    @commands.slash_command()
    async def extras(self, inter):
        pass

    @extras.sub_command()
    async def env(self, inter):
        msg = f'''
        Python {python_version}
        disnake.py {disnake_version}
        Is Docker: {bool(self.bot.IS_DOCKER)}
        Commit: {self.bot.commit}
        Branch: {self.bot.branch}
        '''
        await inter.response.send_message(inspect.cleandoc(msg))

    @extras.sub_command()
    async def about(self, inter):
        """About Kurisu"""
        embed = disnake.Embed(title="Kurisu", color=disnake.Color.green())
        embed.set_author(name="Maintained by Nintendo Homebrew helpers and staff")
        embed.set_thumbnail(url="http://i.imgur.com/hjVY4Et.jpg")
        embed.url = "https://github.com/nh-server/Kurisu"
        embed.description = "Kurisu, the Nintendo Homebrew Discord bot!"
        await inter.response.send_message(embed=embed)

    @commands.guild_only()
    @extras.sub_command()
    async def membercount(self, inter):
        """Prints the member count of the server."""
        await inter.response.send_message(f"{inter.guild.name} has {inter.guild.member_count:,} members!")

    @extras.sub_command()
    async def uptime(self, inter):
        """Print total uptime of the bot."""
        await inter.response.send_message(f"Uptime: {datetime.datetime.now() - self.bot.startup}")

    @commands.slash_command()
    async def permissions(self, inter):
        pass

    @commands.guild_only()
    @is_staff("SuperOP")
    @permissions.sub_command()
    async def copyrolepermissions(
            self, inter,
            role: disnake.Role = Param(desc="Discord Role"),
            src_channel: Union[disnake.TextChannel, disnake.VoiceChannel] = Param(desc="Discord channel to copy role perms from"),
            des_channel: Union[disnake.TextChannel, disnake.VoiceChannel] = Param(desc="Discord channel to copy role perms to")):
        """Copy role overwrites from a channel to channels"""
        if des_channel != type(src_channel):
            return await inter.response.send_message("Voice channels and text channel permissions are incompatible!")
        role_overwrites = src_channel.overwrites_for(role)
        await des_channel.set_permissions(role, overwrite=role_overwrites)
        await inter.response.send_message("Changed permissions successfully!")

    @commands.guild_only()
    @is_staff("SuperOP")
    @permissions.sub_command()
    async def copychannelpermissions(
            self, inter,
            src_channel: Union[disnake.TextChannel, disnake.VoiceChannel] = Param(desc="Discord channel to copy perms from"),
            des_channel: Union[disnake.TextChannel, disnake.VoiceChannel] = Param(desc="Discord channels to copy perms to")):
        """Copy channel overwrites from a channel to channels"""
        if type(des_channel) != type(src_channel):
            return await inter.response.send_message("Voice channels and text channel permissions are incompatible!")
        overwrites = src_channel.overwrites
        await des_channel.edit(overwrites=overwrites)
        await inter.response.send_message("Changed permissions successfully!")

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.user_command(name="Get user roles")
    async def userroles(self, inter):
        """Gets user roles and their id. Staff only."""
        u = inter.target
        if not u:
            u = inter.author
        msg = f"{u}'s Roles:\n\n"
        for role in u.roles:
            if role.is_default():
                continue
            msg += f"{role} = {role.id}\n"
        await inter.response.send_message(msg, ephemeral=True)

    @is_staff("OP")
    @extras.sub_command()
    async def embedtext(self, inter, text: str = Param("Text to embed")):
        """Embed content."""
        await inter.response.send_message(embed=disnake.Embed(description=text))

    @is_staff("HalfOP")
    @extras.sub_command()
    async def disableleavelogs(self, inter):
        """DEBUG COMMAND"""
        self.bot.pruning = True
        await inter.response.send_message("disable")

    @is_staff("HalfOP")
    @extras.sub_command()
    async def enableleavelogs(self, inter):
        """DEBUG COMMAND"""
        self.bot.pruning = False
        await inter.response.send_message("enable")

    @extras.sub_command(name="32c3")
    async def _32c3(self, inter):
        """Console Hacking 2015"""
        await inter.response.send_message("https://www.youtube.com/watch?v=bZczf57HSag")

    @extras.sub_command(name="33c3")
    async def _33c3(self, inter):
        """Nintendo Hacking 2016"""
        await inter.response.send_message("https://www.youtube.com/watch?v=8C5cn_Qj0G8")

    @extras.sub_command(name="34c3")
    async def _34c3(self, inter):
        """Console Security - Switch"""
        await inter.response.send_message("https://www.youtube.com/watch?v=Ec4NgWRE8ik")

    @is_staff("Owner")
    @commands.guild_only()
    @extras.sub_command()
    async def dumpchannel(self, inter, channel: TextChannel, limit=100):
        """Dump 100 messages from a channel to a file."""
        await inter.response.send_message(f"Dumping {limit} messages from {channel.mention}")
        os.makedirs(f"#{channel.name}-{channel.id}", exist_ok=True)
        async for message in channel.history(limit=limit):
            with open(f"#{channel.name}-{channel.id}/{message.id}.txt", "w") as f:
                f.write(message.content)
        await inter.response.send_message("Done!")

    @commands.guild_only()
    @extras.sub_command()
    async def togglechannel(self, inter, channel_name: Literal['elsewhere', 'artswhere'] = Param(desc="Optional channel to get access to")):
        """Enable or disable access to specific channels."""
        author = inter.author
        try:
            if channel_name == "elsewhere":
                if self.bot.roles['#elsewhere'] in author.roles:
                    await author.remove_roles(self.bot.roles['#elsewhere'])
                    await inter.response.send_message("Access to #elsewhere removed.", ephemeral=True)
                elif self.bot.roles['No-elsewhere'] not in author.roles:
                    await author.add_roles(self.bot.roles['#elsewhere'])
                    await author.send("Access to #elsewhere granted.", ephemeral=True)
                else:
                    await author.send("Your access to elsewhere is restricted, contact staff to remove it.")
            elif channel_name == "artswhere":
                if self.bot.roles['#art-discussion'] in author.roles:
                    await author.remove_roles(self.bot.roles['#art-discussion'])
                    await inter.response.send_message("Access to #art-discussion removed.", ephemeral=True)
                elif self.bot.roles['No-art'] not in author.roles:
                    await author.add_roles(self.bot.roles['#art-discussion'])
                    await inter.response.send_message("Access to #art-discussion granted.", ephemeral=True)
                else:
                    await inter.response.send_message("Your access to #art-discussion is restricted, contact staff to remove it.", ephemeral=True)
        except disnake.errors.Forbidden:
            await inter.response.send_message("💢 I don't have permission to do this.", ephemeral=True)

    @commands.cooldown(rate=1, per=21600.0, type=commands.BucketType.member)
    @extras.sub_command()
    async def nickme(self, inter, nickname: str = Param(desc="New nickname")):
        """Change your nickname. Nitro Booster and crc only. Works only in DMs. 6 Hours Cooldown."""
        member = self.bot.guild.get_member(inter.author.id)
        if self.bot.roles['crc'] not in member.roles and not member.premium_since:
            await inter.response.send_message("This command can only be used by Nitro Boosters and members of crc!", ephemeral=True)
            inter.application_command.reset_cooldown(inter)
        elif self.check_nickname(nickname):
            try:
                await member.edit(nick=nickname)
                await inter.response.send_message(f"Your nickname is now `{nickname}`!", ephemeral=True)
            except disnake.errors.Forbidden:
                await inter.response.send_message("💢  I can't change your nickname! (Permission Error)", ephemeral=True)
        else:
            await inter.response.send_message("The nickname doesn't comply with our nickname policy or it's too long!", ephemeral=True)
            inter.application_command.reset_cooldown(inter)

    @commands.cooldown(rate=1, per=300.0, type=commands.BucketType.member)
    @extras.sub_command()
    async def remindme(self, inter, remind_in: str = Param(desc="When to remind you. Time format: #d#h#m#s"), reminder: str= Param(desc="What should i remind you of?")):
        """Sends a reminder after a set time, just for you"""
        if (seconds := parse_time(remind_in)) == -1:
            return await inter.response.send_message("💢 I don't understand your time format.", ephemeral=True)
        if seconds < 30 or seconds > 3.154e+7:
            return await inter.response.send_message("You can't set a reminder for less than 30 seconds or for more than a year.", ephemeral=True)
        if len(reminder) > 800:
            return await inter.response.send_message("The reminder is too big! (Longer than 800 characters)", ephemeral=True)
        timestamp = datetime.datetime.now()
        delta = datetime.timedelta(seconds=seconds)
        reminder_time = timestamp + delta
        await crud.add_reminder(reminder_time, inter.author.id, reminder)
        await inter.response.send_message("I will send you a reminder then.", ephemeral=True)

    @commands.slash_command()
    async def tag(self, inter, title: str = ""):
        """Command group for commands related to tags."""
        pass

    @is_staff('Helper')
    @tag.sub_command()
    async def create(self, inter, title: str = Param(desc="Title of the new tag"),content: str = Param(desc="Contents of the new tag")):
        """Creates a tag. Max content size is 2000 characters. Helpers+ only."""
        if await crud.get_tag(title):
            return await inter.response.send_message("This tag already exists!")
        if len(content) > 2000:
            return await inter.response.send_message("The tag contents are too big! (Longer than 2000 characters)")
        await crud.create_tag(title=title, content=content, author=inter.author.id)
        await inter.response.send_message("Tag created successfully")

    @tag.sub_command()
    async def search(self, inter, query: str = Param(desc="Tag title to search for")):
        """Search tags by title. Returns first 10 results."""
        if tags := await crud.search_tags(query):
            embed = disnake.Embed(description='\n'.join(f'{n}. {tag.title}' for n, tag in enumerate(tags, start=1)), color=gen_color(inter.author.id))
            await inter.response.send_message(embed=embed)
        else:
            await inter.response.send_message("No tags found.")

    @tag.sub_command()
    async def list(self, inter):
        """Lists the title of all existent tags."""
        if tags := await crud.get_tags():
            embed = disnake.Embed(description='\n'.join(f'{n}. {tag.title}' for n, tag in enumerate(tags, start=1)), color=gen_color(inter.author.id))
            await inter.response.send_message(embed=embed)
        else:
            await inter.response.send_message("There are no tags.")

    @is_staff('Helper')
    @tag.sub_command()
    async def delete(self, inter, title: str= Param(desc="Tag to delete")):
        """Deletes a tag. Helpers+ only."""
        if not (await crud.get_tag(title)):
            return await inter.response.send_message("This tag doesn't exists!")
        await crud.delete_tag(title=title)
        await inter.response.send_message("Tag deleted successfully")

    @tag.sub_command()
    async def show(self, inter, title: str = Param(desc="Tag to show")):
        if tag := await crud.get_tag(title):
            return await inter.response.send_message(tag.content)
        else:
            await inter.response.send_message("This tag doesn't exist!")


def setup(bot):
    bot.add_cog(Extras(bot))
