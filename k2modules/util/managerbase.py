from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Type
    from kurisu2 import Kurisu2
    from .database import BaseDatabaseManager


class BaseManager:
    """Base class for Kurisu2 managers."""

    def __init__(self, bot: 'Kurisu2'):
        self.bot = bot
        self.log = bot.log
        self.log.debug('Initializing %s', type(self).__name__)

        if self.db_manager:
            self.db = self.db_manager(bot, self.db_filename)

    # until PyCharm recognizes __init_subclass__ properly, these inspections must be disabled
    # noinspection PyMethodOverriding,PyArgumentList
    def __init_subclass__(cls, *, db_manager: 'Type[BaseDatabaseManager]' = None, db_filename: str = None, **kwargs):
        cls.db_manager = db_manager
        cls.db_filename = db_filename

    def close(self):
        try:
            self.db.close()
        except AttributeError:
            pass
