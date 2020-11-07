import discord
from discord.ext import commands

from . import switch, wiiu_support, wiiu_results, ctr_support, ctr_results


class Results(commands.Cog):
    """
    Parses game console result codes.
    """
    def fetch(self, error):
        if ctr_support.is_valid(error):
            return ctr_support.get(error)
        if ctr_results.is_valid(error):
            return ctr_results.get(error)
        if wiiu_support.is_valid(error):
            return wiiu_support.get(error)
        if wiiu_results.is_valid(error):
            return wiiu_results.get(error)
        if switch.is_valid(error):
            return switch.get(error)

        # Console name, module name, result, color
        return None

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

    def hex2err(self, error, suppress_error=False):
        # Don't bother processing anything if it's not hex.
        if self.is_hex(error):
            if switch.is_valid(error):
                return switch.hex2err(error)
        if not suppress_error:
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

    @commands.command(aliases=['err', 'res'])
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

        ret = self.fetch(err)

        if ret:
            embed = discord.Embed(title=ret.get_title())
            if ret.extra_description:
                embed.description = ret.extra_description
            for field in ret:
                embed.add_field(name=field.field_name, value=field.message, inline=False)

            embed.color = ret.color
            await ctx.send(embed=embed)
        else:
            await ctx.send(f'{ctx.author.mention}, the code you entered is \
invalid or is for a system I don\'t have support for.')

    @commands.command(aliases=['serr'])
    async def nxerr(self, ctx, err: str):
        """
        Displays information on switch result codes, with a fancy embed.
        0x prefix is not required for hex input.

        Examples:
          .nxerr 0x4A8
          .nxerr 4A8
          .nxerr 2168-0002
          .nxerr 2-ARVHA-0000
        """
        err = self.fixup_input(err)
        if (meme := self.check_meme(err)) is not None:
            return await ctx.send(meme)

        ret = None

        if switch.is_valid(err):
            ret = switch.get(err)

        if ret:
            embed = discord.Embed(title=ret.get_title())
            if ret.extra_description:
                embed.description = ret.extra_description
            for field in ret:
                embed.add_field(name=field.field_name, value=field.message, inline=False)

            embed.color = ret.color
            await ctx.send(embed=embed)
        else:
            await ctx.send(f'{ctx.author.mention}, the code you entered is \
invalid for the switch.')

    @commands.command(aliases=['3dserr'])
    async def ctrerr(self, ctx, err: str):
        """
        Displays information on 3DS result codes, with a fancy embed.
        0x prefix is not required for hex input.

        Examples:
          .ctrerr 0xD960D02B
          .ctrerr D960D02B
          .ctrerr 022-2634
        """
        err = self.fixup_input(err)
        if (meme := self.check_meme(err)) is not None:
            return await ctx.send(meme)

        ret = None

        if ctr_support.is_valid(err):
            ret = ctr_support.get(err)
        elif ctr_results.is_valid(err):
            ret = ctr_results.get(err)

        if ret:
            embed = discord.Embed(title=ret.get_title())
            if ret.extra_description:
                embed.description = ret.extra_description
            for field in ret:
                embed.add_field(name=field.field_name, value=field.message, inline=False)

            embed.color = ret.color
            await ctx.send(embed=embed)
        else:
            await ctx.send(f'{ctx.author.mention}, the code you entered is \
invalid for the 3DS.')

    @commands.command(aliases=['wiiuerr'])
    async def cafeerr(self, ctx, err: str):
        """
        Displays information on Wii U result codes, with a fancy embed.
        0x prefix is not required for hex input.

        Examples:
          .cafeerr 0xC070FA80
          .cafeerr C070FA80
          .cafeerr 0x18106FFF
          .cafeerr 18106FFF
          .cafeerr 102-2804
        """
        err = self.fixup_input(err)
        if (meme := self.check_meme(err)) is not None:
            return await ctx.send(meme)

        ret = None

        if wiiu_support.is_valid(err):
            ret = wiiu_support.get(err)
        elif wiiu_results.is_valid(err):
            ret = wiiu_results.get(err)

        if ret:
            embed = discord.Embed(title=ret.get_title())
            if ret.extra_description:
                embed.description = ret.extra_description
            for field in ret:
                embed.add_field(name=field.field_name, value=field.message, inline=False)

            embed.color = ret.color
            await ctx.send(embed=embed)
        else:
            await ctx.send(f'{ctx.author.mention}, the code you entered is \
invalid for the Wii U.')

    @commands.command(name='err2hex')
    async def cmderr2hex(self, ctx, error: str):
        """
        Converts a support code of a console to a hex result code.

        Switch only supported.
        3DS and WiiU support and result codes are not directly interchangeable.
        """
        error = self.fixup_input(error)
        await ctx.send(self.err2hex(error))

    @commands.command(name='hex2err')
    async def cmdhex2err(self, ctx, error: str):
        """
        Converts a hex result code of a console to a support code.

        Switch only supported.
        3DS and WiiU support and result codes are not directly interchangeable.
        """
        error = self.fixup_input(error)
        await ctx.send(self.hex2err(error))

    @commands.command()
    async def hexinfo(self, ctx, error: str):
        """
        Breaks down a 3DS result code into its components.
        """
        error = self.fixup_input(error)
        if self.is_hex(error):
            if ctr_results.is_valid(error):
                mod, desc, summary, level = ctr_results.hexinfo(error)
                embed = discord.Embed(title="3DS hex result info")
                embed.add_field(name="Module", value=mod, inline=False)
                embed.add_field(name="Summary", value=summary, inline=False)
                embed.add_field(name="Level", value=level, inline=False)
                embed.add_field(name="Description", value=desc, inline=False)

                await ctx.send(embed=embed)
            else:
                await ctx.send('This isn\'t a 3DS result code.')
        else:
            await ctx.send('This isn\'t a hexadecimal value!')


def setup(bot):
    bot.add_cog(Results(bot))
