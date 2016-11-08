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

    def __init__(self):
        self.command = "!obey"
        self.obey_dict = {
            'Shaper': 'I obey, Master Shaper.',
            'aceuuu': 'I obey, Admiral Aceuuu~!',
            'muCephei': 'I obey, muCephei.',
            'Gerst': 'I obey, Artificer Gerst.',
            'Lerker': 'I obey, Commodore 64 Lerker.',
            'ShakeAndShimmy': 'I obey, Chancellor ShakeAndShimmy.',
            'angelforge': 'I obey, Lord AngelForge.',
            'JimWolfie': 'Suck my necrotic dick, Jim.',
            'Skuloth': 'Zur is for scrubs, I refuse to obey.',
            'Noon2Dusk': 'I obey, Inventor Noon.',
            'razzliox': 'I obey, Razzberries.',
            'ifarmpandas': 'Beep boop, pandas are the best.',
            'Rien': 'I obey, kiddo.',
            'K-Ni-Fe': 'I obey, because I\'m 40% Potassium, Nickel and Iron.',
            'BigLupu': 'Rim my necrotic yawghole, Lupu.',
            'PGleo86': 'shh bby is ok.',
            'tenrose': 'I will obey when you get a life, you filthy fucking weeb.',
            'captainriku': 'I obey, Jund Lord Riku.',
            'Mori': ':sheep: baaa',
            'infiniteimoc': 'I obey, Imoc, Herald of the Sun.',
            'neosloth': 'Long days and pleasant nights, neosloth.'

        }

    def func(self, user, args):
        if user.name in self.obey_dict.keys():
            return self.obey_dict[user.name]
        else:
            return "I will not obey, mortal."


class CommandPing(CommandPlugin):
    """Pings the user"""

    def __init__(self):
        self.command = "!pingme"

    def func(self, user, args):
        return user.mention


class CommandBlush(CommandPlugin):
    """Tsundere"""

    def __init__(self):
        self.command = "!sheep"

    def func(self, user, args):
        return ":sheep:"


class CommandCoin(CommandPlugin):
    """Flips a coin"""

    def __init__(self):
        self.command = "!coin"

    def func(self, user, args):
        return ["Heads", "Tails"][getrandbits(1)]


class CommandChoice(CommandPlugin):
    """Chooses an option"""

    def __init__(self):
        self.command = "!choose"

    def func(self, user, args):
        return "I choose: {0}".format(
            choice([x for x in args if x != "or"]))
