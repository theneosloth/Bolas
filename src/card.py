class Card:
    """
    A wrapper around a Scryfall json card object.
    """

    def __init__(self, cardData):
        self._data = cardData

    def __getattr__(self, attr):
        """
        A hack that makes all attributes inaccessible,
        and instead returns the stored json values
        """
        if attr in self._data:
            return str(self._data[attr])
        else:
            return "Attribute not found."

    def __str__(self):
        """
        Returns the string representation of a magic card.
        The ** is the Discord way to bolden the text
        """
        return "**{0}** {1}\n{2}\n{3}".format(self.name, self.mana_cost,
                                              self.type_line,
                                              self.oracle_text)
