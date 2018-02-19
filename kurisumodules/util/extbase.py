from kurisu2 import Kurisu2  # for type hinting


class ExtensionBase:
    """Base class for Kurisu2 extensions."""

    def __init__(self, bot: Kurisu2):
        """Initialize the extension."""
        self.bot = bot
        self.log = bot.log
