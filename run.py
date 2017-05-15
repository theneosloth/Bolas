from src import bot

token = ""
with open("secret_token") as f:
    token = f.read().strip()
bot = bot.Bolas(token)
bot.run(bot.token)
