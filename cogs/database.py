import time
from discord.ext import commands


class DatabaseCog(commands.Cog):
    """
    Base class for cogs that interact with the database.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Cog "{}" loaded'.format(self.qualified_name))

    def add_staff(self, user_id, position):
        self.bot.c.execute('DELETE FROM staff WHERE user_id=?',(user_id,))
        self.bot.c.execute('INSERT INTO staff VALUES(?, ?)', (user_id, position))
        self.bot.conn.commit()

    def remove_staff(self, user_id):
        self.bot.c.execute('DELETE FROM staff WHERE user_id=?', (user_id,))
        self.bot.conn.commit()

    def get_staff(self):
        stafflist = [x[0] for x in self.bot.c.execute('SELECT user_id FROM staff').fetchall()]
        return stafflist

    def get_helpers(self):
        helperlist = [x[0] for x in self.bot.c.execute('SELECT user_id FROM helpers').fetchall()]
        return helperlist

    def add_helper(self, user_id, console):
        self.bot.c.execute('DELETE FROM helpers WHERE user_id=?',(user_id,))
        self.bot.c.execute('INSERT INTO helpers VALUES(?, ?)', (user_id, console))
        self.bot.conn.commit()

    def remove_helper(self, user_id):
        self.bot.c.execute('DELETE FROM helpers WHERE user_id=?', (user_id,))
        self.bot.conn.commit()

    def get_console(self, user_id):
        console = self.bot.c.execute('SELECT console FROM helpers WHERE user_id=?', (user_id,)).fetchone()
        if console:
            return console[0]
        return None

    def get_stafftrole(self, user_id):
        rank = self.bot.c.execute('SELECT position FROM staff WHERE user_id=?', (user_id,)).fetchone()
        if rank:
            return rank[0]
        return None

    def add_timed_restriction(self, user_id, end_date, type):
        self.bot.c.execute('INSERT INTO timed_restriction VALUES(?, ?, ?)',(user_id, end_date, type))
        self.bot.conn.commit()

    def remove_timed_restriction(self, user_id, type):
        self.bot.c.execute('DELETE FROM timed_restriction WHERE user_id=? AND type=?',(user_id, type))
        self.bot.conn.commit()

    def add_softban(self, ctx, user, reason):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.bot.c.execute('INSERT INTO softbans VALUES(?, ? , ? , ?, ?)',(user.id, user.name, ctx.author.id, reason, timestamp))
        self.bot.conn.commit()

    def remove_softban(self, user_id):
        self.bot.c.execute('DELETE FROM softbans WHERE user_id = ?',(user_id,))
        self.bot.conn.commit()

    def add_watch(self, member):
        self.bot.c.execute('INSERT INTO watchlist VALUES(?,?)', (member.id, member.name))
        self.bot.conn.commit()

    def remove_watch(self, member):
        self.bot.c.execute('DELETE FROM watchlist WHERE user_id=?', (member.id,))
        self.bot.conn.commit()


