import os
import logging

from src import bot

logging.basicConfig(level=logging.INFO)
token = os.environ['BOLAS_SECRET_TOKEN']

bot = bot.Bolas()
bot.run(token,reconnect=True)
