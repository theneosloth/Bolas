# _*_ coding:utf-8 _*_

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
            if card.name.lower() == query.lower():
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
                    else:
                        cards.append(Card(x))

                if j["has_more"]:
                    url = j["next_page"]
                else:
                    break

        except IOError:
            pass

        return cards
