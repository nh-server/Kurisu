import discord
from discord.ext import commands
from discord.ext.commands import Cog
import re


def setup(bot):
    bot.add_cog(SwitchSerialNumberCheck(bot))


class SwitchSerialNumberCheck(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["ssnc"])
    async def check_nx_serial(self, ctx, serial):
        """Check the given Switch serial to see if it is patched or not. For safety reasons, the invoking message is
        removed."""
        serial = serial.split()[0].upper()
        if not re.match("XA[JWK][1479][0-9]{6}", serial):
            return await ctx.send("This is not a valid serial number!\n"
                                  "If you believe this to be in error, contact staff.")

        patched = False
        maybe = False
        region = serial[2]

        assembly_line = int(serial[3])
        checking_value = int(serial[3:10])
        print(f"{checking_value} : {len(str(checking_value))}")
        safe_serial = serial[:9] + 'XXXX'

        if region == 'J':
            if assembly_line == 1:
                if 1002100 <= checking_value <= 1002999:
                    maybe = True
                elif checking_value >= 1003000:
                    pass

            elif assembly_line == 4:
                if 4004700 <= checking_value <= 4005999:
                    maybe = True
                elif checking_value >= 4006000:
                    pass

            elif assembly_line == 7:
                if 7004100 <= checking_value <= 7004999:
                    maybe = True
                elif checking_value >= 7005000:
                    pass

            elif assembly_line == 9:
                maybe = True

        elif region == 'W':
            if assembly_line == 1:
                if 1007900 <= checking_value <= 1008199:
                    maybe = True
                elif checking_value >= 1008200:
                    pass

            elif assembly_line == 4:
                if 4001200 <= checking_value <= 4002999:
                    maybe = True
                elif checking_value >= 4003000:
                    pass

            elif assembly_line == 7:
                if 7001790 <= checking_value <= 7002999:
                    maybe = True
                elif checking_value >= 7003000:
                    pass

        elif region == 'K':
            maybe = True

        try:
            await ctx.message.delete()
        except:
            pass

        if maybe:
            return await ctx.send("{}: Serial {} _might_ be patched. The only way you can know this for sure is by "
                                  "pushing the payload manually. You can find instructions to do so here: "
                                  "https://nh-server.github.io/switch-guide/extras/rcm_test/".format(ctx.author.mention,
                                                                                                     safe_serial))
        elif patched:
            return await ctx.send("{}: Serial {} is patched.".format(ctx.author.mention, safe_serial))
        else:
            return await ctx.send("{}: Serial {} is not patched.".format(ctx.author.mention, safe_serial))
