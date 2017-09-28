import re
import asyncio

from urllib.parse import quote

from .plugin_mount import PluginMount

from .scryfall import ScryFall


class HookPlugin(metaclass=PluginMount):
    """
    """

    def func(self):
        raise NotImplementedError("Please implement this method.")

    def __init__(self):
        raise NotImplementedError("Please implement a command.")


class CardFetcher(HookPlugin):

    def __init__(self):
        self.pattern = re.compile("\[\[([^\]]+)\]\]")
        self.sc = ScryFall()
        self._cards = {}
        self.MAX_CARDS = 9
        self.MAX_CARDS_BEFORE_LIST = 5
        self.DETAILS_COMMAND = "!card"
        self.COMMAND_SHORTCUTS = {"!image": "image_uri",
                                  "!flavor": "flavor_text",
                                  "!price": "usd",
                                  "!tix": "tix",
                                  "!details": "",
                                  "!scryfall": "scryfall_uri",
                                  "!buy": "purchase_uris",
                                  "!legality": "legalities",
                                  "!reserved": "reserved"
                                  }
        self.helpstring = """

        Card Fetcher documentation:

        [[Card Name]] to get a card.
        The fetcher supports the scryfall/magiccards.info syntax, so a query like [[t:goblin t:instant]] will return a goblin instant (tarfire)
        !image to get its image
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

    def get_details(self, attr, server_id):
        """
        Returns a string containing the requested card attribute
        """
        if server_id not in self._cards:
            return "Please find a card first."
        else:
            try:
                # Return the attribute if it exists on the card
                if attr and attr in self._cards[server_id]:
                    return "{0} -- {1}".format(
                        self._cards[server_id].__getattr__(attr),
                        self._cards[server_id].name
                    )
                elif attr.strip() == "":
                    return "**{0} (Details): **"\
                        "\nArtist:{1},\nPrinting:{2},\nRarity: {3}\n".format(
                            self._cards[server_id].name,
                            self._cards[server_id].artist,
                            self._cards[server_id].set_name,
                            self._cards[server_id].rarity.capitalize())
                else:
                    return "No such attribute."
            except AttributeError:
                return "No such attribute."

    def func(self, parent, message):
        msg = message.content

        try:
            server_id = message.server.id
        except AttributeError:
            # If this is a PM, store the card with the individual user id
            server_id = message.author.id

        command = msg.split(" ")[0]
        attr = msg.split(" ")[1] if len(msg.split(" ")) > 1 else " "

        result = []
        for match in re.findall(self.pattern, msg):

            # Make sure we prioritize paper cards
            match += " not:online"

            # lil meme
            if ("KANYE" in match.upper()):
                return str(self.sc.search_card("Teferi, Temporal Archmage")[0])

            try:
                cards = self.sc.search_card(match)
            # TODO: Proper Exception handling
            except Exception:
                return "Scryfall appears to be down. No cards can be found."

            if len(cards) == 0:
                result.append("**{0}** not found.\n\n".format(match))
            elif len(cards) < self.MAX_CARDS_BEFORE_LIST:
                result += cards
            elif len(cards) < self.MAX_CARDS:
                # Return titles and mana costs if there are too many results to
                # display details
                return "".join(
                    "**{0}** {1}\n".format(card.name, card.mana_cost)
                    for card in cards)
            else:
                url = "https://scryfall.com/search?q={}".format(quote(match))
                return "Too many matches. Try being more specific. You can see the full list of matched cards here: {}".format(url)

        if (len(result)) > 0:
            # Store the last card found
            self._cards[server_id] = result[0]

        # If the message starts with !card return the attribute requested
        if msg.startswith(self.DETAILS_COMMAND):
            return self.get_details(attr, server_id)

        # Aliases
        elif command in self.COMMAND_SHORTCUTS:
            return self.get_details(
                self.COMMAND_SHORTCUTS[command],
                server_id)

        return [str(x) for x in result]


class ChannelCleaner(HookPlugin):
    def __init__(self):
        self.whitelist = {
            #EDH Discord server. Remove all non link posts from #decklists
            "144547963484635137":(["decklists"], re.compile(".*http(s)*:\/\/.*")),
            "189194499333947392":(["shhh"], re.compile(".*http(s)*:\/\/.*"))
        }
        self.helpstring = ""

    def func(self, parent, message):

        #Terminate execution when in PMs
        if (message.server is None):
            return

        # Stop the function if the channel is not checked or if the channel doesnt exist
        if (message.server.id not in self.whitelist) or (
                (message.channel is None) or (message.channel.name not in self.whitelist[message.server.id][0])):
            return

        client_member = message.server.get_member(parent.user.id)
        if not message.channel.permissions_for(client_member).manage_messages:
            return

        if (self.whitelist[message.server.id][1].match(message.content)) is None:
            asyncio.ensure_future(
                parent.delete_message(message))
