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

    def _loadUrlAsJson(self, url):
        """
        Load a given url into a json object.
        """
        url = request.urlopen(url)
        return json.loads(url.read().decode("utf-8", "replace"))

    def searchCard(self, query):
        """
        Search for a card by name.
        """
        url = self.API_URL + "/cards/search?q=" + parse.quote(query)
        print(url)
        return self.getCardsFromUrl(url)

    def getCardsFromUrl(self, url):
        """
        Return all cards from a given url.
        """
        cards = []
        try:
            while True:
                j = self._loadUrlAsJson(url)
                data = j["data"]
                cards += [Card(x) for x in data]
                if j["has_more"]:
                    url = j["next_page"]
                else:
                    break

        except IOError:
            pass

        return cards
