import json
import re

import urllib.request as request
import urllib.parse as parse

from urllib.error import HTTPError

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


    class CardLimitException(Exception):
        def __init__(self):
            self.message = "Too many cards returned by the query."

    class ScryfallException(Exception):
        def __init__(self, json):
            self.message = json["details"]

    def _load_url_as_json(self, url):
        """
        Load a given url into a json object.
        """
        try:
            url = request.urlopen(url)
        except HTTPError as e:
            # Try to get the ScryFall response error
            response = e.read()
            try:
                error_json = json.loads(response)
                raise self.ScryfallException(error_json)

            # Do nothing if it's a real http excepion
            except json.decoder.JSONDecodeError:
                pass

        return json.loads(url.read().decode("utf-8", "replace"))


    def get_card_rulings(self, cardid):
        url = f"{self.API_URL}/cards/{cardid}/rulings"
        rulings = self._load_url_as_json(url)
        return rulings["data"]

    def card_named(self, name, exact=False):
        """Get a card named NAME"""

        if exact:
            url = self.API_URL + "/cards/named?exact=" + parse.quote(name)
        else:
            url = self.API_URL + "/cards/named?fuzzy=" + parse.quote(name)

        result = self._load_url_as_json(url)

        # If we haven't found a card abort the seach
        if result["object"] == "error":
            raise self.ScryfallException(result)


        return Card(result)


    def search_card(self, query, max_cards = None):
        """
        Search for a card by name.
        """
        url = self.API_URL + "/cards/search?q=" + parse.quote(query)
        result = self.get_cards_from_url(url, max_cards)
        # Strip custom scryfall arguments from the cardname
        name = re.sub("[a-z]+:[a-z]+", "", query).strip().lower()
        for card in result:
            # If we have an exact match and it's not a DFC or a flip card, return just one
            if card.name.lower() == name and (
                    ("all_parts" not in card) and
                    (card.object != "card_face")):
                return [card]

        return result

    def get_cards_from_url(self, url, max_cards=None):
        """
        Return all cards from a given url.
        """
        cards = []
        layout_blacklist = ["art_series"]
        try:
            while True:
                j = self._load_url_as_json(url)

                if (j["object"] == "error"):
                    raise self.ScryfallException(j)

                count = j["total_cards"]

                if max_cards and count > max_cards:
                    raise self.CardLimitException()

                data = j["data"]
                for obj in data:

                    # Ignore the art series cards
                    if obj["layout"] in layout_blacklist:
                        continue

                    if "all_parts" in obj:
                        # If the card has additional parts add them to the
                        # response
                        cards += [Card(self._load_url_as_json(part["uri"]))
                                  for part in obj["all_parts"]]
                    elif "card_faces" in obj:
                        cards += [Card(face)
                                  for face in obj["card_faces"]]
                    else:
                        cards.append(Card(obj))

                if self.LOAD_ALL_MATCHES and j["has_more"]:
                    url = j["next_page"]
                else:
                    break

        except IOError:
            pass

        return cards
