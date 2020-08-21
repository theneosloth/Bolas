from discord import Embed


class Card(dict):
    """
    A wrapper around a Scryfall json card object.
    It's just a dict with a custom __str__ method
    """

    def __init__(self, *args, **kwargs):
        # Superclass constructor
        dict.__init__(self, *args, **kwargs)

        # Setting up custom fields
        if "image_uris" in self:
            for key in self.image_uris:
                self.__setattr__("image_" + key, self.image_uris[key])

    def __getattr__(self, name):
        """
        A hack that makes all attributes inaccessible,
        and instead returns the stored json values as class fields.
        """
        if name in self:
            return self[name]

        return ""

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    @staticmethod
    def _dict_to_string(dic):
        "Returns a colon and newline separated string representation of a dictionary."
        return "\n".join(["{}: {}".format(x, str(y or "n/a"))
                          for x, y in dic.items()])

    def get_price_string(self):
        "Return a formatted string of a card's price"
        if "prices" in self:
            return self._dict_to_string(self["prices"])

        return "Price not found."

    def get_hex_color(self):
        "Returns the hex code of the color of the card"

        hex_colors = {
                "W": 0xe8e4db,
                "U": 0xc1d8e9,
                "B": 0x201720,
                "R": 0xF79D74,
                "G": 0xC2D6BF,
            }

        if ("colors" not in self or len(self["colors"]) == 0):
            # Gray for artifacts and lands
            return 0xc0c0c0
        elif (len(self["colors"]) == 1):
            # Color of the card
            return hex_colors[self["colors"][0]]
        else:
            # Gold for multicolor
            return 0xEDDC8A

    def format_embed(self):
        "Returns a discord Embed object representing the card"
        name, oracle = str(self).split("\n", 1)

        embed = Embed(title=name.replace("*", ""),
                      url=self["scryfall_uri"] if "scryfall_uri" in self else "",
                      description=oracle,
                      color=self.get_hex_color())

        if "image_small" in self:
            embed.set_thumbnail(url=self["image_small"])

        return embed

    def __str__(self):
        """
        Returns the string representation of a magic card.
        """
        # Power/toughness, seen only if it's a creature
        pt = ""
        if "power" in self:
            pt = "{0}/{1}".format(self.power,
                                  self.toughness).replace("*", "\*")
        # Append loyalty to the end of oracle text if the creature is a
        # planeswalker
        if "loyalty" in self:
            self.oracle_text = "{0}\nStarting Loyalty: {1}".format(
                self.oracle_text, self.loyalty)

        flavor = "*{0}*".format(
            self.flavor_text) if "flavor_text" in self else ""

        return "**{0}** {1}\n{2} {3}\n{4}\n{5}\n\n".format(self.name,
                                                           self.mana_cost,
                                                           self.type_line,
                                                           pt,
                                                           self.oracle_text,
                                                           flavor)
