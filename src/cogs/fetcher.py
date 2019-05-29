import asyncio
import re

from discord.ext import commands
from urllib.parse import quote

from ..lib.scryfall import ScryFall

class Fetcher(commands.Cog):
    """
        [[Card Name]] to get a card.
        The fetcher supports the scryfall/magiccards.info syntax, so a query like [[t:goblin t:instant]] will return a goblin instant (tarfire)
        To use the commands put the card name right after the command like so: '!art goblin welder'
    """

    def __init__(self, bot):
        self.bot = bot
        self.pattern = re.compile("\[\[((?:[^\]]|\][^\]])+)\]\]")
        self.sc = ScryFall()
        self.MAX_CARDS = 8
        self.MAX_CARDS_BEFORE_LIST= 4
        # Need to be all lowercase
        self.CARD_NICKNAMES ={"sad robot" : "Solemn Simulacrum",
                              "bob": "Dark Confidant",
                              "steve": "Sakura-Tribe Elder",
                              "scooze": "Scavenging Ooze",
                              "gary": "Gray Merchant of Asphodel",
                              "tim": "Prodigal Sorcerer",
                              "prime time": "Primeval Titan",
                              "skittles": "Skithiryx, the Blight Dragon",
                              "gaaiv": "Grand Arbiter Augustin IV"
        }


    @commands.Cog.listener("on_message")
    async def card_fetch(self, message):
        if message.author.id == self.bot.user.id:
               return

        msg = message.content
        channel = message.channel

        for match in re.findall(self.pattern, msg):
            if match.lower() in self.CARD_NICKNAMES:
                match = self.CARD_NICKNAMES[match.lower()]

            await asyncio.sleep(0.05)
            try:
                cards = self.sc.search_card(match, self.MAX_CARDS)
            # In hindsight giving this an exception is dumb
            except ScryFall.CardLimitException as e:
                url = "https://scryfall.com/search?q={}".format(quote(match))
                await channel.send(f"Too many matches. You can see the full list of matched cards here: {url}")
                return
            # Any generic exception provided by scryfall
            except ScryFall.ScryfallException as e:
                await channel.send(e.message())
                return

            card_count = len(cards)
            if not card_count:
                await channel.send("No cards found.")
            elif card_count < self.MAX_CARDS_BEFORE_LIST:
                for card in cards:
                    await channel.send(embed=card.format_embed())
            else:
                # Return titles and mana costs if there are too many results to
                # display details
                cardlist = "".join(
                    "**{}** {}\n".format(card.name, card.mana_cost)
                    for card in cards)
                await channel.send(cardlist)


    async def _post_card_attribute(self, ctx, cardname, attr):
        # Send a card attribute or the associated exception message
        try:
            card = self.sc.card_named(cardname)
            # Any generic exception provided by scryfall
        except ScryFall.ScryfallException as e:
            await ctx.send(e.message)
            return

        if card and attr in card:
            await ctx.send(card[attr])
        else:
            await ctx.send("Not found.")



    @commands.command()
    async def art(self, ctx, *, arg):
        "Return the art of a given card."
        await self._post_card_attribute(ctx, arg, "image_art_crop")


    @commands.command()
    async def image(self, ctx, *, arg):
        "Return the image of a given card."
        await self._post_card_attribute(ctx, arg, "image_normal")

    @commands.command()
    async def flavor(self, ctx, *, arg):
        "Return the flavor text of a given card."
        await self._post_card_attribute(ctx, arg, "flavor_text")

    @commands.command()
    async def reserved(self, ctx, *, arg):
        "Return whether the given card is reserved."
        await self._post_card_attribute(ctx, arg, "reserved")

    @commands.command()
    async def price(self, ctx, *, arg):
        "Return the price of a given card"
        # Send a card attribute or the associated exception message
        try:
            card = self.sc.card_named(arg)
            # Any generic exception provided by scryfall
        except ScryFall.ScryfallException as e:
            await ctx.send(e.message)
            return

        await ctx.send(card.get_price_string())
