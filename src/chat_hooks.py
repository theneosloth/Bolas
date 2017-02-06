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
    !image to get its image
    !flavor to get its flavor text
    !price to get its price in usd
    !tix to get its price in tix

    !card 'property' (without quotes) to get a specific property of the card.
    Some examples: usd, tix, set, rarity.
    Full list: https://scryfall.com/docs/api-overview

    """

    def __init__(self):
        self.pattern = re.compile("\[\[([^\]]+)\]\]")
        self.sc = ScryFall()
        self._last_cards = {}
        self.MAX_CARDS = 10
        self.DETAILS_COMMAND = "!card"
        # Needs a space in front. This is a terrible hack that has to be fixed.
        self.COMMAND_SHORTCUTS = {"!image": "image_uri",
                                  "!flavor": "flavor_text",
                                  "!price": "usd",
                                  "!tix": "tix"
                                  }

    def get_details(self, attr, server_id):
        if server_id not in self._last_cards:
            return "Please find a card first"
        else:
            if attr:
                return self._last_cards[server_id].__getattr__(attr)
            else:
                return "**{0}(Details): **"\
                    "\nArtist:{1},\nPrinting:{2},\nRarity: {3}\n".format(
                        self._last_cards[server_id].name,
                        self._last_cards[server_id].artist,
                        self._last_cards[server_id].set_name,
                        self._last_cards[server_id].rarity.capitalize())

    def func(self, msg, server_id):
        command = msg.split(" ")[0]
        attr = msg.split(" ")[1] if len(msg.split(" ")) > 1 else " "

        if msg.startswith(self.DETAILS_COMMAND):
            return self.get_details(attr, server_id)

        # Aliases
        elif command in self.COMMAND_SHORTCUTS:
            return self.get_details(
                self.COMMAND_SHORTCUTS[command],
                server_id)

        result = []
        for match in re.findall(self.pattern, msg):

            if ("KANYE" in match.upper()):
                return str(self.sc.search_card("Teferi, Temporal Archmage")[0])

            cards = self.sc.search_card(match)
            if len(cards) < self.MAX_CARDS:
                result += [card for card in cards]
            else:
                return "Too many matches. Try being more specific."

        if (len(result)) > 0:
            self._last_cards[server_id] = result[0]
        else:
            return "No cards found."

        return "".join(str(x) for x in result)
