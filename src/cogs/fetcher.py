import asyncio
import re
import requests
import random
import discord

import urllib.parse as parse

from discord import Embed
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from urllib.parse import quote, quote_plus

from ..scryfall import ScryFall

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
        self.MAX_CARDS_BEFORE_LIST = 4
        # Need to be all lowercase
        self.CARD_NICKNAMES = {"sad robot" : "Solemn Simulacrum set:mrd",
                              "bob": "Dark Confidant set:rav",
                              "steve": "Sakura-Tribe Elder",
                              "scooze": "Scavenging Ooze",
                              "gary": "Gray Merchant of Asphodel",
                              "tim": "Prodigal Sorcerer set:lea",
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

        if len(re.findall(self.pattern, msg)) > self.MAX_CARDS_BEFORE_LIST:
            await channel.send("Too many queries in one message.")
            return

        for match in re.findall(self.pattern, msg):

            cards = []

            if (len(match) < 3):
                await channel.send("Query too short")
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
                try:
                    cards = self.sc.search_card(match,
                                                max_cards=self.MAX_CARDS)
                    # In hindsight giving this an exception is dumb
                except ScryFall.CardLimitException as e:
                    url = "https://scryfall.com/search?q={}".format(quote_plus(match))
                    await channel.send(f"Too many matches. You can see the full list of matched cards here: {url}")
                    continue
                # Any generic exception provided by scryfall
                except ScryFall.ScryfallException as e:
                     await channel.send(e.message,delete_after=5)
                     continue

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
        if not cardname:
            await ctx.send("Please provide a card name after the command.")
            return
        try:
            cardname = cardname.strip("[]")
            cards = self.sc.search_card(cardname, max_cards=1)
            # Any generic exception provided by scryfall
        except ScryFall.ScryfallException as e:
            await ctx.send(e.message,delete_after=5)
            return
        except ScryFall.CardLimitException:
            await ctx.send("Only one card per command please.",delete_after=5)
            return

        card = cards[0]
        if card and attr in card:
            await ctx.send(card[attr])
        else:
            await ctx.send("Not found.",delete_after=5)
            
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
            await ctx.send("Please provide a card name after the command.")
            return

        # Send a card attribute or the associated exception message
        try:
            card = self.sc.search_card(arg, order="usd", max_cards=1)[0]

            # Any generic exception provided by scryfall
        except ScryFall.ScryfallException as e:
            await ctx.send(e.message, delete_after=5)
            return
        except ScryFall.CardLimitException as e:
            await ctx.send(e.message, delete_after=5)
            return

        await ctx.send(card.get_price_string())

    @commands.command()
    async def rulings(self, ctx, *, arg=None):
        "Show all the rulings for a given card."
        if not arg:
            await ctx.send("Please provide a card name after the command.")
            return

        try:
            card = self.sc.card_named(arg)
            rulings = self.sc.get_card_rulings(card.id)
        except ScryFall.ScryfallException as e:
            await ctx.send(e.message)
            return

        if not rulings:
            await ctx.send("No rulings found")
            return

        # String where every line is a bold publish date followed by
        # the comment
        description = "\n\n".join(
            [f'**{r["published_at"]}** {r["comment"]}' for r in rulings])

        # This embed could definitely be prettier
        await ctx.send(embed=Embed(title=card.name, description=description))
        
    @commands.command()
    async def cute(self, ctx):
        "Return the art of a cute card."
        cute_choice = random.choices(
            population=["art:cute or scute", "art:emrakul", "art:kozilek", "art:ulamog"],
            weights=[0.97, 0.01, 0.01, 0.01],
            k=1
        )
        card = self.sc.card_random(cute_choice[0])
        await self._post_card_attribute(ctx, '!"{}" include:extras'.format(card['name']), "image_art_crop")
        
    @commands.command()
    async def random(self, ctx, *, arg="-t:card \(-banned:vintage or t:conspiracy or o:ante or o:'one foot' or Shahrazad\)"):
        "Return the image of a given card at random."
        card = self.sc.card_random(arg)
        url = "{}/cards/search?q={}".format(self.sc.API_URL, parse.quote_plus(arg))
        j = self.sc._load_url_as_json(url)
        print(card['name'])
        await ctx.send(embed=Embed(title="Probability", description="1 in {}".format(j['total_cards'])),delete_after=5)
        await self._post_card_attribute(ctx, '!"{}" -t:token -layout:art_series -t:card \(-banned:vintage or t:conspiracy or o:ante or o:"one foot" or Shahrazad\)'.format(card['name']), "image_normal")
        
    @cog_ext.cog_slash(name="art",
                      description="Return the art of a given card.",
                      options=[
                          create_option(
                              name="arg",
                              description="Name of card. (e.g.: Gallia of the Endless Dance)",
                              option_type=3,
                              required=True
                          )
                      ])
    async def art(self, ctx, *, arg=None):        
        await self._post_card_attribute(ctx, arg, "image_art_crop")

    @cog_ext.cog_slash(name="image",
                      description="Return the image of a given card.",
                      options=[
                          create_option(
                              name="arg",
                              description="Name of card. (e.g.: Void Beckoner is:godzilla)",
                              option_type=3,
                              required=True
                          )
                      ])
    async def _image(self, ctx, *, arg=None):        
        await self._post_card_attribute(ctx, arg, "image_normal")

    @cog_ext.cog_slash(name="flavor",
                      description="Return the flavor text of a given card.",
                      options=[
                          create_option(
                              name="arg",
                              description="Name of card. (e.g.: Ancient Grudge set:isd)",
                              option_type=3,
                              required=True
                          )
                      ])
    async def _flavor(self, ctx, *, arg=None):        
        await self._post_card_attribute(ctx, arg, "flavor_text")

    @cog_ext.cog_slash(name="reserved",
                      description="Return whether the given card is reserved.",
                      options=[
                          create_option(
                              name="arg",
                              description="Name of card. (e.g.: Raging River)",
                              option_type=3,
                              required=True
                          )
                      ])
    async def _reserved(self, ctx, *, arg=None):
        await self._post_card_attribute(ctx, arg, "reserved")

    @cog_ext.cog_slash(name="price",
                      description="Return the price of a given card.",
                      options=[
                          create_option(
                              name="arg",
                              description="Name of card. (e.g.: Black Lotus set:lea)",
                              option_type=3,
                              required=True
                          )
                      ])
    async def _price(self, ctx, *, arg=None):        
        if not arg:
            await ctx.send("Please provide a card name after the command.")
            return

        # Send a card attribute or the associated exception message
        try:
            card = self.sc.search_card(arg, order="usd", max_cards=1)[0]

            # Any generic exception provided by scryfall
        except ScryFall.ScryfallException as e:
            await ctx.send(e.message, delete_after=5)
            return
        except ScryFall.CardLimitException as e:
            await ctx.send(e.message, delete_after=5)
            return

        await ctx.send(card.get_price_string())

    @cog_ext.cog_slash(name="rulings",
                      description="Show all the rulings for a given card.",
                      options=[
                          create_option(
                              name="arg",
                              description="Name of card. (e.g.: Panglacial Wurm)",
                              option_type=3,
                              required=True
                          )
                      ])
    async def _rulings(self, ctx, *, arg=None):        
        if not arg:
            await ctx.send("Please provide a card name after the command.")
            return

        try:
            card = self.sc.card_named(arg)
            rulings = self.sc.get_card_rulings(card.id)
        except ScryFall.ScryfallException as e:
            await ctx.send(e.message)
            return

        if not rulings:
            await ctx.send("No rulings found")
            return

        # String where every line is a bold publish date followed by
        # the comment
        description = "\n\n".join(
            [f'**{r["published_at"]}** {r["comment"]}' for r in rulings])

        # This embed could definitely be prettier
        await ctx.send(embed=Embed(title=card.name, description=description))
        
    @cog_ext.cog_slash(name="cute",
                       description="Return the art of a cute card.")
    async def _cute(self, ctx):        
        cute_choice = random.choices(
            population=["art:cute or scute", "art:emrakul", "art:kozilek", "art:ulamog"],
            weights=[0.97, 0.01, 0.01, 0.01],
            k=1
        )
        card = self.sc.card_random(cute_choice[0])
        await self._post_card_attribute(ctx, '!"{}" include:extras'.format(card['name']), "image_art_crop")
        
    @cog_ext.cog_slash(name="random",
                      description="Return the image of a given card at random.",
                      options=[
                          create_option(
                              name="arg",
                              description="Group of cards. \(e.g.: is:commander\)",
                              option_type=3,
                              required=False
                          )
                      ])
    async def _random(self, ctx, *, arg="-t:card \(-banned:vintage or t:conspiracy or o:ante or o:'one foot' or Shahrazad\)"):
        "Return the image of a given card at random."
        card = self.sc.card_random(arg)
        url = "{}/cards/search?q={}".format(self.sc.API_URL, parse.quote_plus(arg))
        j = self.sc._load_url_as_json(url)
        await self._post_card_attribute(ctx, '!"{}" -t:token -layout:art_series -t:card \(-banned:vintage or t:conspiracy or o:ante or o:"one foot" or Shahrazad\)'.format(card['name']), "image_normal")
        await ctx.send(embed=Embed(title="Probability", description="1 in {}".format(j['total_cards'])),delete_after=5)

def setup(bot):
    bot.add_cog(Fetcher(bot))
