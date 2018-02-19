from .dbcommon import DatabaseManager

# I can't really think of a use for this... maybe I'll remove it if nothing happens.


class ConfigurationManager(DatabaseManager, table='configuration', columns={'key': 'text', 'value': 'text'}):
    """Manages bot configuration."""

    # TODO: ConfigurationManager
