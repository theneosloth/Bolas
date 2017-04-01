import re

from .plugin_mount import PluginMount

from .scryfall import ScryFall


class HookPlugin(metaclass=PluginMount):
    """
    """

    def func(self):
        raise NotImplementedError("Please implement this method")

    def __init__(self):
        raise NotImplementedError("Please implement a command")


class CardFetcher(HookPlugin):
    """

    Card Fetcher documentation:

    [[Card Name]] to get a card.
    The fetcher supports the scryfall syntax, so a query like [[t:goblin t:instant]] will return a goblin instant (tarfire)
    !image to get its image
    !flavor to get its flavor text
    !price to get its price in usd
    !tix to get its price in tix
    !details to get an overview of the card
    !scryfall to get its scryfall page
    !buy to get the list of places you can buy it from
    !legality to get the list of formats where the card is legal
    !reserved to see whether the card is on the reserved list

    !card 'property' (without quotes) to get a specific property of the card.
    Some examples: usd, tix, set, rarity.
    Full list: https://scryfall.com/docs/api-overview


    """

    def __init__(self):
        self.pattern = re.compile("\[\[([^\]]+)\]\]")
        self.sc = ScryFall()
        self._last_cards = {}
        self.MAX_CARDS = 9
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

    def get_details(self, attr, server_id):
        if server_id not in self._last_cards:
            return "Please find a card first"
        else:
            try:
                # Return the attribute if it exists on the card
                if attr and attr in self._last_cards[server_id]:
                    return "{0} -- {1}".format(
                        self._last_cards[server_id].__getattr__(attr),
                        self._last_cards[server_id].name
                    )
                else:
                    return "**{0} (Details): **"\
                        "\nArtist:{1},\nPrinting:{2},\nRarity: {3}\n".format(
                            self._last_cards[server_id].name,
                            self._last_cards[server_id].artist,
                            self._last_cards[server_id].set_name,
                            self._last_cards[server_id].rarity.capitalize())
            except AttributeError:
                return "No such attribute."

    def func(self, msg, server_id):
        command = msg.split(" ")[0]
        attr = msg.split(" ")[1] if len(msg.split(" ")) > 1 else " "

        result = []
        for match in re.findall(self.pattern, msg):

            # lil meme
            if ("KANYE" in match.upper()):
                return str(self.sc.search_card("Teferi, Temporal Archmage")[0])

            cards = self.sc.search_card(match)
            if len(cards) < self.MAX_CARDS:
                result += [card for card in cards]
            else:
                return "Too many matches. Try being more specific."

        if (len(result)) > 0:
            self._last_cards[server_id] = result[0]

        # If the message starts with !card return the attribute requested
        if msg.startswith(self.DETAILS_COMMAND):
            return self.get_details(attr, server_id)

        # Aliases
        elif command in self.COMMAND_SHORTCUTS:
            return self.get_details(
                self.COMMAND_SHORTCUTS[command],
                server_id)

        if len(result) == 0:
            return "Card not found."
        return "".join(str(x) for x in result)
