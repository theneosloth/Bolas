import re
import asyncio

from urllib.parse import quote
from time import sleep

from .plugin_mount import PluginMount

from .scryfall import ScryFall
from .card import Card


class HookPlugin(metaclass=PluginMount):
    """
    """

    def func(self):
        raise NotImplementedError("Please implement this method.")

    def __init__(self):
        raise NotImplementedError("Please implement a command.")

    @property
    def name(self):
        return self._name

    @property
    def helpstring(self):
        return self._helpstring


class CardFetcher(HookPlugin):

    def __init__(self):
        # Captures text between [[ and ]] that contains one or more instances of
        # either a non-] character or ] followed by a non-] character.
        self.pattern = re.compile("\[\[((?:[^\]]|\][^\]])+)\]\]")
        self.sc = ScryFall()
        self._cards = {}
        self.MAX_CARDS = 9
        self.MAX_CARDS_BEFORE_LIST = 5
        self.DETAILS_COMMAND = "!card"
        self.COMMAND_SHORTCUTS = {"!image": "image_normal",
                                  "!art": "image_art_crop",
                                  "!flavor": "flavor_text",
                                  "!price": "price",
                                  "!details": "",
                                  "!scryfall": "scryfall_uri",
                                  "!buy": "purchase_uris",
                                  "!legality": "legalities",
                                  "!reserved": "reserved"
                                  }
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

        self._name = "Card Fetcher"

        self._helpstring = """

        Card Fetcher documentation:

        [[Card Name]] to get a card.
        The fetcher supports the scryfall/magiccards.info syntax, so a query like [[t:goblin t:instant]] will return a goblin instant (tarfire)
        !image to get its image
        !art to get the full art
        !flavor to get its flavor text
        !price to get its price in usd
        !tix to get its price in tix
        !details to get an overview of the card
        !scryfall to get its scryfall page
        !buy to get the list of places you can buy it from
        !legality to get the list of formats where the card is legal
        !reserved to see whether the card is on the reserved list

        The card query and a command can be in the same message, so "!image [[Goblin Welder]]" will return the image of goblin welder.

        !card 'property' (without quotes) to get a specific property of the card.
        Some examples: usd, tix, set, rarity.
        Full list: https://scryfall.com/docs/api-overview


        """

    def _format_dict(self, dict):
        """
        Converts a dict into a readable string.
        """

        result = ""
        for k, v in dict.items():
            result += "\n{0}: {1}".format(k.capitalize(), v)

        return result

    def get_details(self, attr, guild_id):
        """
        Returns a string containing the requested card attribute
        """
        if guild_id not in self._cards:
            return "Please find a card first."
        else:
            try:
                sleep(0.1)
                # Return the attribute if it exists on the card
                card = self.sc.search_card(self._cards[guild_id])[0]
                if attr == "price":
                    return self.get_price_string(card)
                elif (attr and attr in card) or (attr == "image"):

                    card_attr = card.__getattr__(attr)
                    if isinstance(card_attr, dict):
                        card_attr = self._format_dict(card_attr)
                    else:
                        card_attr = str(card_attr)

                    return "{0} -- {1}".format(
                        card_attr,
                        card.name
                    )
                elif attr.strip() == "":
                    return "**{0} (Details): **"\
                        "\nArtist:{1},\nPrinting:{2},\nRarity: {3}\n".format(
                            card.name,
                            card.artist,
                            card.set_name,
                            card.rarity.capitalize())
                else:
                    return "No such attribute."
            except AttributeError:
                return "No such attribute."

    def get_price_string(self, card):
        "Return a formatted string of a card's price"
        if "prices" in card:
            return "{} usd \n{} tix".format(card["prices"]["usd"],
                                      card["prices"]["tix"])
        else:
            return "Price not found."

    def func(self, parent, message):
        msg = message.content

        try:
            guild_id = message.guild.id
        except AttributeError:
            # If this is a PM, store the card with the individual user id
            guild_id = message.author.id

        command = msg.split(" ")[0]
        attr = msg.split(" ")[1] if len(msg.split(" ")) > 1 else " "

        result = []
        last_match = ""

        if len(re.findall(self.pattern, msg)) > self.MAX_CARDS_BEFORE_LIST:
            return "Too many queries in one message."

        for match in re.findall(self.pattern, msg):

            # Replace nicknames with the real card name
            if (match.lower() in self.CARD_NICKNAMES):
                match = self.CARD_NICKNAMES[match.lower()]

            # Make sure we prioritize paper cards
            #match += " not:online"

            # Store the last match for attribute commands

            try:
                cards = self.sc.search_card(match)
            # TODO: Proper Exception handling
            except Exception:
                import traceback
                print(traceback.format_exc())
                return "Scryfall appears to be down. No cards can be found."

            if len(cards) == 0:
                result.append("Card not found.")
            elif len(cards) < self.MAX_CARDS_BEFORE_LIST:
                result += cards
                last_match = match
            elif len(cards) < self.MAX_CARDS:
                # Return titles and mana costs if there are too many results to
                # display details
                return "".join(
                    "**{0}** {1}\n".format(card.name, card.mana_cost)
                    for card in cards)
            else:
                url = "https://scryfall.com/search?q={}".format(quote(match))
                return "Too many matches. Try being more specific. You can see the full list of matched cards here: {}".format(url)

        if len(result) > 0 and last_match:
            # Store the last card found
            self._cards[guild_id] = last_match

        # If the message starts with !card return the attribute requested
        if msg.startswith(self.DETAILS_COMMAND):
            return self.get_details(attr, guild_id)

        # Aliases
        elif command in self.COMMAND_SHORTCUTS:
            return self.get_details(
                self.COMMAND_SHORTCUTS[command],
                guild_id)

        return [x.format_embed() if isinstance(x, Card) else x for x in result]


class ChannelCleaner(HookPlugin):
    def __init__(self):
        # TODO: Stop hardcoding stuff in
        self.whitelist = {
            # EDH Discord server. Remove all non link posts from #decklists
            "144547963484635137": (["decklists"], re.compile(".*http(s)*:\/\/.*")),
            # PlayEDH
            "304276578005942272": (["decklists"], re.compile(".*http(s)*:\/\/.*")),
            # Dragon's server
            "334571063197302784 ": (["decklists"], re.compile(".*http(s)*:\/\/.*")),
            # Teferi server
            "278284235125686272": (["decklists"], re.compile(".*http(s)*:\/\/.*"))
        }

        self._name = "Channel Cleaner"
        self._helpstring = "Set up on a per server basis"

    def func(self, parent, message):

        # Terminate execution when in PMs
        if message.guild is None:
            return

        # Stop the function if the channel is not checked or if the channel doesn't exist
        if (message.guild.id not in self.whitelist) or (
                (message.channel is None) or (message.channel.name not in self.whitelist[message.guild.id][0])):
            return

        client_member = message.guild.get_member(parent.user.id)
        if not message.channel.permissions_for(client_member).manage_messages:
            return

        if (self.whitelist[message.guild.id][1].match(message.content)) is None:
            asyncio.ensure_future(
                parent.delete_message(message))
