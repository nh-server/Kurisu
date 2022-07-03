from typing import TYPE_CHECKING
import logging
if TYPE_CHECKING:
    from typing import Type, Optional
    from kurisu import Kurisu
    from .database import BaseDatabaseManager


class BaseManager:
    """Base class for Kurisu managers."""

    db_manager: 'Optional[Type[BaseDatabaseManager]]'

    def __init__(self, bot: 'Kurisu'):
        self.bot = bot
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(logging.DEBUG)
        self.log.debug('Initializing %s', type(self).__name__)

        if self.db_manager:
            self.db = self.db_manager(bot)

    # until PyCharm recognizes __init_subclass__ properly, these inspections must be disabled
    # noinspection PyMethodOverriding,PyArgumentList
    def __init_subclass__(cls, *, db_manager: 'Optional[Type[BaseDatabaseManager]]' = None, **kwargs):
        cls.db_manager = db_manager
