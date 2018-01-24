import kurisu2
from .dbcommon import DatabaseManager


class ConfigurationManager(DatabaseManager):
    """Manages bot configuration."""

    def __init__(self, bot: kurisu2.Kurisu2, database_path: str):
        self.log.debug('Initializing %s', type(self).__name__)
        super().__init__('configuration', bot, database_path)
        self._create_tables((('key', 'text'), ('value', 'text')))

    # TODO: ConfigurationManager
