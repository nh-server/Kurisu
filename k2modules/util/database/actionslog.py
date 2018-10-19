from collections import OrderedDict

from .common import BaseDatabaseManager

tables = {'actions_log': OrderedDict((('snowflake', 'blob'), ('user_id', 'blob'), ('type', 'text'), ('reason', 'text'),
                                      ('attachments', 'blob')))}


class ActionsLogDatabaseManager(BaseDatabaseManager, tables=tables):
    """Manages the actions_log database."""

    # TODO: ActionsLogDatabaseManager

    def add_entry(self, user_id: int, action_type: str):
        pass
