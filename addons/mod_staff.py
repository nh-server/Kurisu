import discord
import json
from discord.ext import commands
from sys import argv

class ModStaff:
    """
    Extra things.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    roles = ["HalfOP", "OP", "SuperOP", "Owner"]

    @commands.has_permissions(administrator=True)
    @commands.command(pass_context=True)
    async def addstaff(self, ctx, user, position):
        """Add user as staff. Owners only."""
        if position not in self.roles:
            await self.bot.say("💢 That's not a valid position.")
            return
        staff_role = discord.utils.get(ctx.message.server.roles, name="Staff")
        member = ctx.message.mentions[0]
        server = ctx.message.author.server
        with open("staff.json", "r") as f:
            staff = json.load(f)
        staff[member.id] = position
        with open("staff.json", "w") as f:
            json.dump(staff, f)
        # replace roles, so to not leave previous ones on by accident
        if position == "HalfOP":  # this role requires the use of sudo
            await self.bot.replace_roles(member, staff_role)
        else:
            await self.bot.replace_roles(member, staff_role, discord.utils.get(ctx.message.server.roles, name=position))
        await self.bot.say("{} is now on staff as {}. Welcome to the secret party room!".format(member.mention, position))

    @commands.has_permissions(administrator=True)
    @commands.command(pass_context=True)
    async def delstaff(self, ctx, user):
        """Remove user from staff. Owners only."""
        staff_role = discord.utils.get(ctx.message.server.roles, name="Staff")
        member = ctx.message.mentions[0]
        server = ctx.message.author.server
        await self.bot.say(member.name)
        with open("staff.json", "r") as f:
            staff = json.load(f)
        staff.pop(member.id, None)
        with open("staff.json", "w") as f:
            json.dump(staff, f)
        await self.bot.replace_roles(member)
        await self.bot.say("{} is no longer staff. Stop by some time!".format(member.mention))

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True)
    async def sudo(self, ctx):
        """Gain staff powers temporarily. Only needed by HalfOPs."""
        halfop_role = discord.utils.get(ctx.message.server.roles, name="HalfOP")
        author = ctx.message.author
        server = author.server
        with open("staff.json", "r") as f:
            staff = json.load(f)
        if author.id not in staff:
            await self.bot.say("You are not listed as staff, and can't use this. (this message should not appear)")
            return
        if staff[author.id] != "HalfOP":
            await self.bot.say("You are not HalfOP, therefore this command is not required.")
            return
        await self.bot.add_roles(author, halfop_role)
        await self.bot.say("{} is now using sudo. Welcome to the twilight zone!".format(author.mention))
        msg = "👮 **Sudo**: {} | {}#{}".format(author.mention, author.name, author.discriminator)
        await self.bot.send_message(discord.utils.get(server.channels, name="mod-logs"), msg)

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True)
    async def unsudo(self, ctx):
        """Remove temporary staff powers. Only needed by HalfOPs."""
        halfop_role = discord.utils.get(ctx.message.server.roles, name="HalfOP")
        author = ctx.message.author
        server = author.server
        with open("staff.json", "r") as f:
            staff = json.load(f)
        if author.id not in staff:
            await self.bot.say("You are not listed as staff, and can't use this. (this message should not appear)")
            return
        if staff[author.id] != "HalfOP":
            await self.bot.say("You are not HalfOP, therefore this command is not required.")
            return
        await self.bot.remove_roles(author, halfop_role)
        await self.bot.say("{} is no longer using sudo!".format(author.mention))
        msg = "🕵 **Unsudo**: {} | {}#{}".format(author.mention, author.name, author.discriminator)
        await self.bot.send_message(discord.utils.get(server.channels, name="mod-logs"), msg)

def setup(bot):
    bot.add_cog(ModStaff(bot))
