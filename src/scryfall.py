import json

import urllib.request as request
import urllib.parse as parse

from .card import Card

class ScryFall:
    """
    A very barebone wrapper around the scryfall api.
    """

    def __init__(self):
        self.API_URL = "https://api.scryfall.com"

        # If set to true the wrapper will load every single match and not just
        # the first page of responses
        self.LOAD_ALL_MATCHES = False

    def _load_url_as_json(self, url):
        """
        Load a given url into a json object.
        """
        url = request.urlopen(url)
        return json.loads(url.read().decode("utf-8", "replace"))

    def search_card(self, query):
        """
        Search for a card by name.
        """
        url = self.API_URL + "/cards/search?q=" + parse.quote(query)
        result = self.get_cards_from_url(url)
        for card in result:
            # If we have an exact match and it's not a DFC or a flip card, return just one
            if card.name.lower() == query.lower() and (
                    ("all_parts" not in card) and (card.object != "card_face")):
                return [card]

        return result

    def get_cards_from_url(self, url):
        """
        Return all cards from a given url.
        """
        cards = []
        try:
            while True:
                j = self._load_url_as_json(url)
                data = j["data"]
                for x in data:
                    if "all_parts" in x:
                        # If the card has additional parts add them to the
                        # response
                        cards += [Card(self._load_url_as_json(part["uri"]))
                                  for part in x["all_parts"]]
                    elif "card_faces" in x:
                        cards += [Card(face)
                                  for face in x["card_faces"]]
                    else:
                        cards.append(Card(x))

                if self.LOAD_ALL_MATCHES and j["has_more"]:
                    url = j["next_page"]
                else:
                    break

        except IOError:
            pass

        return cards
