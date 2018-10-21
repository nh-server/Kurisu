from .managerbase import BaseManager
from .database import RestrictionsDatabaseManager


class RestrictionsManager(BaseManager, db_manager=RestrictionsDatabaseManager, db_filename='restrictions.sqlite3'):
    """Manages user restrictions."""

    db: RestrictionsDatabaseManager

    # TODO: RestrictionsManager
