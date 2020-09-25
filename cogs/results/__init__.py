import discord
from discord.ext import commands

from . import (switch, wiiu, ctr, types)

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

    def err2hex(self, error):
        # Only Switch is supported. The other two can only give nonsense results.
        if switch.is_valid(error):
            return switch.err2hex(error)

    def hex2err(self, error):
        if ctr.is_valid(error):
            return ctr.hex2err(error)
        if wiiu.is_valid(error):
            return wiiu.err2hex(error)
        if switch.is_valid(error):
            return switch.hex2err(error)

    def fixup_input(self, input):
        # Truncate input to 16 chars so as not to create a huge embed or do
        # eventual regex on a huge string. If we add support for consoles that
        # that have longer error codes, adjust accordingly.
        input = input[:16]
        self.is_hex = False
        # Fix up hex input if 0x was omitted. It's fine if it doesn't convert.
        if not input.startswith('0x'):
            try:
                input = hex(int(input, 16))
                self.is_hex = True
            except ValueError:
                pass
        else:
            self.is_hex = True
        return input

    def check_meme(self, err:str) -> str:
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
            extra = f'{self.err2hex(err) if not self.is_hex else err}/{self.hex2err(err) if self.is_hex else err}'
            embed = discord.Embed(title=f"{extra} ({system_name})")
            embed.add_field(name="Module", value=module_name, inline=False)

            if error.summary is not None:
                embed.add_field(name="Summary", value=error.summary, inline=False)
            if error.level is not None:
                embed.add_field(name="Level", value=error.level, inline=False)

            embed.add_field(name="Description", value=error.description, inline=False)

            if error.support_url:
                embed.add_field(name="Further information", value=error.support_url, inline=False)

            if error.is_ban:
                embed.add_field(name="Console, account and game bans", value="Nintendo Homebrew does not provide support for unbanning your game or console. Please do not ask for further assistance with this.")
            embed.color = color
            await ctx.send(embed=embed)
        else:
            await ctx.send(f'{ctx.author.mention}, the code you entered is \
invalid or is for a system I don\'t have support for.', delete_after=10)

    @commands.command(name='err2hex')
    async def cmderr2hex(self, ctx, error:str):
        error = self.fixup_input(error)
        return await ctx.send(self.err2hex(error))

    @commands.command(name='hex2err')
    async def cmdhex2err(self, ctx, error:str):
        error = self.fixup_input(error)
        return await ctx.send(self.hex2err(error))
  
def setup(bot):
    bot.add_cog(Results(bot))

