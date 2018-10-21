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
            self.__setattr__("image", self.image_uris["normal"])
            try:
                self.__setattr__("art_crop", self.image_uris["art_crop"])
            except KeyError:
                pass

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

    def get_hex_color(self):
        "Returns the hex code of the color of the card"

        hex_colors = {
                "W": 0xffffff,
                "U": 0x0080ff,
                "B": 0x000000,
                "R": 0xff0000,
                "G": 0x008000,
            }

        if (len(self["colors"]) == 0):
            # Gray for artifacts and lands
            return 0xc0c0c0
        elif (len(self["colors"]) == 1):
            # Color of the card
            return hex_colors[self["colors"][0]]
        else:
            # Gold for multicolor
            return 0xffff00

    def format_embed(self):
        name, oracle = str(self).split("\n", 1)
        name = name.strip("*")
        embed = Embed(title=name,
                      url=self["scryfall_uri"],
                      description=oracle,
                      color=self.get_hex_color())

        if "image" in self:
            embed.set_thumbnail(url=self["image"])

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
