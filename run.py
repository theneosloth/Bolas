import os

from src import bot

token = os.environ['BOLAS_SECRET_TOKEN']
bot = bot.Bolas(token)
bot.run(bot.token)
