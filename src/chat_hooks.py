import re

from .plugin_mount import PluginMount

from mtgjson import CardDb


class HookPlugin(metaclass=PluginMount):
    """
    """

    def func(self):
        raise NotImplementedError("Please implement this method")

    def __init__(self):
        raise NotImplementedError("Please implement a command")


class CardFetcher(HookPlugin):

    def __init__(self):
        self.pattern = re.compile("\[\[(.*)\]\]")
        self.db = CardDb.from_url()

    def _img_from_gatherer(self, url):
        return url.replace("Pages/Card/Details.aspx",
                           "Handlers/Image.ashx") + "&type=card"

    def func(self, msg):
        results = []
        for match in re.findall(self.pattern, msg):
            card = self.db.cards_by_name[match]
            results.append("{0}\n{1}\n\n".format(
                card.name, self._img_from_gatherer(card.gatherer_url)))

        return results
