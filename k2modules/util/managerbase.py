from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kurisu2 import Kurisu2


class BaseManager:
    """Base class for Kurisu2 managers."""

    def __init__(self, bot: 'Kurisu2'):
        self.bot = bot
        self.log = bot.log
        self.log.debug('Initializing %s', type(self).__name__)
