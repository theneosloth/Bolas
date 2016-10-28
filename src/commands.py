from .plugin_mount import PluginMount


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
            "Shaper": "I obey, Master Shaper.",
            "aceuuu": "I obey, Admiral Aceuuu~!",
            "muCephei": "I obey, muCephei.",
            "Gerst": "I obey, Artificer Gerst.",
            "Lerker": "I obey, Commodore 64 Lerker.",
            "ShakeAndShimmy": "I obey, Chancellor ShakeAndShimmy.",
            "angelforge": "I obey, Lord AngelForge.",
            "JimWolfie": "Suck my necrotic dick, Jim.",
            "Skuloth": "Zur is for scrubs, I refuse to obey.",
            "Noon2Dusk": "I obey, Inventor Noon.",
            "razzliox": "I obey, Razzberries.",
            "ifarmpandas": "Beep boop, pandas are the best.",
            "Rien": "I obey, kiddo.",
            "K-Ni-Fe": "I obey, because I\"m 40% Potassium, Nickel and Iron.",
            "BigLupu": "Rim my necrotic yawghole, Lupu.",
            "PGleo86": "shh bby is ok",
            "neosloth": "Long days and pleasant nights, neosloth"
        }

    def func(self, user, args):
        if user.name in self.obey_dict.keys():
            return self.obey_dict[user.name]
        else:
            return "I will not obey, mortal."


class CommandPing(CommandPlugin):

    def __init__(self):
        self.command = "!pingme"

    def func(self, user, args):
        return user.mention
