from datetime import datetime
import time
from discord.ext import commands
from discord import utils
import aiosqlite3
import os


class ConnectionHolder:
    def __init__(self):
        self.dbcon = None

    async def load_db(self, database_name, loop):
        if not os.path.isfile(database_name):
            print(f'Creating database {database_name}')
            with open('schema.sql', 'r', encoding='utf-8') as f:
                schema = f.read()
            self.dbcon = await aiosqlite3.connect(database_name, loop=loop)
            await self.dbcon.executescript(schema)
            await self.dbcon.commit()
            print(f'{database_name} initialized')
        else:
            self.dbcon = await aiosqlite3.connect(database_name, loop=loop)
            print(f'Loaded {database_name}')

    async def __aenter__(self):
        self.dbcon.__enter__()
        cursor = await self.dbcon.cursor()
        return cursor

    async def __aexit__(self, exc_class, exc, traceback):
        self.dbcon.__exit__(exc_class, exc, traceback)
        if self.dbcon.in_transaction:
            await self.dbcon.commit()


class DatabaseCog(commands.Cog):
    """
    Base class for cogs that interact with the database.
    """
    def __init__(self, bot):
        self.bot = bot
        print(f'Cog "{self.qualified_name}" loaded')

    async def add_restriction(self, user_id, role):
        async with self.bot.holder as cur:
            await cur.execute('SELECT user_id FROM permanent_roles WHERE user_id=? AND role_id=?', (user_id, role.id))
            if await cur.fetchone() is None:
                await cur.execute('INSERT INTO permanent_roles VALUES(?, ?)', (user_id, role.id))
                return True
            return False

    async def remove_restriction(self, user_id, role):
        async with self.bot.holder as cur:
            await cur.execute('DELETE FROM permanent_roles WHERE user_id=? AND role_id=?', (user_id, role.id))

    async def get_restrictions_roles_id(self, user_id):
        async with self.bot.holder as cur:
            await cur.execute('SELECT role_id FROM permanent_roles WHERE user_id=?', (user_id,))
            rows = await cur.fetchall()
            if rows:
                return [x[0] for x in rows]
            return []

    async def add_staff(self, user_id, position):
        async with self.bot.holder as cur:
            if await self.get_stafftrole(user_id) is None:
                await cur.execute('INSERT INTO staff VALUES(?, ?)', (user_id, position))
            else:
                await cur.execute('UPDATE staff SET position=? WHERE user_id=? ', (position, user_id))

    async def remove_staff(self, user_id):
        async with self.bot.holder as cur:
            await cur.execute('DELETE FROM staff WHERE user_id=?', (user_id,))

    async def get_staff(self):
        async with self.bot.holder as cur:
            await cur.execute('SELECT user_id FROM staff')
            rows = await cur.fetchall()
            if rows:
                return [x[0] for x in rows]
            return []

    async def get_helpers(self):
        async with self.bot.holder as cur:
            await cur.execute('SELECT user_id FROM helpers')
            rows = await cur.fetchall()
            if rows:
                return [x[0] for x in rows]
            return []

    async def add_helper(self, user_id, console):
        async with self.bot.holder as cur:
            if await self.get_console(user_id) is None:
                await cur.execute('INSERT INTO helpers VALUES(?, ?)', (user_id, console))
            else:
                await cur.execute('UPDATE helpers SET console=? WHERE user_id=?', (console, user_id))

    async def remove_helper(self, user_id):
        async with self.bot.holder as cur:
            await cur.execute('DELETE FROM helpers WHERE user_id=?', (user_id,))

    async def get_console(self, user_id):
        async with self.bot.holder as cur:
            await cur.execute('SELECT console FROM helpers WHERE user_id=?', (user_id,))
            row = await cur.fetchone()
            return row[0] if row is not None else row

    async def get_stafftrole(self, user_id):
        async with self.bot.holder as cur:
            await cur.execute('SELECT position FROM staff WHERE user_id=?', (user_id,))
            rank = await cur.fetchone()
            return rank[0] if rank is not None else rank

    async def add_warn(self, user_id, issuer_id, reason):
        async with self.bot.holder as cur:
            snowflake = utils.time_snowflake(datetime.now())
            await cur.execute('INSERT INTO warns VALUES(?, ?, ?, ?)', (snowflake, user_id, issuer_id, reason))

    async def remove_warn_id(self, user_id, index):
        # i dont feel so good
        async with self.bot.holder as cur:
            await cur.execute('DELETE FROM warns WHERE warn_id in (SELECT warn_id FROM warns WHERE user_id=? LIMIT ?,1)', (user_id, index-1))

    async def remove_warns(self, user_id):
        async with self.bot.holder as cur:
            await cur.execute('DELETE FROM warns WHERE user_id=?', (user_id,))

    async def get_warns(self, user_id):
        async with self.bot.holder as cur:
            await cur.execute('SELECT * FROM warns WHERE user_id=?', (user_id,))
            return await cur.fetchall()

    async def add_timed_restriction(self, user_id, end_date, type):
        async with self.bot.holder as cur:
            await cur.execute('SELECT 1 FROM timed_restrictions WHERE user_id=? AND type=?', (user_id, type))
            if await cur.fetchone() is not None:
                await cur.execute('UPDATE timed_restrictions SET timestamp=?, alert=0 WHERE user_id=? AND type=?', (end_date, user_id, type))
            else:
                await cur.execute('INSERT INTO timed_restrictions VALUES(?, ?, ?, ?)', (user_id, end_date, type, 0))

    async def remove_timed_restriction(self, user_id, type):
        async with self.bot.holder as cur:
            await cur.execute('DELETE FROM timed_restrictions WHERE user_id=? AND type=?', (user_id, type))

    async def get_time_restrictions_by_user_type(self, userid, type):
        async with self.bot.holder as cur:
            await cur.execute('SELECT * from timed_restrictions WHERE user_id=? AND type=?', (userid,type))
            return await cur.fetchone()

    async def get_time_restrictions_by_type(self, type):
        async with self.bot.holder as cur:
            await cur.execute('SELECT * from timed_restrictions WHERE type=?', (type,))
            return await cur.fetchall()

    async def set_time_restriction_alert(self, user_id, type):
        async with self.bot.holder as cur:
            await cur.execute('UPDATE timed_restrictions SET alert=1 WHERE user_id=? AND type=?', (user_id, type))

    async def add_softban(self, user_id, issuer_id, reason, timestamp=None):
        if not timestamp:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        async with self.bot.holder as cur:
            await cur.execute('INSERT INTO softbans VALUES(?, ? , ?, ?)', (user_id, issuer_id, reason, timestamp))

    async def remove_softban(self, user_id):
        async with self.bot.holder as cur:
            await cur.execute('DELETE FROM softbans WHERE user_id = ?', (user_id,))

    async def get_softban(self, user_id):
        async with self.bot.holder as cur:
            await cur.execute('SELECT * FROM softbans WHERE user_id=?', (user_id,))
            return await cur.fetchone()

    async def add_watch(self, user_id):
        async with self.bot.holder as cur:
            await cur.execute('INSERT INTO watchlist VALUES(?)', (user_id,))

    async def remove_watch(self, user_id):
        async with self.bot.holder as cur:
            await cur.execute('DELETE FROM watchlist WHERE user_id=?', (user_id,))

    async def is_watched(self, user_id):
        async with self.bot.holder as cur:
            await cur.execute('SELECT user_id FROM watchlist WHERE user_id=?', (user_id,))
            return await cur.fetchone() is not None

    async def add_nofilter(self, channel):
        async with self.bot.holder as cur:
            await cur.execute('INSERT INTO nofilter VALUES(?)', (channel.id,))

    async def remove_nofilter(self, channel):
        async with self.bot.holder as cur:
            await cur.execute('DELETE FROM nofilter WHERE channel_id=?', (channel.id,))

    async def check_nofilter(self, channel):
        async with self.bot.holder as cur:
            await cur.execute('SELECT channel_id FROM nofilter WHERE channel_id=?', (channel.id,))
            return await cur.fetchone() is not None

    async def add_friendcode(self, user_id, fc):
        async with self.bot.holder as cur:
            await cur.execute('INSERT INTO friend_codes VALUES (?,?)', (user_id, fc))

    async def get_friendcode(self, user_id):
        async with self.bot.holder as cur:
            return await cur.execute('SELECT * FROM friend_codes WHERE user_id = ?', (user_id,))

    async def delete_friendcode(self, user_id):
        async with self.bot.holder as cur:
            await cur.execute('DELETE FROM friend_codes WHERE user_id = ?', (user_id,))
