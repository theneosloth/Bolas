import asyncio
import json
import re
import os.path
import requests
import random
import urllib.request as request

from discord import Embed, File
from discord.ext import commands
from urllib.parse import quote, quote_plus
from urllib.error import HTTPError

class Tokens(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pattern = re.compile("\[\[((?:[^\]]|\][^\]])+)\]\]")
        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.DIRECTORY = os.path.realpath(os.path.join(
            self.ROOT_DIR, "../../misc/"
        ))
        self.MAX_CARDS = 8
        self.MAX_CARDS_BEFORE_LIST = 4
        self.SPECIAL_TOKENS = ["city's blessing",
                               "copy",
                               "emblem",
                               "experience counter",
                               "investigate",
                               "monarch",
                               "token",
                               "venture into the dungeon",
                               "{A}",
                               "{E}"]
        # Need to be all lowercase
        
    async def get_tokens(self, ctx, deck, token_array = []):
        "Return tokens of an Archidekt list."
        tokens = ["city's blessing", 
                  "copy",
                  "emblem",
                  "experience counter",
                  "investigate",
                  "monarch",
                  "token",
                  "venture into the dungeon",
                  "{A}",
                  "{E}"]
        
        categories_array = []
        scryfall_search = ""
        for category in deck['categories']:
            if category['includedInDeck']:
                categories_array.append(category['name'])
        for card in deck['cards']:
            if any(x in card['categories'] for x in categories_array):
                if card['card']['oracleCard']['faces']:
                    for face in card['card']['oracleCard']['faces']:
                        card['card']['oracleCard']['text']+= face['text'] + " ";
                if any(x in card['card']['oracleCard']['text'] for x in tokens):
                    if "city's blessing" in card['card']['oracleCard']['text']:
                        if "City's Blessing" not in token_array:
                            token_array.append("City's Blessing")
                    if re.search(r'(token that.+ copy)',card['card']['oracleCard']['text']):
                        if "Copy" not in token_array:
                            token_array.append("Copy")
                    if "daybound" in card['card']['oracleCard']['text'] or "becomes day" in card['card']['oracleCard']['text'] or "becomes night" in card['card']['oracleCard']['text']:
                        if "Day Night" not in token_array:
                            token_array.append("Day Night")
                    if "emblem" in card['card']['oracleCard']['text']:
                        regex = r'(emblem with .+\.(\')*")'
                        emblem_results = re.findall(regex,card['card']['oracleCard']['text'])
                        for emblem in emblem_results:                        
                            if emblem[0].replace('emblem', 'Emblem') + " (" + card['card']['oracleCard']['name'] + ")" not in token_array:
                                token_array.append(emblem[0].replace('emblem', 'Emblem') + " (" + card['card']['oracleCard']['name'] + ")")                        
                    if "experience counter" in card['card']['oracleCard']['text']:
                        if "Experience" not in token_array:
                            token_array.append("Experience")
                    if "investigate" in card['card']['oracleCard']['text']:
                        if "Clue token" not in token_array:
                            token_array.append("Clue token")
                    if "monarch" in card['card']['oracleCard']['text']:
                        if "The Monarch" not in token_array:
                            token_array.append("The Monarch")
                    if "token" in card['card']['oracleCard']['text']:
                        regex = r'((([0-9XYZ]+\/[0-9XYZ]+|(?<=\ba\b (?<=\ba\b \btapped\b (?!.+(\ba\b|:))(?!(number of)* [0-9XYZ]+\/[0-9XYZ]+))))[^\,\.]+){0,1}((?<!(?:\bClue \b))artifact|creature|enchantment|land|planeswalker|\b(?!\bCreature\b)[A-Z][a-z]+\b) token[s]*( named[^\,\.]+){0,1}( with[^\,\.]+(each|power) equal[^\,\.]+(\.")*| with([^\,\.]+(?= equal))| with([^\,\.]+?(?= that))| with[^\.]+(\.(\'|"))+| with[^\,\.]+(?= are created)| with[^\,\.]+(?= instead)| with[^\,\.]+(?= for)| with[^\,\.]+){0,1}(\. (It[s]* (has|power)|The token) [^\.]+\.(\'|")*){0,1})'
                        token_results = re.findall(regex,card['card']['oracleCard']['text'])
                        for token in token_results:
                            tmp_token = token[0].replace("tokens", "token").replace("'",'"')
                            if tmp_token not in token_array and not tmp_token == 'creature token':
                                token_array.append(tmp_token)
                    if "venture into the dungeon" in card['card']['oracleCard']['text']:
                        if "Dungeons (Dungeon of the Mad Mage, Lost Mine of Phandelver, Tomb of Annihilation)" not in token_array:
                            token_array.append("Dungeons (Dungeon of the Mad Mage, Lost Mine of Phandelver, Tomb of Annihilation)")
                    if "{A}" in card['card']['oracleCard']['text']:
                        if "Acorn Stash" not in token_array:
                            token_array.append("Acorn Stash")
                    if "{E}" in card['card']['oracleCard']['text']:
                        if "Energy Reserve" not in token_array:
                            token_array.append("Energy Reserve")
        return token_array

async def setup(bot):
    await bot.add_cog(Tokens(bot))