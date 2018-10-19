from collections import OrderedDict

from .common import BaseDatabaseManager

# I can't really think of a use for this... maybe I'll remove it if nothing happens.

tables = {'configuration': OrderedDict((('key', 'text'), ('value', 'text')))}


class ConfigurationDatabaseManager(BaseDatabaseManager, tables=tables):
    """Manages the configuration database."""

    # TODO: ConfigurationDatabaseManager
