from typing import TYPE_CHECKING

from . import BaseManager
from .database import RestrictionsDatabaseManager

if TYPE_CHECKING:
    from kurisu2 import Kurisu2


class RestrictionsManager(BaseManager):
    """Manages user restrictions."""

    # TODO: RestrictionsManager

    def __init__(self, bot: 'Kurisu2'):
        super().__init__(bot)
        self.db = RestrictionsDatabaseManager(bot, 'restrictions.sqlite3')
