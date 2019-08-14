# ISC License
#
# Copyright (c) 2019, Valentijn "noirscape" V.
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

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
        mariko = False
        if not re.match("XA[JKW][1479][0-9]{6}", serial):

            # This should catch serials from the new "mariko" units
            # XKW10000000000, XKJ10000000000 = HAC-001-01, the "New Switch"
            # XJW01000000000, XWW01000000000 = HOH-001, the Switch Lite
            # As not much about the assembly line is known yet every digit will count for the filter
            if re.match("X[KW][JW][0-9]{7}", serial):
                mariko = True
            else:
                return await ctx.send("This is not a valid serial number!\n"
                                      "If you believe this to be an error, contact staff.")

        patched = False
        maybe = False
        region = serial[2]

        assembly_line = int(serial[3])
        checking_value = int(serial[3:10])
        safe_serial = serial[:9] + 'XXXX'

        if region == 'J':
            if assembly_line == 1:
                if checking_value < 1002000:
                    pass
                elif 1002000 <= checking_value < 1003000:
                    maybe = True
                elif checking_value >= 1003000:
                    patched = True

            elif assembly_line == 4:
                if checking_value < 4004600:
                    pass
                elif 4004600 <= checking_value < 4006000:
                    maybe = True
                elif checking_value >= 4006000:
                    patched = True

            elif assembly_line == 7:
                if checking_value < 7004000:
                    pass
                elif 7004000 <= checking_value < 7005000:
                    maybe = True
                elif checking_value >= 7005000:
                    patched = True

        elif region == 'W':
            if assembly_line == 1:
                if checking_value < 1007400:
                    pass
                elif 1007400 <= checking_value < 1012000:  # GBATemp thread is oddly disjointed here, proper value could
                    # be 1007500, not sure.
                    maybe = True
                elif checking_value >= 1012000:
                    patched = True

            elif assembly_line == 4:
                if checking_value < 4001100:
                    pass
                elif 4001100 <= checking_value < 4001200:
                    maybe = True
                elif checking_value >= 4001200:
                    patched = True

            elif assembly_line == 7:
                if checking_value < 7001780:
                    pass
                elif 7001780 <= checking_value < 7003000:
                    maybe = True
                elif checking_value >= 7003000:
                    maybe = True

            elif assembly_line == 9:
                maybe = True

        elif region == 'K':
            maybe = True

        try:
            await ctx.message.delete()
        except:
            pass

        if mariko:
            return await ctx.send("{}: Serial {} seems to be a \"mariko\" Switch or Switch Lite.\n" 
                                  "These are currently not hackable or vulnerable to any known exploits".format(ctx.author.mention, safe_serial))
        elif maybe:
            return await ctx.send("{}: Serial {} _might_ be patched. The only way you can know this for sure is by "
                                  "pushing the payload manually. You can find instructions to do so here: "
                                  "https://switchgui.de/switch-guide/user_guide/emummc/sending_payload/".format(ctx.author.mention,
                                                                                                     safe_serial))
        elif patched:
            return await ctx.send("{}: Serial {} is patched.".format(ctx.author.mention, safe_serial))
        else:
            return await ctx.send("{}: Serial {} is not patched.".format(ctx.author.mention, safe_serial))
