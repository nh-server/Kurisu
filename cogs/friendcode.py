import discord
import hashlib
import sqlite3
import struct
from cogs.database import DatabaseCog
from discord.ext import commands
from cogs.converters import SafeMember


class FriendCode(DatabaseCog):
    """
    Stores and obtains friend codes using an SQLite 3 database.
    """
    # based on https://github.com/megumisonoda/SaberBot/blob/master/lib/saberbot/valid_fc.rb
    def verify_fc(self, fc):
        fc = int(fc.replace('-', ''))
        if fc > 0x7FFFFFFFFF:
            return None
        principal_id = fc & 0xFFFFFFFF
        checksum = (fc & 0xFF00000000) >> 32
        return (fc if hashlib.sha1(struct.pack('<L', principal_id)).digest()[0] >> 1 == checksum else None)

    def fc_to_string(self, fc):
        fc = str(fc).rjust(12, '0')
        return "{} - {} - {}".format(fc[0:4], fc[4:8], fc[8:12])

    @commands.command(pass_context=True)
    async def fcregister(self, ctx, fc):
        """Add your friend code."""
        fc = self.verify_fc(fc)
        if not fc:
            await ctx.send("This friend code is invalid.")
            return
        rows = self.bot.c.execute('SELECT * FROM friend_codes WHERE user_id = ?', (ctx.author.id,))
        for row in rows:
            # if the user already has one, this prevents adding another
            await ctx.send("Please delete your current friend code with `.fcdelete` before adding another.")
            return
        self.bot.c.execute('INSERT INTO friend_codes VALUES (?,?)', (ctx.author.id, fc))
        await ctx.send("{} Friend code inserted: {}".format(ctx.author.mention, self.fc_to_string(fc)))
        self.bot.conn.commit()

    @commands.command(pass_context=True)
    async def fcquery(self, ctx, member:  SafeMember):
        """Get other user's friend code. You must have one yourself in the database."""
        rows = self.bot.c.execute('SELECT * FROM friend_codes WHERE userid = ?', (int(ctx.author.id),))
        for row in rows:
            # assuming there is only one, which there should be
            rows_m = c.execute('SELECT * FROM friend_codes WHERE userid = ?', (int(member.id),))
            for row_m in rows_m:
                await ctx.send("{} friend code is {}".format(member.mention, self.fc_to_string(row_m[1])))
                try:
                    member.send("{} has asked for your friend code! Their code is {}.".format(self.bot.escape_name(ctx.author), self.fc_to_string(row[1])))
                except discord.errors.Forbidden:
                    pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
                return
            await ctx.send("This user does not have a registered friend code.")
            return
        await ctx.send("You need to register your own friend code with `.fcregister <friendcode>` before getting others.")

    @commands.command(pass_context=True)
    async def fcdelete(self, ctx):
        """Delete your friend code."""
        c = self.bot.conn.cursor()
        c.execute('DELETE FROM friend_codes WHERE userid = ?', (ctx.author.id,))
        await ctx.send("Friend code removed from database.")
        self.bot.conn.commit()

    @commands.command()
    async def fctest(self, ctx, fc):
        fc = self.verify_fc(fc)
        if fc:
            await ctx.send(self.fc_to_string(fc))
        else:
            await ctx.send("Invalid.")


def setup(bot):
    bot.add_cog(FriendCode(bot))
