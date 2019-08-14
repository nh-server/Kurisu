import datetime
import discord
import os
import random
import re
import string

from cogs.checks import is_staff
from discord.ext import commands
from discord import TextChannel


class Extras(commands.Cog):
    """
    Extra things.
    """
    def __init__(self, bot):
        self.bot = bot
        print(f'Cog "{self.qualified_name}" loaded')

    prune_key = "nokey"

    @commands.command(aliases=['about'])
    async def kurisu(self, ctx):
        """About Kurisu"""
        embed = discord.Embed(title="Kurisu", color=discord.Color.green())
        embed.set_author(name="Started by 916253, maintained by ihaveahax")
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
    @commands.command(hidden=True)
    async def copyrole(self, ctx, role: discord.Role, src_channel: discord.TextChannel, des_channels: commands.Greedy[discord.TextChannel]):
        """Copy role permission from a channel to channels"""
        perms = src_channel.overwrites_for(role)
        for c in des_channels:
            await c.set_permissions(role, overwrite=perms)
        await ctx.send("Changed permissions successfully")

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
        if days > 30:
            await ctx.send("Maximum 30 days")
            return
        if days < 1:
            await ctx.send("Minimum 1 day")
            return

        msg = await ctx.send(f"I'm figuring this out!")
        async with ctx.channel.typing():
            count = await ctx.guild.estimate_pruned_members(days=days)
            await msg.edit(content=f"{count:,} members inactive for {days} day(s) would be kicked from {ctx.guild.name}!")

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def activecount(self, ctx, days=30):
        """Shows the number of members active in the past amount of days. Staff only."""
        if days > 30:
            await ctx.send("Maximum 30 days")
            return
        if days < 1:
            await ctx.send("Minimum 1 day")
            return
        msg = await ctx.send(f"I'm figuring this out!")
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

    @commands.command(hidden=True)
    async def togglechannel(self, ctx, channelname):
        """Enable or disable access to specific channels."""
        if isinstance(ctx.channel, discord.abc.GuildChannel):
            await ctx.message.delete()
            author = ctx.author
        else:
            author = self.bot.guild.get_member(ctx.author.id)
        try:
            if channelname == "elsewhere":
                if self.bot.roles['#elsewhere'] in author.roles:
                    await author.remove_roles(self.bot.roles['#elsewhere'])
                    await author.send("Access to #elsewhere removed.")
                elif self.bot.roles['no-elsewhere'] not in author.roles:
                    await author.add_roles(self.bot.roles['#elsewhere'])
                    await author.send("Access to #elsewhere granted.")
                else:
                    await author.send("Your access to elsewhere is restricted, contact staff to remove it.")
            elif channelname == "artswhere":
                if self.bot.roles['#art-discussion'] in author.roles:
                    await author.remove_roles(self.bot.roles['#art-discussion'])
                    await author.send("Access to #art-discussion removed.")
                elif self.bot.roles['no-art'] not in author.roles:
                    await author.add_roles(self.bot.roles['#art-discussion'])
                    await author.send("Access to #art-discussion granted.")
                else:
                    await author.send("Your access to #art-discussion is restricted, contact staff to remove it.")
            else:
                await author.send(f"{channelname} is not a valid toggleable channel.")
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")

    @commands.guild_only()
    @commands.command()
    async def rainbow(self, ctx):
        """Colorful"""
        emoji = '🌈'
        month = datetime.date.today().month
        if month == 6:
            member = ctx.author
            if member.nick and member.nick[-1] == emoji:
                await ctx.send("Your nickname already ends in a rainbow!")
            elif member.name[-1] == emoji and not member.nick:
                await ctx.send("Your name already ends in a rainbow!")
            else:
                try:
                    await ctx.author.edit(nick=f"{member.display_name} {emoji}")
                except discord.errors.Forbidden:
                    await ctx.send("💢  I can't change your nickname!")
                    return
                await ctx.send(f"Your nickname is now `{member.display_name}`!")
        else:
            await ctx.send("This month is not colorful enough!")

    @commands.guild_only()
    @commands.command()
    async def norainbow(self, ctx):
        """Tired of it."""
        emoji = '🌈'
        member = ctx.author
        pattern = re.compile(rf'{emoji}')
        if member.nick:
            iterator = re.finditer(pattern, member.nick)
            search = list(iterator)
            if search:
                res = search[-1]
                nick = member.display_name[0:res.start()] + member.display_name[res.end():]
                try:
                    await ctx.author.edit(nick=nick)
                except discord.errors.Forbidden:
                    await ctx.send("💢  I can't change your nickname!")
                    return
                await ctx.send(f"Your nickname is now `{nick}`!")
            else:
                await ctx.send("You don't have a rainbow!")
        elif bool(re.search(pattern, member.name)):
            await ctx.send("Your username is the one with the rainbow!")
        else:
            await ctx.send("You don't have a rainbow!")

    @commands.guild_only()
    @commands.command()
    async def spooky(self, ctx):
        """Spookybrew"""
        emoji = '🎃'
        month = datetime.date.today().month
        if month == 10:
            member = ctx.author
            if member.nick and member.nick[-1] == emoji:
                await ctx.send("Your nickname already ends in a pumpkin!")
            elif member.name[-1] == emoji and not member.nick:
                await ctx.send("Your name already ends in a pumpkin!")
            else:
                try:
                    await ctx.author.edit(nick=f"{member.display_name} {emoji}")
                except discord.errors.Forbidden:
                    await ctx.send("💢  I can't change your nickname!")
                    return
                await ctx.send(f"Your nickname is now `{member.display_name}`!")
        else:
            await ctx.send("This month is not spooky enough!")

    @commands.guild_only()
    @commands.command()
    async def nospooky(self, ctx):
        """Tired of it."""
        member = ctx.author
        pattern = re.compile(r'🎃')
        if member.nick:
            iterator = re.finditer(pattern, member.nick)
            search = list(iterator)
            if search:
                res = search[-1]
                nick = member.display_name[0:res.start()] + member.display_name[res.end():]
                try:
                    await ctx.author.edit(nick=nick)
                except discord.errors.Forbidden:
                    await ctx.send("💢  I can't change your nickname!")
                    return
            else:
                await ctx.send("You don't have a pumpkin!!")
        elif bool(re.search(pattern, member.name)):
            await ctx.send("Your username is the one with the pumpkin!")
        else:
            await ctx.send("You don't have a pumpkin!")

    @commands.guild_only()
    @commands.command()
    async def turkey(self, ctx):
        """Turkeybrew"""
        emoji = '🦃'
        month = datetime.date.today().month
        if month == 11:
            member = ctx.author
            if member.nick and member.nick[-1] == emoji:
                await ctx.send("Your nickname already ends in a turkey!")
            elif member.name[-1] == emoji and not member.nick:
                await ctx.send("Your name already ends in a turkey!")
            else:
                try:
                    await ctx.author.edit(nick=f"{member.display_name} {emoji}")
                except discord.errors.Forbidden:
                    await ctx.send("💢  I can't change your nickname!")
                    return
                await ctx.send(f"Your nickname is now `{member.display_name}`!")
        else:
            await ctx.send("This month is not thankful enough!")

    @commands.guild_only()
    @commands.command()
    async def noturkey(self, ctx):
        """Tired of it."""
        member = ctx.author
        pattern = re.compile(r'🦃')
        if member.nick:
            iterator = re.finditer(pattern, member.nick)
            search = list(iterator)
            if search:
                res = search[-1]
                nick = member.display_name[0:res.start()] + member.display_name[res.end():]
                try:
                    await ctx.author.edit(nick=nick)
                except discord.errors.Forbidden:
                    await ctx.send("💢  I can't change your nickname!")
                    return
                await ctx.send(f"Your nickname is now `{nick}`!")
            else:
                await ctx.send("You don't have a turkey!")
        elif bool(re.search(pattern, member.name)):
            await ctx.send("Your username is the one with the turkey!")
        else:
            await ctx.send("You don't have a turkey!")

    @commands.guild_only()
    @commands.command()
    async def xmasthing(self, ctx):
        """It's xmas time."""
        emoji = '🎄'
        month = datetime.date.today().month
        if month == 12:
            member = ctx.author
            if member.nick and member.nick[-1] == emoji:
                await ctx.send("Your nickname already ends in an xmas tree!")
            elif member.name[-1] == emoji and not member.nick:
                await ctx.send("Your name already ends in an xmas tree!")
            else:
                try:
                    await ctx.author.edit(nick=f"{member.display_name} {emoji}")
                except discord.errors.Forbidden:
                    await ctx.send("💢  I can't change your nickname!")
                    return
                await ctx.send(f"Your nickname is now `{member.display_name}`!")
        else:
            await ctx.send("This month is not christmassy enough!")

    @commands.guild_only()
    @commands.command()
    async def noxmasthing(self, ctx):
        """Tired of it."""
        member = ctx.author
        pattern = re.compile(r'🎄')
        if member.nick:
            iterator = re.finditer(pattern, member.nick)
            search = list(iterator)
            if search:
                res = search[-1]
                nick = member.display_name[0:res.start()] + member.display_name[res.end():]
                try:
                    await ctx.author.edit(nick=nick)
                except discord.errors.Forbidden:
                    await ctx.send("💢  I can't change your nickname!")
                    return
                await ctx.send(f"Your nickname is now `{nick}`!")
            else:
                await ctx.send("You don't have an xmas tree!")
        elif bool(re.search(pattern, member.name)):
            await ctx.send("Your username is the one with the xmas tree!")
        else:
            await ctx.send("You don't have an xmas tree!")

    @commands.guild_only()
    @commands.command()
    async def fireworks(self, ctx):
        """It's CurrentYear+1 time."""
        emoji = '🎆'
        month = datetime.date.today().month
        day = datetime.date.today().day
        if month == 12 and day == 31 or month == 1 and day == 1:
            member = ctx.author
            if member.nick and member.nick[-1] == emoji:
                await ctx.send("Your nickname already ends in fireworks!")
            elif member.name[-1] == emoji and not member.nick:
                await ctx.send("Your name already ends in fireworks!")
            else:
                try:
                    await ctx.author.edit(nick=f"{member.display_name} {emoji}")
                except discord.errors.Forbidden:
                    await ctx.send("💢  I can't change your nickname!")
                    return
                await ctx.send(f"Your nickname is now `{member.display_name}`!")
        else:
            await ctx.send("This day is not old/new enough!")

    @commands.guild_only()
    @commands.command()
    async def nofireworks(self, ctx):
        """Tired of it."""
        member = ctx.author
        pattern = re.compile(r'🎆')
        if member.nick:
            iterator = re.finditer(pattern, member.nick)
            search = list(iterator)
            if search:
                res = search[-1]
                nick = member.display_name[0:res.start()] + member.display_name[res.end():]
                try:
                    await ctx.author.edit(nick=nick)
                except discord.errors.Forbidden:
                    await ctx.send("💢  I can't change your nickname!")
                    return
                await ctx.send(f"Your nickname is now `{nick}`!")
            else:
                await ctx.send("You don't have fireworks!")
        elif bool(re.search(pattern, member.name)):
            await ctx.send("Your username is the one with the fireworks!")
        else:
            await ctx.send("You don't have fireworks!")

    @commands.guild_only()
    @commands.command()
    async def shamrock(self, ctx):
        """Get out your Jameson Irish Whiskey [PAID PROMOTION]."""
        emoji = '🍀'
        month = datetime.date.today().month
        day = datetime.date.today().day
        if month == 3 and day == 16 or month == 3 and day == 17:
            member = ctx.author
            if member.nick and member.nick[-1] == emoji:
                await ctx.send("Your nickname already ends in a shamrock!")
            elif member.name[-1] == emoji and not member.nick:
                await ctx.send("Your name already ends in fireworks!")
            else:
                try:
                    await ctx.author.edit(nick=f"{member.display_name} {emoji}")
                except discord.errors.Forbidden:
                    await ctx.send("💢  I can't change your nickname!")
                    return
                await ctx.send(f"Your nickname is now `{member.display_name}`!")
        else:
            await ctx.send("This day is not filled with enough Jameson Irish Whiskey [PAID PROMOTION]!")

    @commands.guild_only()
    @commands.command()
    async def noshamrock(self, ctx):
        """Tired of it."""
        member = ctx.message.author
        pattern = re.compile(r'🍀')
        if member.nick:
            iterator = re.finditer(pattern, member.nick)
            search = list(iterator)
            if search:
                res = search[-1]
                nick = member.display_name[0:res.start()] + member.display_name[res.end():]
                try:
                    await ctx.author.edit(nick=nick)
                except discord.errors.Forbidden:
                    await ctx.send("💢  I can't change your nickname!")
                    return
                await ctx.send(f"Your nickname is now `{nick}`!")
            else:
                await ctx.send("You don't have a shamrock!")
        elif bool(re.search(pattern, member.name)):
            await ctx.send("Your username is the one with the shamrock!")
        else:
            await ctx.send("You don't have a shamrock!")


def setup(bot):
    bot.add_cog(Extras(bot))
