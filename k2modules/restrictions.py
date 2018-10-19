from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from .util import Extension

if TYPE_CHECKING:
    from kurisu2 import Kurisu2  # for type hinting


class Restrictions(Extension):
    """Restrictions for users."""

    # TODO: Restrictions


def setup(bot: 'Kurisu2'):
    bot.add_cog(Restrictions(bot))
