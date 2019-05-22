from discord.ext import commands
from cogs import converters
from cogs.checks import is_staff
from cogs.database import DatabaseCog


class ModStaff(DatabaseCog):
    """
    Staff management commands.
    """

    async def cog_check(self, ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        return True

    @is_staff("Owner")
    @commands.command()
    async def addstaff(self, ctx, member: converters.SafeMember, position):
        """Add user as staff. Owners only."""
        if position not in self.bot.staff_roles:
            await ctx.send(f"💢 That's not a valid position. You can use __{'__, __'.join(self.bot.staff_roles.keys())}__")
            return
        await self.add_staff(member.id, position)
        # remove leftover staff roles
        await member.remove_roles(*self.bot.staff_roles.values())
        if position == "HalfOP":  # this role requires the use of sudo
            await member.add_roles(self.bot.roles['Staff'])
        else:
            await member.add_roles(*(self.bot.roles['Staff'], self.bot.roles[position]))
        await ctx.send(f"{member.mention} is now on staff as {position}. Welcome to the secret party room!")

    @is_staff("Owner")
    @commands.command()
    async def delstaff(self, ctx, member: converters.SafeMember):
        """Remove user from staff. Owners only."""
        await ctx.send(member.name)
        await self.remove_staff(member.id)
        await member.remove_roles(*self.bot.staff_roles.values())
        await ctx.send(f"{member.mention} is no longer staff. Stop by some time!")

    @is_staff("HalfOP")
    @commands.command()
    async def sudo(self, ctx):
        """Gain staff powers temporarily. Only needed by HalfOPs."""
        author = ctx.author
        staff_role = await self.get_stafftrole(ctx.author.id)
        if not staff_role:
            await ctx.send("You are not listed as staff, and can't use this. (this message should not appear)")
            return
        if staff_role != "HalfOP":
            await ctx.send("You are not HalfOP, therefore this command is not required.")
            return
        await author.add_roles(self.bot.roles['HalfOP'])
        await ctx.send(f"{author.mention} is now using sudo. Welcome to the twilight zone!")
        msg = f"👮 **Sudo**: {author.mention} | {author}"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("HalfOP")
    @commands.command()
    async def unsudo(self, ctx):
        """Remove temporary staff powers. Only needed by HalfOPs."""
        author = ctx.author
        staff_role = await self.get_stafftrole(ctx.author.id)
        if not staff_role:
            await ctx.send("You are not listed as staff, and can't use this. (this message should not appear)")
            return
        if staff_role != "HalfOP":
            await ctx.send("You are not HalfOP, therefore this command is not required.")
            return
        await author.remove_roles(self.bot.roles['HalfOP'])
        await ctx.send(f"{author.mention} is no longer using sudo!")
        msg = f"🕵 **Unsudo**: {author.mention} | {author}"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("OP")
    @commands.guild_only()
    @commands.command(hidden=True)
    async def updatestaff(self, ctx):
        """Updates the staff list based on staff member in the server."""
        removed = []
        for staffmember in await self.get_staff():
            if ctx.guild.get_member(staffmember) is None:
                await self.remove_staff(staffmember)
                removed.append(await self.bot.fetch_user(staffmember))
        for helper in await self.get_helpers():
            if ctx.guild.get_member(helper) is None:
                await self.remove_helper(helper)
                removed.append(await self.bot.fetch_user(helper))
        if not removed:
            await ctx.send("Updated Staff list, no staff removed!")
        else:
            msg = f"Updated staff list. Removed {', '.join([x.name for x in removed])}."
            await ctx.send(msg)
            modmsg = f"🛠 **Updated Staff list**: {ctx.author.mention} updated the staff list.\n:pencil: __Users removed__: {', '.join([f'{x.id} | {x}'for x in removed])}"
            await self.bot.channels['mod-logs'].send(modmsg)


def setup(bot):
    bot.add_cog(ModStaff(bot))
