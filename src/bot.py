import discord
import asyncio

from discord.ext import commands

from cogs.fetcher import Fetcher
from cogs.commands import Misc
from cogs.deckdiff import Diff
from cogs.rule import Rule
from cogs.discord_cleaner import Cleaner

class Bolas(commands.Bot):

    def __init__(self):
        """ Constructor for the  bot class.

        Args:
            token (str): the token for the discord bot.
        """
        super().__init__(command_prefix=commands.when_mentioned_or('!'))

        self.add_cog(Fetcher(self))
        self.add_cog(Misc(self))
        self.add_cog(Diff(self))
        self.add_cog(Rule(self))
        self.add_cog(Cleaner(self))
