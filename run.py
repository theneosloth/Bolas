from src import bot

token = ""
with open("secret_token.txt") as f:
    token = f.read()

bot = bot.Bolas(token)
bot.run(bot.token)
