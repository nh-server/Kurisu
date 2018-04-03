from .common import DatabaseManager

# I can't really think of a use for this... maybe I'll remove it if nothing happens.


class ConfigurationDatabaseManager(DatabaseManager, table='configuration', columns={'key': 'text', 'value': 'text'}):
    """Manages the configuration database."""

    # TODO: ConfigurationDatabaseManager
