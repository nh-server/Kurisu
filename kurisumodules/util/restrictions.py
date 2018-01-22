import os.path
import sqlite3

import kurisu2  # for type hinting
from .tools import connwrap


class RestrictionsException(Exception):
    """General class for exceptions with RestrictionsManager"""


class RestrictionsManager:
    _db_closed = False

    def __init__(self, bot: kurisu2.Kurisu2, database_path: str):
        self.bot = bot
        self.log = bot.log
        self.dbpath = os.path.join(bot.config_directory, database_path)
        self.log.debug('Loading sqlite3 database: %s', self.dbpath)
        self.conn = sqlite3.connect(self.dbpath)
        try:
            with connwrap(self.conn) as c:
                c.execute('CREATE TABLE restrictions (`user id` INTEGER, `restriction` TEXT)')
        except sqlite3.OperationalError:
            # table likely exists
            pass
        else:
            self.log.info('restrictions table created in %s', self.dbpath)

    def close(self):
        if self._db_closed:
            return
        self.log.debug('Unloaded sqlite3 database: %s', self.dbpath)
        try:
            self.conn.commit()
            self.conn.close()
        except sqlite3.ProgrammingError:
            pass
        self._db_closed = True

    def __del__(self):
        # noinspection PyBroadException
        try:
            self.close()
        except Exception:
            pass  # this will only occur during shutdown if I screwed up

    def add_restriction(self, user_id: int, restriction: str) -> bool:
        assert not self._db_closed
        assert isinstance(user_id, int)
        with connwrap(self.conn) as c:
            res = c.execute('SELECT * FROM restrictions WHERE `user id` = ? AND `restriction` = ?',
                            (user_id, restriction))
            row = res.fetchone()
            if row is None:
                c.execute('INSERT INTO restrictions VALUES (?,?)', (user_id, restriction))
                c.execute()
                self.log.info('Added restriction to user id %d: %s', user_id, restriction)
                return True
            else:
                return False

    def remove_restriction(self, user_id: int, restriction: str) -> bool:
        assert not self._db_closed
        assert isinstance(user_id, int)
        with connwrap(self.conn) as c:
            res = c.execute('DELETE FROM restrictions WHERE `user id` = ? AND `restriction` = ?',
                            (user_id, restriction))
            result = bool(res.rowcount)
            if result:
                self.log.info('Removed restriction from user id %d: %s', user_id, restriction)
            return result
