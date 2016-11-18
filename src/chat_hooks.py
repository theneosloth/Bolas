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

!card 'property' (without quotes) to get a specific property of the card.
Some examples: usd, tix, set, rarity.
Full list: https://scryfall.com/docs/api-overview

    """

    def __init__(self):
        self.pattern = re.compile("\[\[([^\]]+)\]\]")
        self.sc = ScryFall()
        self._last_cards = {}
        self.MAX_CARDS = 5
        self.DETAILS_COMMAND = "!card"
        # Needs a space in front. This is a terrible hack that has to be fixed.
        self.COMMAND_SHORTCUTS = {"!image": " image_uri",
                                  "!flavor": " flavor_text",
                                  }

    def get_details(self, msg, server_id):
        if server_id not in self._last_cards:
            return "Please find a card first"
        else:
            msg = msg.split(" ")
            if len(msg) > 1:
                return self._last_cards[server_id].__getattr__(msg[1])

            else:
                return "**{0}(Details): **"\
                    "\nArtist:{1},\nPrinting:{2},\nRarity: {3}\n".format(
                        self._last_cards[server_id].name,
                        self._last_cards[server_id].artist,
                        self._last_cards[server_id].set_name,
                        self._last_cards[server_id].rarity)

    def func(self, msg, server_id):
        if msg.startswith(self.DETAILS_COMMAND):
            return self.get_details(msg, server_id)

        # Aliases
        elif msg.split(" ")[0] in self.COMMAND_SHORTCUTS:
            # Temporary hack
            return self.get_details(
                self.COMMAND_SHORTCUTS[msg.split(" ")[0]],
                server_id)

        result = []
        for match in re.findall(self.pattern, msg):
            cards = self.sc.search_card(match)
            if len(cards) < self.MAX_CARDS:
                result += [card for card in cards]
            else:
                return "The incantations are too long. Try being more specific"

        if (len(result)) > 0:
            self._last_cards[server_id] = result[0]

        return "".join(str(x) for x in result)
