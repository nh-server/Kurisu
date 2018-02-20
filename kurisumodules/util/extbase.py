from kurisu2 import Kurisu2  # for type hinting


class Extension:
    """Base class for Kurisu2 extensions."""

    def __init__(self, bot: Kurisu2):
        """Initialize the extension."""
        self.bot = bot
        self.log = bot.log

        self.restrictions = bot.restrictions
        self.warns = bot.warns
        self.configuration = bot.configuration
