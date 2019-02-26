import json
from discord.ext import commands
import addons.checks

class ModStaff:
    """
    Staff management commands.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    @addons.checks.is_staff("Owner")
    @commands.command(pass_context=True)
    async def addstaff(self, ctx, user, position):
        """Add user as staff. Owners only."""
        if position not in self.bot.staff_ranks:
            await self.bot.say("💢 That's not a valid position. You can use __{}__".format("__, __".join(self.bot.staff_ranks.keys())))
            return
        member = ctx.message.mentions[0]
        addons.checks.staff[member.id] = position
        with open("data/staff.json", "w") as f:
            json.dump(addons.checks.staff, f)
        # remove leftover staff roles
        await self.bot.remove_roles(member, *self.bot.staff_ranks.values())
        await self.bot.say(member.name)
        if position == "HalfOP":  # this role requires the use of sudo
            await self.bot.add_roles(member, self.bot.staff_role)
        else:
            await self.bot.add_roles(member, self.bot.staff_role, self.bot.staff_ranks[position])
        await self.bot.say("{} is now on staff as {}. Welcome to the secret party room!".format(member.mention, position))

    @addons.checks.is_staff("Owner")
    @commands.command(pass_context=True)
    async def delstaff(self, ctx, user):
        """Remove user from staff. Owners only."""
        member = ctx.message.mentions[0]
        await self.bot.say(member.name)
        addons.checks.staff.pop(member.id, None)
        with open("data/staff.json", "w") as f:
            json.dump(addons.checks.staff, f)
        await self.bot.remove_roles(member, self.bot.staff_role, *self.bot.staff_ranks.values())
        await self.bot.say("{} is no longer staff. Stop by some time!".format(member.mention))

    @addons.checks.is_staff("HalfOP")
    @commands.command(pass_context=True)
    async def sudo(self, ctx):
        """Gain staff powers temporarily. Only needed by HalfOPs."""
        author = ctx.message.author
        staff = addons.checks.staff
        if author.id not in staff:
            await self.bot.say("You are not listed as staff, and can't use this. (this message should not appear)")
            return
        if staff[author.id] != "HalfOP":
            await self.bot.say("You are not HalfOP, therefore this command is not required.")
            return
        await self.bot.add_roles(author, self.bot.halfop_role)
        await self.bot.say("{} is now using sudo. Welcome to the twilight zone!".format(author.mention))
        msg = "👮 **Sudo**: {} | {}#{}".format(author.mention, author.name, author.discriminator)
        await self.bot.send_message(self.bot.modlogs_channel, msg)

    @addons.checks.is_staff("HalfOP")
    @commands.command(pass_context=True)
    async def unsudo(self, ctx):
        """Remove temporary staff powers. Only needed by HalfOPs."""
        author = ctx.message.author
        staff = addons.checks.staff
        if author.id not in staff:
            await self.bot.say("You are not listed as staff, and can't use this. (this message should not appear)")
            return
        if staff[author.id] != "HalfOP":
            await self.bot.say("You are not HalfOP, therefore this command is not required.")
            return
        await self.bot.remove_roles(author, self.bot.halfop_role)
        await self.bot.say("{} is no longer using sudo!".format(author.mention))
        msg = "🕵 **Unsudo**: {} | {}#{}".format(author.mention, author.name, author.discriminator)
        await self.bot.send_message(self.bot.modlogs_channel, msg)

def setup(bot):
    bot.add_cog(ModStaff(bot))
