from .managerbase import BaseManager
from .database import RestrictionsDatabaseManager


class RestrictionsManager(BaseManager, db_manager=RestrictionsDatabaseManager):
    """Manages user restrictions."""

    db: RestrictionsDatabaseManager

    # TODO: RestrictionsManager
