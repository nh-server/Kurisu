import discord
import hashlib
import sqlite3
import struct
from discord.ext import commands
from sys import argv

class FriendCode:
    """
    Stores and obtains friend codes using an SQLite 3 database.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Loading fc.sqlite')
        self.conn = sqlite3.connect('fc.sqlite')
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    def __unload(self):
        print('Unloading fc.sqlite')
        self.conn.commit()
        self.conn.close()

    # based on https://github.com/megumisonoda/SaberBot/blob/master/lib/saberbot/valid_fc.rb
    def verify_fc(self, fc):
        fc = int(fc.replace('-', ''))
        if fc > 0x7FFFFFFFFF or fc < 0x0100000000:
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
            await self.bot.say("This friend code is invalid.")
            return
        c = self.conn.cursor()
        rows = c.execute('SELECT * FROM friend_codes WHERE userid = ?', (ctx.message.author.id,))
        for row in rows:
            # if the user already has one, this prevents adding another
            await self.bot.say("Please delete your current friend code with `.fcdelete` before adding another.")
            return
        c.execute('INSERT INTO friend_codes VALUES (?,?)', (ctx.message.author.id, fc))
        await self.bot.say("{} Friend code inserted: {}".format(ctx.message.author.mention, self.fc_to_string(fc)))

    @commands.command(pass_context=True)
    async def fcquery(self, ctx, user):
        """Get other user's friend code. You must have one yourself in the database."""
        c = self.conn.cursor()
        member = ctx.message.mentions[0]
        rows = c.execute('SELECT * FROM friend_codes WHERE userid = ?', (ctx.message.author.id,))
        for row in rows:
            # assuming there is only one, which there should be
            rows_m = c.execute('SELECT * FROM friend_codes WHERE userid = ?', (member.id,))
            for row_m in rows_m:
                await self.bot.say("{} friend code is {}".format(member.mention, self.fc_to_string(row_m[1])))
                try:
                    await self.bot.send_message(member, "{} has asked for your friend code! Their code is {}.".format(self.bot.escape_name(member), self.fc_to_string(row[1])))
                except discord.errors.Forbidden:
                    pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
                return
            await self.bot.say("This user does not have a registered friend code.")
            return
        await self.bot.say("You need to register your own friend code with `.fcregister <friendcode>` before getting others.")

    @commands.command(pass_context=True)
    async def fcdelete(self, ctx):
        """Delete your friend code."""
        c = self.conn.cursor()
        c.execute('DELETE FROM friend_codes WHERE userid = ?', (ctx.message.author.id,))
        await self.bot.say("Friend code removed from database.")

    @commands.command()
    async def fctest(self, fc):
        fc = self.verify_fc(fc)
        if fc:
            await self.bot.say(self.fc_to_string(fc))
        else:
            await self.bot.say("invalid")

def setup(bot):
    bot.add_cog(FriendCode(bot))
