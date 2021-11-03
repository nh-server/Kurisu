import disnake

from disnake.ext import commands
from disnake.ext.commands import Param

from utils import crud
from utils.checks import is_staff, staff_ranks


class ModStaff(commands.Cog):
    """
    Staff management commands.
    """

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, inter):
        if inter.guild is None:
            raise commands.NoPrivateMessage()
        return True

    StaffRoles = commands.option_enum(['Owner''SuperOP','OP','HalfOP'])

    @commands.slash_command()
    async def manage_staff(self, inter):
        pass
        
    @is_staff("Owner")
    @manage_staff.sub_command()
    async def addstaff(self, inter, member: disnake.Member = Param(desc="Member to add/promote to a staff role"), position: StaffRoles = Param(desc="Staff position to add member to")):
        """Add user as staff. Owners only."""
        await crud.add_staff(member.id, position)
        # remove leftover staff roles
        await member.remove_roles(*self.bot.staff_roles.values())
        if position == "HalfOP":  # this role requires the use of sudo
            await member.add_roles(self.bot.roles['Staff'])
        else:
            await member.add_roles(*(self.bot.roles['Staff'], self.bot.roles[position]))
        await inter.response.send_message(f"{member.mention} is now on staff as {position}. Welcome to the secret party room!")

    @is_staff("Owner")
    @manage_staff.sub_command()
    async def delstaff(self, inter, member: disnake.Member = Param(desc="Member to remove from staff")):
        """Remove user from staff. Owners only."""
        await inter.response.send_message(member.name)
        await crud.remove_staff(member.id)
        await member.remove_roles(*self.bot.staff_roles.values())
        await inter.response.send_message(f"{member.mention} is no longer staff. Stop by some time!")

    @is_staff("HalfOP")
    @manage_staff.sub_command()
    async def sudo(self, inter):
        """Gain staff powers temporarily. Only needed by HalfOPs."""
        author = inter.author
        staff = await crud.get_staff(author.id)
        if not staff:
            await inter.response.send_message("You are not listed as staff, and can't use this. (this message should not appear)", ephemeral=True)
            return
        if staff.position != "HalfOP":
            await inter.response.send_message("You are not HalfOP, therefore this command is not required.", ephemeral=True)
            return
        await author.add_roles(self.bot.roles['HalfOP'])
        await inter.response.send_message(f"{author.mention} is now using sudo. Welcome to the twilight zone!", ephemeral=True)
        msg = f"👮 **Sudo**: {author.mention} | {author}"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("HalfOP")
    @manage_staff.sub_command()
    async def unsudo(self, inter):
        """Remove temporary staff powers. Only needed by HalfOPs."""
        author = inter.author
        staff = await crud.get_staff(author.id)
        if not staff:
            await inter.response.send_message("You are not listed as staff, and can't use this. (this message should not appear)", ephemeral=True)
            return
        if staff.position != "HalfOP":
            await inter.response.send_message("You are not HalfOP, therefore this command is not required.", ephemeral=True)
            return
        await author.remove_roles(self.bot.roles['HalfOP'])
        await inter.response.send_message(f"{author.mention} is no longer using sudo!", ephemeral=True)
        msg = f"🕵 **Unsudo**: {author.mention} | {author}"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("OP")
    @manage_staff.sub_command()
    async def updatestaff(self, inter):
        """Updates the staff list based on staff member in the server."""
        removed = []
        for staffmember in await crud.get_staff_all():
            if inter.guild.get_member(staffmember.id) is None:
                await crud.remove_staff(staffmember.id)
                removed.append(await self.bot.fetch_user(staffmember.id))
        for helper in await crud.get_helpers():
            if inter.guild.get_member(helper.id) is None:
                await crud.remove_helper(helper.id)
                removed.append(await self.bot.fetch_user(helper.id))
        if not removed:
            await inter.response.send_message("Updated Staff list, no staff removed!")
        else:
            msg = f"Updated staff list. Removed {', '.join([x.name for x in removed])}."
            await inter.response.send_message(msg)
            modmsg = f"🛠 **Updated Staff list**: {inter.author.mention} updated the staff list.\n:pencil: __Users removed__: {', '.join([f'{x.id} | {x}'for x in removed])}"
            await self.bot.channels['mod-logs'].send(modmsg)

    @manage_staff.sub_command()
    async def liststaff(self, inter):
        """List staff members per rank."""
        staff_list = await crud.get_staff_all()
        ranks = dict.fromkeys(staff_ranks.keys())
        embed = disnake.Embed()
        for rank in ranks:
            ranks[rank] = []
            for staff in staff_list:
                if rank == staff.position:
                    ranks[rank].append(staff.id)
            if ranks[rank]:
                embed.add_field(
                    name=rank,
                    value="".join(f"<@{x}>\n" for x in ranks[rank]),
                    inline=False,
                )

        await inter.response.send_message("Here is a list of our staff members:", embed=embed)


def setup(bot):
    bot.add_cog(ModStaff(bot))
