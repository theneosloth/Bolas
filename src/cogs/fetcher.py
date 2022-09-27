import asyncio
import json
import re
import random
import os.path
import urllib.request as request
import urllib.parse
import pytz

from discord import Embed, File
from discord.ext import commands, tasks
from urllib.parse import quote, quote_plus
from urllib.error import HTTPError
from datetime import datetime, timedelta

from ..scryfall import ScryFall
from .archidekt import Archidekt
from .commands import Misc
#from .spoilers import Spoilers


class Fetcher(commands.Cog):
    """
        [[Card Name]] to get a card.
        The fetcher supports the scryfall/magiccards.info syntax, so a query like [[t:goblin t:instant]] will return a goblin instant (tarfire)
        To use the commands put the card name right after the command like so: '!art goblin welder'
    """

    def __init__(self, bot):
        self.bot = bot
        #self.task_start = datetime.now()
        # self.get_product_news.start()
        self.pattern = re.compile("\[\[((?:[^\]]|\][^\]])+)\]\]")
        self.sc = ScryFall()
        self.ctx = Misc(bot)
        #self.news = Spoilers(bot)
        self.archidekt = Archidekt(bot)
        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.DIRECTORY = os.path.realpath(os.path.join(
            self.ROOT_DIR, "../../misc/"
        ))
        self.MAX_CARDS = 8
        self.MAX_CARDS_BEFORE_LIST = 4
        # Need to be all lowercase
        self.CARD_NICKNAMES = {"sad robot": "Solemn Simulacrum set:mrd",
                               "bob": "Dark Confidant set:rav",
                               "steve": "Sakura-Tribe Elder",
                               "scooze": "Scavenging Ooze",
                               "gary": "Gray Merchant of Asphodel",
                               "tim": "Prodigal Sorcerer set:lea",
                               "prime time": "Primeval Titan",
                               "skittles": "Skithiryx, the Blight Dragon",
                               "gaaiv": "Grand Arbiter Augustin IV",
                               "magus of the cradle": "Circle of Dreams Druid",
                               "twd": "Walking Dead",
                               "streve": "Strefan, Maurer Progenitor",
                               "ayaya": "Ayara, First of Locthwain",
                               "magus of the crucible": "Ramunap Excavator",
                               "drop of honey, but white": "Porphyry Nodes",
                               "perry": "Perrie, the Pulverizer",
                               "perry, the platypus": "Perrie, the Pulverizer",
                               }

    @commands.Cog.listener("on_message")
    async def card_fetch(self, message):
        if message.author.id == self.bot.user.id:
            return

        ctx = await self.bot.get_context(message)

        # dt = datetime.now()
        # ts = self.news.task_start + timedelta(minutes=2)

        # if dt < ts:
        #     self.news.task_start = ts
        #     self.news.news_cycle.restart()

        archidekt_check = re.search(
            r"https:\/\/archidekt.com\/decks\/[0-9]+", ctx.message.content)

        if archidekt_check:
            og_url, embed = await self.archidekt.embed_link(ctx, archidekt_check[0])
            await self.ctx.send(ctx, embed=embed)
            return

        hello_check = re.search(
            r"^([H|h]ello|[H|h]i) ([E|e]mmy|[E|e]mrakul)", ctx.message.content)

        if hello_check:
            await self.ctx.send(ctx, "Hewwo. owo")
            return

        thx_check = re.search(
            r"^([T|t]hank[s]*|[T|t]hx) ([E|e]mmy|[E|e]mrakul)", ctx.message.content)

        if thx_check:
            await self.ctx.send(ctx, "You're welcome. <3")
            return

        if len(re.findall(self.pattern, ctx.message.content)) > self.MAX_CARDS_BEFORE_LIST:
            await self.ctx.send(ctx, "**>:(** Too many queries in one message.")
            return

        alchemy = False

        for match in re.findall(self.pattern, ctx.message.content):

            cards = []
            if match[0] == "@":
                alchemy = True

            if match[0] == "$":
                await self.price(ctx, arg=match[1:])
                return

            if match[0] == "?":
                await self.rulings(ctx, arg=match[1:])
                return

            if match[0] == "#":
                await self.legality(ctx, arg=match[1:])
                return

            if len(match) < 3 and not match.lower() == 'x':
                await self.ctx.send(ctx, "Query too short ~~for me~~ *flips tentacles*")
                continue

            if match.lower() == "pot of greed":
                pog_choice = random.choices(
                    population=["Normal Spell\nDraw 2 cards.", "Normal Spell\nPot of Greed can be activated during your Main Phase, when the chain is empty and you have priority. If it resolves, meaning neither the activation nor the effect have been negated, you may take the top two cards of your deck, and add them to the hidden cards in your hand. Neither you nor your opponent may look at the cards until they're added to your hand, and when they're added to your hand, only my may look at those cards. If you resolve this card, but the amount of cards in your deck is less than 2, you will lose the game because you can't draw cards when forced to do so. If an effect would prevent you from drawing or adding cards to your hand before you resolve this effect, you cannot resolve this effect. If an effect would prevent you from drawing or adding cards to your hand before you activate this card, you cannot activate this card. After this card resolves, even if it was negated, or the effect couldn't resolve, send the card to your GY. If activated, this card cannot be moved anywhere except to your GY or be banished. Any effect that would target a card to send it anywhere else, cannot target this card when resolving. Any effect that would send this card anywhere else, cannot be activated if this is the only card it could send. Any effect that would send this card anywhere else when resolving, doesn't send it anywhere else."],
                    weights=[0.95, 0.05],
                    k=1
                )
                pog_embed = Embed(title="Pot of Greed",
                                  url="https://www.db.yugioh-card.com/yugiohdb/card_search.action?ope=2&cid=4844",
                                  description=pog_choice[0],
                                  color=0xC2D6BF)
                pog_embed.set_thumbnail(
                    url="https://ms.yugipedia.com//1/1d/PotofGreed-LOB-NA-R-1E.jpg")
                await self.ctx.send(ctx, embed=pog_embed)
                continue

            # Convert card nicknames to their full names
            if match.lower() in self.CARD_NICKNAMES:
                match = self.CARD_NICKNAMES[match.lower()]

            await asyncio.sleep(0.05)
            # Try to get an exact match first
            try:
                # ! is the scryfall syntax for exact matches. The card
                # name has to be quoted
                cards = self.sc.search_card(f"!'{match}'",
                                            max_cards=self.MAX_CARDS)
            # If a match was not made for some reason just try again
            except ScryFall.ScryfallException:
                pass
            if not cards:
                # If no Scryfall Syntax, try to get a commander
                if not ":" in match:
                    try:
                        # ! is the scryfall syntax for exact matches. The card
                        # name has to be quoted
                        cards = self.sc.search_card(f"'{match}' is:commander",
                                                    max_cards=self.MAX_CARDS_BEFORE_LIST)

                        tmp_cards = []
                        if hasattr(cards, 'name'):
                            if match.lower() in re.split(', | ', cards.name.lower()):
                                tmp_cards.append(cards)
                        else:
                            for card in cards:
                                if match.lower() in re.split(', | ', card.name.lower()):
                                    tmp_cards.append(card)

                        cards = tmp_cards
                    # If a match was not made for some reason just try again
                    except ScryFall.CardLimitException:
                        pass
                    except ScryFall.ScryfallException:
                        pass
                if not cards:
                    try:
                        cards = self.sc.search_card(match,
                                                    max_cards=self.MAX_CARDS,
                                                    alchemy=alchemy)
                    # In hindsight giving this an exception is dumb
                    except ScryFall.CardLimitException as e:
                        url = "https://scryfall.com/search?q={}".format(
                            quote_plus(match))
                        await self.ctx.send(ctx, f"**OwO so big** list of cards. You can see the full list of matched cards here: {url}")
                        continue
                    # Any generic exception provided by scryfall
                    except ScryFall.ScryfallException as e:
                        await self.ctx.send(ctx, "**uwu sowwy.** {}".format(e.message), delete_after=5)
                        continue

            card_count = len(cards)
            if not card_count:
                await self.ctx.send(ctx, "**>.<** No cards found.", delete_after=5)
            elif card_count < self.MAX_CARDS_BEFORE_LIST:
                for card in cards:
                    await self.ctx.send(ctx, embed=card.format_embed())
            else:
                # Return titles and mana costs if there are too many results to
                # display details
                url = "**owo omg** so many matched cards here: https://scryfall.com/search?q={}\n".format(
                    quote_plus(match))
                cardlist = "".join(
                    "**{}** {}\n".format(card.name, card.mana_cost)
                    for card in cards)
                cardlist = url + cardlist
                await self.ctx.send(ctx, cardlist)

    async def _post_card_attribute(self, ctx, cardname, attr):
        # Send a card attribute or the associated exception message
        if not cardname:
            await self.ctx.send(ctx, "Please provide a card name after the command.", delete_after=5)
            return
        try:
            cardname = cardname.strip("[]")
            cards = self.sc.search_card(cardname, max_cards=1)
            # Any generic exception provided by scryfall
        except ScryFall.ScryfallException as e:
            await self.ctx.send(ctx, e.message, delete_after=5)
            return
        except ScryFall.CardLimitException:
            await self.ctx.send(ctx, "Only one card per command please.", delete_after=5)
            return

        if(len(cards) > 1):
            for tmp in cards:
                if cardname.lower() in tmp["name"].lower():
                    card = tmp
        if not 'card' in locals():
            card = cards[0]
        if card and attr in card:
            await self.ctx.send(ctx, card[attr])
        else:
            await self.ctx.send(ctx, "Not found.", delete_after=5)    

    @commands.command()
    async def art(self, ctx, *, arg=None):
        "Return the art of a given card."
        await self._post_card_attribute(ctx, arg, "image_art_crop")

    @commands.command()
    async def image(self, ctx, *, arg=None):
        "Return the image of a given card."
        await self._post_card_attribute(ctx, arg, "image_normal")

    @commands.command()
    async def flavor(self, ctx, *, arg=None):
        "Return the flavor text of a given card."
        await self._post_card_attribute(ctx, arg, "flavor_text")

    @commands.command()
    async def reserved(self, ctx, *, arg=None):
        "Return whether the given card is reserved."
        await self._post_card_attribute(ctx, arg, "reserved")

    @commands.command()
    async def price(self, ctx, *, arg=None):
        "Return the price of a given card."
        if not arg:
            await self.ctx.send(ctx, "Please provide a card name after the command.", delete_after=5)
            return

        # Send a card attribute or the associated exception message
        try:
            card = self.sc.search_card(arg, order="usd", max_cards=1)[0]

            # Any generic exception provided by scryfall
        except ScryFall.ScryfallException as e:
            await self.ctx.send(ctx, e.message, delete_after=5)
            return
        except ScryFall.CardLimitException as e:
            await self.ctx.send(ctx, e.message, delete_after=5)
            return

        await self.ctx.send(ctx, card.get_price_string())

    @commands.command()
    async def rulings(self, ctx, *, arg=None):
        "Show all the rulings for a given card."
        if not arg:
            await self.ctx.send(ctx, "Please provide a card name after the command.", delete_after=5)
            return

        try:
            card = self.sc.card_named(arg)
            rulings = self.sc.get_card_rulings(card.id)
        except ScryFall.ScryfallException as e:
            await self.ctx.send(ctx, e.message)
            return

        if not rulings:
            await self.ctx.send(ctx, "No rulings found")
            return

        # String where every line is a bold publish date followed by
        # the comment
        description = "\n\n".join(
            [f'**{r["published_at"]}** {r["comment"]}' for r in rulings])

        # This embed could definitely be prettier
        await self.ctx.send(ctx, embed=Embed(title=card.name, description=description))

    @commands.command()
    async def legality(self, ctx, *, arg=None):
        "Return the legality of a given card."
        if not arg:
            await self.ctx.send(ctx, "Please provide a card name after the command.", delete_after=5)
            return

        # Send a card attribute or the associated exception message
        try:
            card = self.sc.search_card(arg, max_cards=1)[0]

            # Any generic exception provided by scryfall
        except ScryFall.ScryfallException as e:
            await self.ctx.send(ctx, e.message, delete_after=5)
            return
        except ScryFall.CardLimitException as e:
            await self.ctx.send(ctx, e.message, delete_after=5)
            return

        await self.ctx.send(ctx, card.get_legality_string())

    @commands.command()
    async def cute(self, ctx):
        "Return the art of a cute card."
        cute_choice = random.choices(
            population=["art:eldrazi", "art:emrakul",
                        "art:kozilek", "art:ulamog"]
        )
        card = self.sc.card_random(cute_choice[0])
        print(card['name'])
        await self._post_card_attribute(ctx, '!"{}" -t:token -layout:art_series -t:card \(-banned:vintage or t:conspiracy or o:ante or o:"one foot" or Shahrazad\)'.format(card['name']), "image_art_crop")

    @commands.command()
    async def random(self, ctx, *, arg="-t:card \(-banned:vintage or t:conspiracy or o:ante or o:'one foot' or Shahrazad\)"):
        "Return the image of a given card at random."
        count = self.sc.get_count(arg)
        await self.ctx.send(ctx, "Random chance of 1:{}".format(count))
        card = self.sc.card_random(arg)
        await self._post_card_attribute(ctx, '!"{}" -t:token -layout:art_series -t:card \(-banned:vintage or t:conspiracy or o:ante or o:"one foot" or Shahrazad\)'.format(card['name']), "image_normal")


async def setup(bot):
    await bot.add_cog(Fetcher(bot))
