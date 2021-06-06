import os
import logging

from discord import Game, ActivityType
from discord.ext import commands
from secret import BOLAS_SECRET_TOKEN

logging.basicConfig(level=logging.INFO)
token = os.environ['BOLAS_SECRET_TOKEN']

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description = "A magic the gathering card fetcher bot")

@bot.event
async def on_ready():
    game = Game("!help")
    await bot.change_presence(status=ActivityType.playing,
                              activity = game)

enabled_extensions = ['src.cogs.fetcher',
                      'src.cogs.commands',
                      'src.cogs.deckdiff',
                      'src.cogs.discord_cleaner',
                      'src.cogs.rule']

for extension in enabled_extensions:
    try:
        bot.load_extension(extension)
    except commands.errors.ExtensionNotFound:
        logging.error(f"{extension} extension could not be loaded.")

bot.run(token,reconnect=True)
