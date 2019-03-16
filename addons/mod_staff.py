import json
from discord.ext import commands
import addons.checks
from addons import converters


@commands.guild_only()
class ModStaff(commands.Cog):
    """
    Staff management commands.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    @addons.checks.is_staff("Owner")
    @commands.command(pass_context=True)
    async def addstaff(self, ctx, member: converters.SafeMember, position):
        """Add user as staff. Owners only."""
        if position not in self.bot.staff_ranks:
            await ctx.send("💢 That's not a valid position. You can use __{}__".format("__, __".join(self.bot.staff_ranks.keys())))
            return
        addons.checks.staff[str(member.id)] = position
        with open("data/staff.json", "w") as f:
            json.dump(addons.checks.staff, f)
        # remove leftover staff roles
        member.remove_roles(*self.bot.staff_ranks.values())
        if position == "HalfOP":  # this role requires the use of sudo
            await member.add_roles(self.bot.staff_role)
        else:
            await member.add_roles(self.bot.staff_role, self.bot.staff_ranks[position])
        await ctx.send("{} is now on staff as {}. Welcome to the secret party room!".format(member.mention, position))

    @addons.checks.is_staff("Owner")
    @commands.command()
    async def delstaff(self, ctx, member: converters.SafeMember):
        """Remove user from staff. Owners only."""
        await ctx.send(member.name)
        addons.checks.staff.pop(str(member.id), None)
        with open("data/staff.json", "w") as f:
            json.dump(addons.checks.staff, f)
        await member.remove_roles(self.bot.staff_role, *self.bot.staff_ranks.values())
        await ctx.send("{} is no longer staff. Stop by some time!".format(member.mention))

    @addons.checks.is_staff("HalfOP")
    @commands.command(pass_context=True)
    async def sudo(self, ctx):
        """Gain staff powers temporarily. Only needed by HalfOPs."""
        author = ctx.author
        staff = addons.checks.staff
        if str(author.id) not in staff:
            await ctx.send("You are not listed as staff, and can't use this. (this message should not appear)")
            return
        if staff[str(author.id)] != "HalfOP":
            await ctx.send("You are not HalfOP, therefore this command is not required.")
            return
        await author.add_roles(self.bot.halfop_role)
        await ctx.send("{} is now using sudo. Welcome to the twilight zone!".format(author.mention))
        msg = "👮 **Sudo**: {} | {}#{}".format(author.mention, author.name, author.discriminator)
        await self.bot.modlogs_channel.send(msg)

    @addons.checks.is_staff("HalfOP")
    @commands.command(pass_context=True)
    async def unsudo(self, ctx):
        """Remove temporary staff powers. Only needed by HalfOPs."""
        author = ctx.author
        staff = addons.checks.staff
        if str(author.id) not in staff:
            await ctx.send("You are not listed as staff, and can't use this. (this message should not appear)")
            return
        if staff[str(author.id)] != "HalfOP":
            await ctx.send("You are not HalfOP, therefore this command is not required.")
            return
        await author.remove_roles(self.bot.halfop_role)
        await ctx.send("{} is no longer using sudo!".format(author.mention))
        msg = "🕵 **Unsudo**: {} | {}#{}".format(author.mention, author.name, author.discriminator)
        await self.bot.modlogs_channel.send(msg)

def setup(bot):
    bot.add_cog(ModStaff(bot))
