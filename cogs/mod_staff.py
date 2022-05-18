from __future__ import annotations

import discord

from discord.ext import commands
from typing import TYPE_CHECKING
from utils import crud
from utils.checks import is_staff, staff_ranks

if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.utils import KurisuContext, GuildContext


class ModStaff(commands.Cog):
    """
    Staff management commands.
    """

    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.emoji = discord.PartialEmoji.from_str('🛠️')

    async def cog_check(self, ctx: KurisuContext):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        return True

    @is_staff("Owner")
    @commands.command()
    async def addstaff(self, ctx: GuildContext, member: discord.Member, position):
        """Add user as staff. Owners only."""
        if position not in self.bot.staff_roles:
            await ctx.send(f"💢 That's not a valid position. You can use __{'__, __'.join(self.bot.staff_roles.keys())}__")
            return
        await crud.add_staff(member.id, position)
        # remove leftover staff roles
        await member.remove_roles(*self.bot.staff_roles.values())
        if position == "HalfOP":  # this role requires the use of sudo
            await member.add_roles(self.bot.roles['Staff'])
        else:
            await member.add_roles(*(self.bot.roles['Staff'], self.bot.roles[position]))
        await ctx.send(f"{member.mention} is now on staff as {position}. Welcome to the secret party room!")

    @is_staff("Owner")
    @commands.command()
    async def delstaff(self, ctx: GuildContext, member: discord.Member):
        """Remove user from staff. Owners only."""
        await ctx.send(member.name)
        await crud.remove_staff(member.id)
        await member.remove_roles(*self.bot.staff_roles.values())
        await ctx.send(f"{member.mention} is no longer staff. Stop by some time!")

    @is_staff("HalfOP")
    @commands.command()
    async def sudo(self, ctx: GuildContext):
        """Gain staff powers temporarily. Only needed by HalfOPs."""
        author = ctx.author
        staff = await crud.get_staff_member(author.id)
        if not staff:
            await ctx.send("You are not listed as staff, and can't use this. (this message should not appear)")
            return
        if staff.position != "HalfOP":
            await ctx.send("You are not HalfOP, therefore this command is not required.")
            return
        await author.add_roles(self.bot.roles['HalfOP'])
        await ctx.send(f"{author.mention} is now using sudo. Welcome to the twilight zone!")
        msg = f"👮 **Sudo**: {author.mention} | {author}"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("HalfOP")
    @commands.guild_only()
    @commands.command()
    async def unsudo(self, ctx: GuildContext):
        """Remove temporary staff powers. Only needed by HalfOPs."""
        author = ctx.author
        staff = await crud.get_staff_member(author.id)
        if not staff:
            await ctx.send("You are not listed as staff, and can't use this. (this message should not appear)")
            return
        if staff.position != "HalfOP":
            await ctx.send("You are not HalfOP, therefore this command is not required.")
            return
        await author.remove_roles(self.bot.roles['HalfOP'])
        await ctx.send(f"{author.mention} is no longer using sudo!")
        msg = f"🕵 **Unsudo**: {author.mention} | {author}"
        await self.bot.channels['mod-logs'].send(msg)

    @is_staff("OP")
    @commands.guild_only()
    @commands.command(hidden=True)
    async def updatestaff(self, ctx: GuildContext):
        """Updates the staff list based on staff member in the server."""
        removed = []
        for staffmember in await crud.get_staff():
            if ctx.guild.get_member(staffmember.id) is None:
                await crud.remove_staff(staffmember.id)
                removed.append(await self.bot.fetch_user(staffmember.id))
        for helper in await crud.get_helpers():
            if ctx.guild.get_member(helper.id) is None:
                await crud.remove_helper(helper.id)
                removed.append(await self.bot.fetch_user(helper.id))
        if not removed:
            await ctx.send("Updated Staff list, no staff removed!")
        else:
            msg = f"Updated staff list. Removed {', '.join([x.name for x in removed])}."
            await ctx.send(msg)
            modmsg = f"🛠 **Updated Staff list**: {ctx.author.mention} updated the staff list.\n:pencil: __Users removed__: {', '.join([f'{x.id} | {x}'for x in removed])}"
            await self.bot.channels['mod-logs'].send(modmsg)

    @commands.command()
    async def liststaff(self, ctx: GuildContext):
        """List staff members per rank."""
        staff_list = await crud.get_staff()
        ranks: dict[str, list] = {}
        embed = discord.Embed()
        for rank in staff_ranks.keys():
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

        await ctx.send("Here is a list of our staff members:", embed=embed)


async def setup(bot):
    await bot.add_cog(ModStaff(bot))
