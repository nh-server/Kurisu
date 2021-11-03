import disnake

from disnake.ext import commands
from disnake.ext.commands import Param

from utils.checks import is_staff
from utils import crud


class HelperList(commands.Cog):
    """
    Management of active helpers.
    """

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, inter):
        if inter.guild is None:
            raise commands.NoPrivateMessage()
        return True

    HelperConsoles = commands.option_enum(["3DS", "WiiU", "Switch", "Legacy"])

    @commands.slash_command()
    async def manage_helpers(self, inter):
        pass
        
    @is_staff(role='Owner')
    @manage_helpers.sub_command()
    async def addhelper(self, inter, member: disnake.Member = Param(desc="Member to add as a Helper"), console: HelperConsoles = Param(desc="Console to add helper as")):
        """Add user as a helper. Owners only."""
        await crud.add_helper(member.id, 'Helper', console)
        await member.add_roles(self.bot.roles['Helpers'])
        await inter.response.send_message(f"{member.mention} is now a helper. Welcome to the party room!")

    @is_staff(role='Owner')
    @manage_helpers.sub_command()
    async def delhelper(self, inter, member: disnake.Member = Param(desc="Member to remove from helpers")):
        """Remove user from helpers. Owners only."""
        if not await crud.get_helper(member.id):
            return await inter.response.send_message("This user is not a helper!")
        await inter.response.send_message(member.name)
        await crud.remove_helper(member.id)
        await member.remove_roles(self.bot.roles['Helpers'])
        await inter.response.send_message(f"{member.mention} is no longer a helper. Stop by some time!")

    @manage_helpers.sub_command()
    async def helpon(self, inter):
        """Gain highlighted helping role. Only needed by Helpers."""
        author = inter.author
        helper = await crud.get_helper(author.id)
        if not helper or not helper.console:
            await inter.response.send_message("You are not listed as a helper, and can't use this.")
            return
        await author.add_roles(self.bot.helper_roles[helper.console])
        await inter.response.send_message(f"{author.mention} is now actively helping.")
        msg = f"🚑 **Elevated: +Help**: {author.mention} | {author}"
        await self.bot.channels['mod-logs'].send(msg)

    @manage_helpers.sub_command()
    async def helpoff(self, inter):
        """Remove highlighted helping role. Only needed by Helpers."""
        author = inter.author
        helper = await crud.get_helper(author.id)
        if not helper or not helper.console:
            await inter.response.send_message("You are not listed as a helper, and can't use this.")
            return
        await author.remove_roles(self.bot.helper_roles[helper.console])
        await inter.response.send_message(f"{author.mention} is no longer actively helping!")
        msg = f"👎🏻 **De-Elevated: -Help**: {author.mention} | {author}"
        await self.bot.channels['mod-logs'].send(msg)

    @manage_helpers.sub_command()
    async def listhelpers(self, inter):
        """List helpers per console."""
        helper_list = await crud.get_helpers()
        consoles = dict.fromkeys(self.bot.helper_roles.keys())
        embed = disnake.Embed()
        for console in consoles:
            consoles[console] = []
            for helper in helper_list:
                if console == helper.console:
                    consoles[console].append(helper.id)
            if consoles[console]:
                embed.add_field(
                    name=console,
                    value="".join(f"<@{x}>\n" for x in consoles[console]),
                    inline=False,
                )
        await inter.response.send_message("Here is a list of our helpers:", embed=embed)


def setup(bot):
    bot.add_cog(HelperList(bot))
