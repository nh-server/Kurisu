import datetime
import discord
import os
import random
import re
import string
from discord.ext import commands
from addons.checks import is_staff

class Extras:
    """
    Extra things.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    prune_key = "nokey"

    @commands.command(aliases=['about'])
    async def kurisu(self):
        """About Kurisu"""
        embed = discord.Embed(title="Kurisu", color=discord.Color.green())
        embed.set_author(name="Started by 916253, maintained by ihaveahax")
        embed.set_thumbnail(url="http://i.imgur.com/hjVY4Et.jpg")
        embed.url = "https://github.com/nh-server/Kurisu"
        embed.description = "Kurisu, the Nintendo Homebrew Discord bot!"
        await self.bot.say("", embed=embed)

    @commands.command()
    async def membercount(self):
        """Prints the member count of the server."""
        await self.bot.say("{} has {:,} members!".format(self.bot.server.name, self.bot.server.member_count))

    @is_staff("SuperOP")
    @commands.command(pass_context=True, no_pm=True, hidden=True)
    async def copyrole(self, ctx, role: discord.Role, src_channel: discord.Channel, *, des_channels):
        """Copy role permission from a channel to channels"""
        perms = src_channel.overwrites_for(role)
        converter = commands.ChannelConverter
        for c in des_channels.split():
            try:
                ch = converter(ctx, c).convert()
            except commands.errors.BadArgument as e:
                await self.bot.say(e)
                continue
            await self.bot.edit_channel_permissions(ch, role, overwrite=perms)
        await self.bot.say("Changed permissions successfully")

    @is_staff("HalfOP")
    @commands.command(pass_context=True, hidden=True)
    async def userroles(self, ctx, u: discord.Member = None):
        """Gets user roles and their id. Staff only."""
        if not u:
            u = ctx.message.author
        msg = "{}'s Roles:\n\n".format(u)
        for role in u.roles:
            if role.is_everyone: #Dont include everyone role
                continue
            msg += "{} = {}\n".format(role, role.id)
        await self.bot.send_message(ctx.message.author, msg)

    @is_staff("HalfOP")
    @commands.command(pass_context=True, hidden=True)
    async def serverroles(self, ctx, exp: str):
        """Gets the server roles and their id by regex. Staff only."""
        msg = "Server roles matching `{}`:\n\n".format(exp)
        for role in ctx.message.server.roles:
            if bool(re.search(exp, role.name, re.IGNORECASE)):
                msg += "{} = {}\n".format(role.name, role.id)
        await self.bot.send_message(ctx.message.author, msg)

    @is_staff("OP")
    @commands.command(hidden=True)
    async def embedtext(self, *, text):
        """Embed content."""
        await self.bot.say(embed=discord.Embed(description=text))

    @is_staff("HalfOP")
    @commands.command()
    async def estprune(self, days=30):
        """Estimate count of members that would be pruned based on the amount of days. Staff only."""
        if days > 30:
            await self.bot.say("Maximum 30 days")
            return
        if days < 1:
            await self.bot.say("Minimum 1 day")
            return
        msg = await self.bot.say("I'm figuring this out!".format(self.bot.server.name))
        count = await self.bot.estimate_pruned_members(server=self.bot.server, days=days)
        await self.bot.edit_message(msg, "{:,} members inactive for {} day(s) would be kicked from {}!".format(count, days, self.bot.server.name))

    @is_staff("HalfOP")
    @commands.command()
    async def activecount(self, days=30):
        """Shows the number of members active in the past amount of days. Staff only."""
        if days > 30:
            await self.bot.say("Maximum 30 days")
            return
        if days < 1:
            await self.bot.say("Minimum 1 day")
            return
        msg = await self.bot.say("I'm figuring this out!".format(self.bot.server.name))
        count = await self.bot.estimate_pruned_members(server=self.bot.server, days=days)
        if days == 1:
            await self.bot.edit_message(msg, "{:,} members were active today in {}!".format(self.bot.server.member_count-count, self.bot.server.name))
        else:
            await self.bot.edit_message(msg, "{:,} members were active in the past {} days in {}!".format(self.bot.server.member_count-count, days, self.bot.server.name))


    @is_staff("HalfOP")
    @commands.command(pass_context=True)
    async def prune30(self, ctx, key=""):
        """Prune members that are inactive for 30 days. Staff only."""
        if self.bot.pruning > 0:
            await self.bot.say("Pruning is already in progress.")
            return
        if key != self.prune_key:
            if key != "":
                await self.bot.say("That's not the correct key.")
            self.prune_key = ''.join(random.sample(string.ascii_letters, 8))
            await self.bot.say("Are you sure you want to prune members inactive for 30 days?\nTo see how many members get kicked, use `.estprune`.\nTo confirm the prune, use the command `.prune30 {}`.".format(self.prune_key))
            return
        self.prune_key = ''.join(random.sample(string.ascii_letters, 8))
        await self.bot.say("Starting pruning!")
        count = await self.bot.prune_members(self.bot.server, days=30)
        self.bot.pruning = count
        await self.bot.send_message(self.bot.mods_channel, "{:,} are currently being kicked from {}!".format(count, self.bot.server.name))
        msg = "👢 **Prune**: {} pruned {:,} members".format(ctx.message.author.mention, count)
        await self.bot.send_message(self.bot.modlogs_channel, msg)

    @is_staff("HalfOP")
    @commands.command()
    async def disableleavelogs(self):
        """DEBUG COMMAND"""
        self.bot.pruning = True
        await self.bot.say("disable")

    @is_staff("HalfOP")
    @commands.command()
    async def enableleavelogs(self):
        """DEBUG COMMAND"""
        self.bot.pruning = False
        await self.bot.say("enable")

    @commands.command(name="32c3")
    async def _32c3(self):
        """Console Hacking 2015"""
        await self.bot.say("https://www.youtube.com/watch?v=bZczf57HSag")

    @commands.command(name="33c3")
    async def _33c3(self):
        """Nintendo Hacking 2016"""
        await self.bot.say("https://www.youtube.com/watch?v=8C5cn_Qj0G8")

    @commands.command(name="34c3")
    async def _34c3(self):
        """Console Security - Switch"""
        await self.bot.say("https://www.youtube.com/watch?v=Ec4NgWRE8ik")

    if os.environ.get('KURISU_TRACEMALLOC', '0') == '1':
        @is_staff("OP")
        @commands.command(hidden=True)
        async def tmsnap(self):
            os.makedirs('tmsnap', exist_ok=True)
            import tracemalloc
            snapshot = tracemalloc.take_snapshot()
            log_fn = 'tmsnap/' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.log'
            await self.bot.say('Dumping to ' + log_fn)
            with open(log_fn, 'w', encoding='utf-8') as o:
                for s in snapshot.statistics('lineno'):
                    print(':'.join((str(s.traceback), str(s.size), str(s.count))), file=o)
            await self.bot.say('Done!')

    @is_staff("Owner")
    @commands.command(pass_context=True, hidden=True)
    async def dumpchannel(self, ctx, channel_name, limit=100):
        """Dump 100 messages from a channel to a file."""
        channel = ctx.message.channel_mentions[0]
        await self.bot.say("Dumping {} messages from {}".format(limit, channel.mention))
        os.makedirs("#{}-{}".format(channel.name, channel.id), exist_ok=True)
        async for message in self.bot.logs_from(channel, limit=limit):
            with open("#{}-{}/{}.txt".format(channel.name, channel.id, message.id), "w") as f:
                f.write(message.content)
        await self.bot.say("Done!")

    @commands.command(pass_context=True, hidden=True)
    async def togglechannel(self, ctx, channelname):
        """Enable or disable access to specific channels."""
        author = ctx.message.author
        await self.bot.delete_message(ctx.message)
        if channelname == "elsewhere":
            if self.bot.elsewhere_role in author.roles:
                await self.bot.remove_roles(author, self.bot.elsewhere_role)
                await self.bot.send_message(author, "Access to #elsewhere removed.")
            else:
                await self.bot.add_roles(author, self.bot.elsewhere_role)
                await self.bot.send_message(author, "Access to #elsewhere granted.")
        else:
            await self.bot.send_message(author, "{} is not a valid toggleable channel.".format(channelname))
    
    @commands.command(pass_context=True)
    async def rainbow(self, ctx):
        """Colorful"""
        month = datetime.date.today().month
        if month == 6:
            member = ctx.message.author
            if member.nick and member.nick[-1] == "🌈":
                await self.bot.say("Your nickname already ends in a rainbow!")
            elif member.name[-1] == "🌈" and not member.nick:
                await self.bot.say("Your name already ends in a rainbow!")
            else:
                await self.bot.change_nickname(member, member.display_name + " 🌈")
                await self.bot.say("Your nickname is now \"{} \"!".format(member.display_name))  
        else:
            await self.bot.say("This month is not colorful enough!")
            
    @commands.command(pass_context=True)
    async def norainbow(self, ctx):
        """Tired of it."""
        member = ctx.message.author
        pattern = re.compile(r'🌈')
        if member.nick:
            iterator = re.finditer(pattern, member.nick)
            search = list(iterator)
            if search:
                res = search[-1]
                nick = member.display_name[0:res.start()] + member.display_name[res.end():]
                await self.bot.say("Your nickname is now \"{}\"!".format(nick))
                await self.bot.change_nickname(member, nick)
            else:
                await self.bot.say("You don't have a rainbow!")
        elif bool(re.search(pattern, member.name)):
            await self.bot.say("Your username is the one with the rainbow!")
        else:
            await self.bot.say("You don't have a rainbow!")

    @commands.command(pass_context=True)
    async def spooky(self, ctx):
        """Spookybrew"""
        month = datetime.date.today().month
        if month == 10:
            member = ctx.message.author
            if member.nick and member.nick[-1] == "🎃":
                await self.bot.say("Your nickname already ends in a pumpkin!")
            elif member.name[-1] == "🎃" and not member.nick:
                await self.bot.say("Your name already ends in a pumpkin!")
            else:
                await self.bot.change_nickname(member, member.display_name + " 🎃")
                await self.bot.say("Your nickname is now \"{} \"!".format(member.display_name))  
        else:
            await self.bot.say("This month is not spooky enough!")

    @commands.command(pass_context=True)
    async def nospooky(self, ctx):
        """Tired of it."""
        member = ctx.message.author
        pattern = re.compile(r'🎃')
        if member.nick:
            iterator = re.finditer(pattern, member.nick)
            search = list(iterator)
            if search:
                res = search[-1]
                nick = member.display_name[0:res.start()] + member.display_name[res.end():]
                await self.bot.say("Your nickname is now \"{}\"!".format(nick))
                await self.bot.change_nickname(member, nick)
            else:
                await self.bot.say("You don't have a pumpkin!!")
        elif bool(re.search(pattern, member.name)):
            await self.bot.say("Your username is the one with the pumpkin!")
        else:
            await self.bot.say("You don't have a pumpkin!")
            
    @commands.command(pass_context=True)
    async def turkey(self, ctx):
        """Turkeybrew"""
        month = datetime.date.today().month
        if month == 11:
            member = ctx.message.author
            if member.nick and member.nick[-1] == "🦃":
                await self.bot.say("Your nickname already ends in a turkey!")
            elif member.name[-1] == "🦃" and not member.nick:
                await self.bot.say("Your name already ends in a turkey!")
            else:
                await self.bot.change_nickname(member, member.display_name + " 🦃")
                await self.bot.say("Your nickname is now \"{} \"!".format(member.display_name))  
        else:
            await self.bot.say("This month is not thankful enough!")

    @commands.command(pass_context=True)
    async def noturkey(self, ctx):
        """Tired of it."""
        member = ctx.message.author
        pattern = re.compile(r'🦃')
        if member.nick:
            iterator = re.finditer(pattern, member.nick)
            search = list(iterator)
            if search:
                res = search[-1]
                nick = member.display_name[0:res.start()] + member.display_name[res.end():]
                await self.bot.say("Your nickname is now \"{}\"!".format(nick))
                await self.bot.change_nickname(member, nick)
            else:
                await self.bot.say("You don't have a turkey!")
        elif bool(re.search(pattern, member.name)):
            await self.bot.say("Your username is the one with the turkey!")
        else:
            await self.bot.say("You don't have a turkey!")
            
    @commands.command(pass_context=True)
    async def xmasthing(self, ctx):
        """It's xmas time."""
        month = datetime.date.today().month
        if month == 12:
            member = ctx.message.author
            if member.nick and member.nick[-1] == "🎄":
                await self.bot.say("Your nickname already ends in an xmas tree!")
            elif member.name[-1] == "🎄" and not member.nick:
                await self.bot.say("Your name already ends in an xmas tree!")
            else:
                await self.bot.change_nickname(member, member.display_name + " 🎄")
                await self.bot.say("Your nickname is now \"{} \"!".format(member.display_name))  
        else:
            await self.bot.say("This month is not christmassy enough!")
            
    @commands.command(pass_context=True)
    async def noxmasthing(self, ctx):
        """Tired of it."""
        member = ctx.message.author
        pattern = re.compile(r'🎄')
        if member.nick:
            iterator = re.finditer(pattern, member.nick)
            search = list(iterator)
            if search:
                res = search[-1]
                nick = member.display_name[0:res.start()] + member.display_name[res.end():]
                await self.bot.say("Your nickname is now \"{}\"!".format(nick))
                await self.bot.change_nickname(member, nick)
            else:
                await self.bot.say("You don't have an xmas tree!")
        elif bool(re.search(pattern, member.name)):
            await self.bot.say("Your username is the one with the xmas tree!")
        else:
            await self.bot.say("You don't have an xmas tree!")

    @commands.command(pass_context=True)
    async def fireworks(self, ctx):
        """It's CurrentYear+1 time."""
        month = datetime.date.today().month
        day = datetime.date.today().day
        if month == 12 and day == 31 or month == 1 and day == 1:
            member = ctx.message.author
            if member.nick and member.nick[-1] == "🎆":
                await self.bot.say("Your nickname already ends in fireworks!")
            elif member.name[-1] == "🎆" and not member.nick:
                await self.bot.say("Your name already ends in fireworks!")
            else:
                await self.bot.change_nickname(member, member.display_name + " 🎆")
                await self.bot.say("Your nickname is now \"{} \"!".format(member.display_name))
        else:
            await self.bot.say("This day is not old/new enough!")

    @commands.command(pass_context=True)
    async def nofireworks(self, ctx):
        """Tired of it."""
        member = ctx.message.author
        pattern = re.compile(r'🎆')
        if member.nick:
            iterator = re.finditer(pattern, member.nick)
            search = list(iterator)
            if search:
                res = search[-1]
                nick = member.display_name[0:res.start()] + member.display_name[res.end():]
                await self.bot.say("Your nickname is now \"{}\"!".format(nick))
                await self.bot.change_nickname(member, nick)
            else:
                await self.bot.say("You don't have fireworks!")
        elif bool(re.search(pattern, member.name)):
            await self.bot.say("Your username is the one with the fireworks!")
        else:
            await self.bot.say("You don't have fireworks!")

def setup(bot):
    bot.add_cog(Extras(bot))
