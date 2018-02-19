from kurisu2 import Kurisu2
from .dbcommon import DatabaseManager

# I can't really think of a use for this... maybe I'll remove it if nothing happens.


class ConfigurationManager(DatabaseManager):
    """Manages bot configuration."""

    def __init__(self, bot: Kurisu2, database_path: str):
        super().__init__('configuration', bot, database_path)
        self._create_tables(key='text', value='text')

    # TODO: ConfigurationManager
