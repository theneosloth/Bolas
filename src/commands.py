from .plugin_mount import PluginMount

from random import getrandbits, choice
from subprocess import run, PIPE

class CommandPlugin(metaclass=PluginMount):
    """
    Class that stores the instances for each command.
    Every command must contain a command string property and a func function
    """

    def func(self):
        raise NotImplementedError("Please implement this method.")

    def __init__(self):
        raise NotImplementedError(
            "Please implement a command variable and a helpstring variable.")


class CommandObey(CommandPlugin):

    def __init__(self):
        self.command = "!obey"

        self.helpstring = "!obey: " \
                          "This only works if you are one of the chosen ones."

        self.obey_dict = {
            "neosloth": "I obey."
        }

    def func(self, user, args):
        if user.name in self.obey_dict.keys():
            return self.obey_dict[user.name]
        else:
            return "I will not obey."


class CommandPing(CommandPlugin):

    def __init__(self):
        self.command = "!pingme"
        self.helpstring = "!pingme: Pings the user."

    def func(self, user, args):
        return user.mention


class CommandAddMe(CommandPlugin):
    """!addme: The link to add Bolas to your Discord room."""

    def __init__(self):
        self.command = "!addme"
        self.helpstring = "!addme: " \
                          "The link to add Bolas to your Discord server."

    def func(self, user, args):
        return "https://discordapp.com/oauth2/authorize?client_id=245372541915365377&scope=bot&permissions=0"


class CommandCoin(CommandPlugin):

    def __init__(self):
        self.command = "!coin"
        self.helpstring = "!coin: Flips a coin."

    def func(self, user, args):
        return ["Heads", "Tails"][getrandbits(1)]


class CommandChoice(CommandPlugin):

    def __init__(self):
        self.command = "!choose"
        self.helpstring = "!choose: Chooses an option. "\
                          "Example: !choose apples or oranges"

    def func(self, user, args):
        return "I choose: {0}".format(
            choice(" ".join(args).split(" or ")))


class CommandGit(CommandPlugin):

    def __init__(self):
        self.command = "!git"
        self.helpstring = "!git: Repo link."

    def func(self, user, args):
        return "{0}\n{1}".format(
            "https://gitlab.com/neosloth/bolas",
            "https://github.com/superstepa/bolas")

class CommandChangelog(CommandPlugin):
    def __init__(self):
        self.command = "!changelog"
        self.helpstring = "!changelog: Gets the last 3 changes to the bot"

    def func(self, user, args):
        changes = run(
            "git log --oneline -3",
            stdout=PIPE).stdout.decode('utf-8')
        return "{}".format(changes)
