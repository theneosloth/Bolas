import os
import logging
import asyncio

from discord import Game, ActivityType, Intents
from discord.ext import commands
from secret import BOLAS_SECRET_TOKEN, DEV_ONLY

logging.basicConfig(level=logging.INFO)
token = BOLAS_SECRET_TOKEN

intents = Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description="A magic the gathering card fetcher bot",
    pm_help=True,
    intents=intents)

bot.dev_mode = DEV_ONLY


@bot.event
async def on_ready():
    game = Game("!help // !updates")
    await bot.change_presence(status=ActivityType.playing,
                              activity=game)


async def load_extensions():
    for filename in os.listdir("./src/cogs"):
        if filename.endswith(".py"):
            # cut off the .py from the file name
            await bot.load_extension(f"src.cogs.{filename[:-3]}")


async def main(token):
    async with bot:
        await load_extensions()
        await bot.start(token)

asyncio.run(main(token))
