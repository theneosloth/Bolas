import os
import logging
import discord

from discord import Game, ActivityType
from discord.ext import commands
from discord_slash import SlashCommand
from secret import BOLAS_SECRET_TOKEN

logging.basicConfig(level=logging.INFO)
token = BOLAS_SECRET_TOKEN

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description = "A magic the gathering card fetcher bot")
slash = SlashCommand(bot, sync_commands=True, sync_on_cog_reload=True)

@bot.event
async def on_ready():
    game = Game("/help (Use !addme again to update)")
    await bot.change_presence(status=ActivityType.playing,
                              activity = game) 

enabled_extensions = ['cog',
    				  'src.cogs.fetcher',
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
