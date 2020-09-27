import discord
from discord.ext import commands

from . import switch, wiiu, ctr, types


class Results(commands.Cog):
    """
    Parses game console result codes.
    """
    def __init__(self, bot):
        self.bot = bot

    def fetch(self, error):
        if ctr.is_valid(error):
            return ctr.get(error)
        if wiiu.is_valid(error):
            return wiiu.get(error)
        if switch.is_valid(error):
            return switch.get(error)

        # Console name, module name, result, color
        return None, None, None, types.WARNING_COLOR

    def err2hex(self, error, suppress_error=False):
        # If it's already hex, just return it.
        if self.is_hex(error):
            return error

        # Only Switch is supported. The other two can only give nonsense results.
        if switch.is_valid(error):
            return switch.err2hex(error, suppress_error)

        if not suppress_error:
            return 'Invalid or unsupported error code format. \
Only Nintendo Switch XXXX-YYYY formatted error codes are supported.'

    def hex2err(self, error):
        # Don't bother processing anything if it's not hex.
        if self.is_hex(error):
            if ctr.is_valid(error):
                return ctr.hex2err(error)
            if wiiu.is_valid(error):
                return wiiu.hex2err(error)
            if switch.is_valid(error):
                return switch.hex2err(error)
        return 'This isn\'t a hexadecimal value!'

    def fixup_input(self, user_input):
        # Truncate input to 16 chars so as not to create a huge embed or do
        # eventual regex on a huge string. If we add support for consoles that
        # that have longer error codes, adjust accordingly.
        user_input = user_input[:16]

        # Fix up hex input if 0x was omitted. It's fine if it doesn't convert.
        try:
            user_input = hex(int(user_input, 16))
        except ValueError:
            pass

        return user_input

    def is_hex(self, user_input):
        try:
            user_input = hex(int(user_input, 16))
        except ValueError:
            return False
        return True

    def check_meme(self, err: str) -> str:
        memes = {
            '0xdeadbeef': 'you sure you want to eat that?',
            '0xdeadbabe': 'i think you have bigger problems if that\'s the case',
            '0x8badf00d': 'told you not to eat it'
        }
        return memes.get(err.casefold())

    @commands.command(aliases=['nxerr', 'serr', 'err', 'res'])
    async def result(self, ctx, err: str):
        """
        Displays information on game console result codes, with a fancy embed.
        0x prefix is not required for hex input.

        Examples:
          .err 0xD960D02B
          .err D960D02B
          .err 022-2634
          .err 102-2804
          .err 2168-0002
          .err 2-ARVHA-0000
        """
        err = self.fixup_input(err)
        if (meme := self.check_meme(err)) is not None:
            return await ctx.send(meme)

        system_name, module_name, error, color = self.fetch(err)

        if error:
            if self.is_hex(err):
                err_str = self.hex2err(err)
            else:
                err_str = self.err2hex(err, True)

            err_disp = f'{err}{"/" + err_str if err_str else ""}'
            embed = discord.Embed(title=f"{err_disp} ({system_name})")
            embed.add_field(name="Module", value=module_name, inline=False)

            if error.summary is not None:
                embed.add_field(name="Summary", value=error.summary, inline=False)
            if error.level is not None:
                embed.add_field(name="Level", value=error.level, inline=False)

            embed.add_field(name="Description", value=error.description, inline=False)

            if error.support_url:
                embed.add_field(name="Further information", value=error.support_url, inline=False)

            if error.is_ban:
                embed.add_field(
                    name="Console, account and game bans",
                    value="Nintendo Homebrew does not provide support \
for unbanning. Please do not ask for further assistance with this.")
            embed.color = color if not error.is_ban else types.WARNING_COLOR
            await ctx.send(embed=embed)
        else:
            await ctx.send(f'{ctx.author.mention}, the code you entered is \
invalid or is for a system I don\'t have support for.')

    @commands.command(name='err2hex')
    async def cmderr2hex(self, ctx, error: str):
        error = self.fixup_input(error)
        return await ctx.send(self.err2hex(error))

    @commands.command(name='hex2err')
    async def cmdhex2err(self, ctx, error: str):
        error = self.fixup_input(error)
        return await ctx.send(self.hex2err(error))


def setup(bot):
    bot.add_cog(Results(bot))
