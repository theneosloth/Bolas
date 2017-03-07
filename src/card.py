class Card(dict):
    """
    A wrapper around a Scryfall json card object.
    """

    def __getattr__(self, name):
        """
        A hack that makes all attributes inaccessible,
        and instead returns the stored json values as class fields.
        """
        if name in self:
            if (isinstance(self[name], dict)):
                return self._format_dict(self[name])
            else:
                return str(self[name])
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __str__(self):
        """
        Returns the string representation of a magic card.
        The ** is the Discord way to bolden the text
        """
        # Power/toughness, seen only if it's a creature
        pt = ""
        if "power" in self:
            pt = "{0}/{1}".format(self.power, self.toughness)

        mana_cost = ""
        if "mana_cost" in self:
            mana_cost = self.mana_cost
        else:
            mana_cost = "{N/A}"

        return "**{0}** {1}\n{2} {3}\n{4}\n\n".format(self.name,
                                                      mana_cost,
                                                      self.type_line,
                                                      pt,
                                                      self.oracle_text)

    def _format_dict(self, dict):
        """
        Converts a dict into a readable, discord compatible string.
        """

        result = ""
        for k, v in dict.items():
            result += "\n{0}: {1}".format(k.capitalize(), v)

        return "```\n{0}\n```".format(result)
