from .plugin_mount import PluginMount

from random import getrandbits, choice


class CommandPlugin(metaclass=PluginMount):
    """
    Class that stores the instances for each command.
    Every command must contain a command string property and a func function
    """

    def func(self):
        raise NotImplementedError("Please implement this method")

    def __init__(self):
        raise NotImplementedError("Please implement a command variable")


class CommandObey(CommandPlugin):
    """!obey: This only works if you are one of the chosen ones."""

    def __init__(self):
        self.command = "!obey"
        self.obey_dict = {
            "neosloth": "I also think that Consecrated Sphinx is a bad card."
        }

    def func(self, user, args):
        if user.name in self.obey_dict.keys():
            return self.obey_dict[user.name]
        else:
            return "I will not obey."


class CommandPing(CommandPlugin):
    """!pingme: Pings the user"""

    def __init__(self):
        self.command = "!pingme"

    def func(self, user, args):
        return user.mention


class CommandAddMe(CommandPlugin):
    """!addme: The link to add Bolas to your Discord room."""

    def __init__(self):
        self.command = "!addme"

    def func(self, user, args):
        return "https://discordapp.com/oauth2/authorize?client_id=245372541915365377&scope=bot&permissions=0"


class CommandCoin(CommandPlugin):
    """!coin: Flips a coin"""

    def __init__(self):
        self.command = "!coin"

    def func(self, user, args):
        return ["Heads", "Tails"][getrandbits(1)]


class CommandChoice(CommandPlugin):
    """!choose: Chooses an option. Example: !choose apples or oranges"""

    def __init__(self):
        self.command = "!choose"

    def func(self, user, args):
        return "I choose: {0}".format(
            choice(" ".join(args).split("or")))


class CommandGit(CommandPlugin):
    """!git: Repo link"""

    def __init__(self):
        self.command = "!git"

    def func(self, user, args):
        return "https://gitlab.com/neosloth/Bolas/"
