import time
from discord.ext import commands


class DatabaseCog(commands.Cog):
    """
    Base class for cogs that interact with the database.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Cog "{}" loaded'.format(self.qualified_name))

    def add_restriction(self, user_id, role):
        if self.bot.c.execute('SELECT user_id FROM permanent_roles WHERE user_id=? AND role=?', (user_id, role)).fetchone() is None:
            self.bot.c.execute('INSERT INTO permanent_roles VALUES(?, ?)', (user_id, role))
            self.bot.conn.commit()

    def remove_restriction(self, user_id, role):
        self.bot.c.execute('DELETE FROM permanent_roles WHERE user_id=? AND role=?', (user_id, role))
        self.bot.conn.commit()

    def get_restrictions_roles(self, user_id):
        rows = self.bot.c.execute('SELECT role FROM permanent_roles WHERE user_id=?', (user_id,)).fetchall()
        if rows:
            return [x[0] for x in rows]
        return []

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

    def add_warn(self, user_id, issuer_id, reason, timestamp):
        self.bot.c.execute('INSERT INTO warns VALUES(?, ?, ?, ?)', (user_id, issuer_id, reason, timestamp))
        self.bot.conn.commit()

    def remove_warn(self, user_id, index):
        # i dont feel so good
        self.bot.c.execute('DELETE FROM warns WHERE rowid in (SELECT rowid FROM warns WHERE user_id=? LIMIT ?,1)', (user_id,index-1))
        self.bot.conn.commit()

    def remove_warns(self, user_id):
        self.bot.c.execute('DELETE FROM warns WHERE user_id=?', (user_id,))
        self.bot.conn.commit()

    def get_warns(self, user_id):
        warns = self.bot.c.execute('SELECT * FROM warns WHERE user_id=?', (user_id,)).fetchall()
        return warns

    def add_timed_restriction(self, user_id, end_date, type):
        if self.bot.c.execute('SELECT 1 FROM timed_restrictions WHERE user_id=? AND type=?', (user_id, type)).fetchone() is not None:
            self.remove_timed_restriction(user_id, type)
        self.bot.c.execute('INSERT INTO timed_restrictions VALUES(?, ?, ?, ?)', (user_id, end_date, type, 0))
        self.bot.conn.commit()

    def remove_timed_restriction(self, user_id, type):
        self.bot.c.execute('DELETE FROM timed_restrictions WHERE user_id=? AND type=?', (user_id, type))
        self.bot.conn.commit()

    def get_time_restrictions(self, type):
        return self.bot.c.execute('SELECT * from timed_restrictions WHERE type=?', (type,))

    def set_time_restriction_alert(self, user_id, type):
        self.bot.c.execute('UPDATE timed_restrictions SET alert=1 WHERE user_id=? AND type=?',(user_id, type))
        self.bot.conn.commit()

    def add_softban(self, ctx, user, reason):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.bot.c.execute('INSERT INTO softbans VALUES(?, ? , ? , ?, ?)',(user.id, user.name, ctx.author.id, reason, timestamp))
        self.bot.conn.commit()

    def remove_softban(self, user_id):
        self.bot.c.execute('DELETE FROM softbans WHERE user_id = ?',(user_id,))
        self.bot.conn.commit()

    def get_softbans(self, user_id):
        rows = self.bot.c.execute('SELECT * FROM softbans WHERE user_id=?', (user_id,)).fetchall()
        return rows

    def add_watch(self, user_id):
        self.bot.c.execute('INSERT INTO watchlist VALUES(?)', (user_id,))
        self.bot.conn.commit()

    def remove_watch(self, user_id):
        self.bot.c.execute('DELETE FROM watchlist WHERE user_id=?', (user_id,))
        self.bot.conn.commit()

    def is_watched(self, user_id):
        if self.bot.c.execute('SELECT user_id FROM watchlist WHERE user_id=?', (user_id,)).fetchone():
            return True
        return False


