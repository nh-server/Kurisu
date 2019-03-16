import datetime
import discord
import os
import random
import re
import string
from discord.ext import commands
from discord import TextChannel
from addons.checks import is_staff


class Extras(commands.Cog):
    """
    Extra things.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

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

    @commands.command()
    async def membercount(self, ctx):
        """Prints the member count of the server."""
        await ctx.send("{} has {:,} members!".format(ctx.guild.name, ctx.guild.member_count))

    @commands.guild_only()
    @is_staff("SuperOP")
    @commands.command(hidden=True)
    async def copyrole(self, ctx, role: discord.Role, src_channel: discord.TextChannel, des_channels: commands.Greedy[discord.TextChannel]):
        """Copy role permission from a channel to channels"""
        perms = src_channel.overwrites_for(role)
        for c in des_channels:
            await c.set_permissions(role, overwrite=perms)
        await ctx.send("Changed permissions successfully")

    @commands.guild_only()
    @is_staff("HalfOP")
    @commands.command(hidden=True)
    async def userroles(self, ctx, u: discord.Member = None):
        """Gets user roles and their id. Staff only."""
        if not u:
            u = ctx.author
        msg = "{}'s Roles:\n\n".format(u)
        for role in u.roles:
            if role.is_default(): #Dont include everyone role
                continue
            msg += "{} = {}\n".format(role, role.id)
        await ctx.author.send(msg)

    @commands.guild_only()
    @is_staff("HalfOP")
    @commands.command(hidden=True)
    async def serverroles(self, ctx, exp: str):
        """Gets the server roles and their id by regex. Staff only."""
        msg = "Server roles matching `{}`:\n\n".format(exp)
        for role in ctx.guild.roles:
            if bool(re.search(exp, role.name, re.IGNORECASE)):
                msg += "{} = {}\n".format(role.name, role.id)
        await ctx.author.send(msg)

    @is_staff("OP")
    @commands.command(hidden=True)
    async def embedtext(self, ctx, *, text):
        """Embed content."""
        await ctx.send(embed=discord.Embed(description=text))

    @commands.guild_only()
    @is_staff("HalfOP")
    @commands.command()
    async def estprune(self, ctx, days=30):
        """Estimate count of members that would be pruned based on the amount of days. Staff only."""
        if days > 30:
            await ctx.send("Maximum 30 days")
            return
        if days < 1:
            await ctx.send("Minimum 1 day")
            return

        msg = await ctx.send("I'm figuring this out!".format(ctx.guild.name))
        with ctx.channel.typing:
            count = await ctx.guildestimate_pruned_members(days=days)
            await msg.edit(content="{:,} members inactive for {} day(s) would be kicked from {}!".format(count, days, ctx.guild.name))

    @commands.guild_only()
    @is_staff("HalfOP")
    @commands.command()
    async def activecount(self, ctx, days=30):
        """Shows the number of members active in the past amount of days. Staff only."""
        if days > 30:
            await ctx.send("Maximum 30 days")
            return
        if days < 1:
            await ctx.send("Minimum 1 day")
            return
        msg = await ctx.send("I'm figuring this out!".format(ctx.guild.name))
        with ctx.channel.typing:
            count = await ctx.guildestimate_pruned_members(days=days)
            if days == 1:
                await msg.edit(content="{:,} members were active today in {}!".format(ctx.guild.member_count-count, ctx.guild.name))
            else:
                await msg.edit(content="{:,} members were active in the past {} days in {}!".format(ctx.guild.member_count-count, days, ctx.guild.name))

    @commands.guild_only()
    @is_staff("HalfOP")
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
            await ctx.send("Are you sure you want to prune members inactive for 30 days?\nTo see how many members get kicked, use `.estprune`.\nTo confirm the prune, use the command `.prune30 {}`.".format(self.prune_key))
            return
        self.prune_key = ''.join(random.sample(string.ascii_letters, 8))
        await ctx.send("Starting pruning!")
        count = await ctx.guild.prune_members(days=30)
        self.bot.pruning = count
        await self.bot.mods_channel.send("{:,} are currently being kicked from {}!".format(count, ctx.guild.name))
        msg = "👢 **Prune**: {} pruned {:,} members".format(ctx.author.mention, count)
        await self.bot.modlogs_channel.send(msg)

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

    @commands.command(name="32c3", )
    async def _32c3(self, ctx):
        """Console Hacking 2015"""
        await ctx.send("https://www.youtube.com/watch?v=bZczf57HSag")

    @commands.command(name="33c3", )
    async def _33c3(self, ctx):
        """Nintendo Hacking 2016"""
        await ctx.send("https://www.youtube.com/watch?v=8C5cn_Qj0G8")

    @commands.command(name="34c3", )
    async def _34c3(self, ctx):
        """Console Security - Switch"""
        await ctx.send("https://www.youtube.com/watch?v=Ec4NgWRE8ik")

    if os.environ.get('KURISU_TRACEMALLOC', '0') == '1':
        @commands.guild_only()
        @is_staff("OP")
        @commands.command(hidden=True)
        async def tmsnap(self, ctx):
            os.makedirs('tmsnap', exist_ok=True)
            import tracemalloc
            snapshot = tracemalloc.take_snapshot()
            log_fn = 'tmsnap/' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.log'
            await ctx.send('Dumping to ' + log_fn)
            with open(log_fn, 'w', encoding='utf-8') as o:
                for s in snapshot.statistics('lineno'):
                    print(':'.join((str(s.traceback), str(s.size), str(s.count))), file=o)
            await ctx.send('Done!')

    @commands.guild_only()
    @is_staff("Owner")
    @commands.command(hidden=True)
    async def dumpchannel(self, ctx, channel: TextChannel, limit=100):
        """Dump 100 messages from a channel to a file."""
        await ctx.send("Dumping {} messages from {}".format(limit, channel.mention))
        os.makedirs("#{}-{}".format(channel.name, channel.id), exist_ok=True)
        async for message in channel.history(limit=limit):
            with open("#{}-{}/{}.txt".format(channel.name, channel.id, message.id), "w") as f:
                f.write(message.content)
        await ctx.send("Done!")

    @commands.command(hidden=True)
    async def togglechannel(self, ctx, channelname):
        """Enable or disable access to specific channels."""
        author = ctx.author
        await ctx.message.delete()
        try:
            if channelname == "elsewhere":
                if self.bot.elsewhere_role in author.roles:
                    await author.remove_roles(self.bot.elsewhere_role)
                    await author.send("Access to #elsewhere removed.")
                elif self.bot.noelsewhere_role not in author.roles:
                    await author.add_roles(author, self.bot.elsewhere_role)
                    await ctx.send("Access to #elsewhere granted.")
                else:
                    await author.send("Your access to elsewhere is restricted, contact staff to remove it.")
            else:
                await ctx.send_message("{} is not a valid toggleable channel.".format(channelname))
        except discord.errors.Forbidden:
            pass

    @commands.command()
    async def rainbow(self, ctx):
        """Colorful"""
        month = datetime.date.today().month
        if month == 6:
            member = ctx.author
            if member.nick and member.nick[-1] == "🌈":
                await ctx.send("Your nickname already ends in a rainbow!")
            elif member.name[-1] == "🌈" and not member.nick:
                await ctx.send("Your name already ends in a rainbow!")
            else:
                await self.bot.change_nickname(member, member.display_name + " 🌈")
                await ctx.send("Your nickname is now \"{} \"!".format(member.display_name))  
        else:
            await ctx.send("This month is not colorful enough!")
            
    @commands.command()
    async def norainbow(self, ctx):
        """Tired of it."""
        member = ctx.author
        pattern = re.compile(r'🌈')
        if member.nick:
            iterator = re.finditer(pattern, member.nick)
            search = list(iterator)
            if search:
                res = search[-1]
                nick = member.display_name[0:res.start()] + member.display_name[res.end():]
                await ctx.send("Your nickname is now \"{}\"!".format(nick))
                await self.bot.change_nickname(member, nick)
            else:
                await ctx.send("You don't have a rainbow!")
        elif bool(re.search(pattern, member.name)):
            await ctx.send("Your username is the one with the rainbow!")
        else:
            await ctx.send("You don't have a rainbow!")

    @commands.command()
    async def spooky(self, ctx):
        """Spookybrew"""
        month = datetime.date.today().month
        if month == 10:
            member = ctx.author
            if member.nick and member.nick[-1] == "🎃":
                await ctx.send("Your nickname already ends in a pumpkin!")
            elif member.name[-1] == "🎃" and not member.nick:
                await ctx.send("Your name already ends in a pumpkin!")
            else:
                await self.bot.change_nickname(member, member.display_name + " 🎃")
                await ctx.send("Your nickname is now \"{} \"!".format(member.display_name))  
        else:
            await ctx.send("This month is not spooky enough!")

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
                await ctx.send("Your nickname is now \"{}\"!".format(nick))
                await self.bot.change_nickname(member, nick)
            else:
                await ctx.send("You don't have a pumpkin!!")
        elif bool(re.search(pattern, member.name)):
            await ctx.send("Your username is the one with the pumpkin!")
        else:
            await ctx.send("You don't have a pumpkin!")
            
    @commands.command()
    async def turkey(self, ctx):
        """Turkeybrew"""
        month = datetime.date.today().month
        if month == 11:
            member = ctx.author
            if member.nick and member.nick[-1] == "🦃":
                await ctx.send("Your nickname already ends in a turkey!")
            elif member.name[-1] == "🦃" and not member.nick:
                await ctx.send("Your name already ends in a turkey!")
            else:
                await self.bot.change_nickname(member, member.display_name + " 🦃")
                await ctx.send("Your nickname is now \"{} \"!".format(member.display_name))  
        else:
            await ctx.send("This month is not thankful enough!")

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
                await ctx.send("Your nickname is now \"{}\"!".format(nick))
                await self.bot.change_nickname(member, nick)
            else:
                await ctx.send("You don't have a turkey!")
        elif bool(re.search(pattern, member.name)):
            await ctx.send("Your username is the one with the turkey!")
        else:
            await ctx.send("You don't have a turkey!")
            
    @commands.command()
    async def xmasthing(self, ctx):
        """It's xmas time."""
        month = datetime.date.today().month
        if month == 12:
            member = ctx.author
            if member.nick and member.nick[-1] == "🎄":
                await ctx.send("Your nickname already ends in an xmas tree!")
            elif member.name[-1] == "🎄" and not member.nick:
                await ctx.send("Your name already ends in an xmas tree!")
            else:
                await self.bot.change_nickname(member, member.display_name + " 🎄")
                await ctx.send("Your nickname is now \"{} \"!".format(member.display_name))  
        else:
            await ctx.send("This month is not christmassy enough!")
            
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
                await ctx.send("Your nickname is now \"{}\"!".format(nick))
                await self.bot.change_nickname(member, nick)
            else:
                await ctx.send("You don't have an xmas tree!")
        elif bool(re.search(pattern, member.name)):
            await ctx.send("Your username is the one with the xmas tree!")
        else:
            await ctx.send("You don't have an xmas tree!")

    @commands.command()
    async def fireworks(self, ctx):
        """It's CurrentYear+1 time."""
        month = datetime.date.today().month
        day = datetime.date.today().day
        if month == 12 and day == 31 or month == 1 and day == 1:
            member = ctx.author
            if member.nick and member.nick[-1] == "🎆":
                await ctx.send("Your nickname already ends in fireworks!")
            elif member.name[-1] == "🎆" and not member.nick:
                await ctx.send("Your name already ends in fireworks!")
            else:
                await self.bot.change_nickname(member, member.display_name + " 🎆")
                await ctx.send("Your nickname is now \"{} \"!".format(member.display_name))
        else:
            await ctx.send("This day is not old/new enough!")

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
                await ctx.send("Your nickname is now \"{}\"!".format(nick))
                await self.bot.change_nickname(member, nick)
            else:
                await ctx.send("You don't have fireworks!")
        elif bool(re.search(pattern, member.name)):
            await ctx.send("Your username is the one with the fireworks!")
        else:
            await ctx.send("You don't have fireworks!")

def setup(bot):
    bot.add_cog(Extras(bot))
