from kurisu2 import Kurisu2
from .dbcommon import DatabaseManager


class WarnsManager(DatabaseManager):
    """Manages user warnings."""

    def __init__(self, bot: Kurisu2, database_path: str):
        super().__init__('warns', bot, database_path)
        self._create_tables((('snowflake', 'integer'), ('user_id', 'integer'), ('reason', 'text')))

    # TODO: WarnsManager
