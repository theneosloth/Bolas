 # -*- coding: utf-8 -*-
import asyncio

from .plugin_mount import PluginMount

from random import getrandbits, choice
from subprocess import check_output


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
            # neosloth
            "120767447681728512": "I obey.",
            # Average Dragon
            "182268688559374336": "Eat a dick, dragon."
        }

    def func(self, parent, message):
        if message.author.id in self.obey_dict.keys():
            return self.obey_dict[message.author.id]
        else:
            return "I will not obey."


class CommandPing(CommandPlugin):

    def __init__(self):
        self.command = "!pingme"
        self.helpstring = "!pingme: Pings the message.author."

    def func(self, parent, message):
        return message.author.mention


class CommandAddMe(CommandPlugin):
    """!addme: The link to add Bolas to your Discord room."""

    def __init__(self):
        self.command = "!addme"
        self.helpstring = "!addme: " \
                          "The link to add Bolas to your Discord server."

    def func(self, parent, message):
        return "https://discordapp.com/oauth2/authorize?client_id=245372541915365377&scope=bot&permissions=0"


class CommandCoin(CommandPlugin):

    def __init__(self):
        self.command = "!coin"
        self.helpstring = "!coin: Flips a coin."

    def func(self, parent, message):
        return ["Heads", "Tails"][getrandbits(1)]


class CommandChoice(CommandPlugin):

    def __init__(self):
        self.command = "!choose"
        self.helpstring = "!choose: Chooses an option. "\
                          "Example: !choose apples or oranges"

    def func(self, parent, message):
        return "I choose: {0}".format(
            choice(" ".join(message.content.split(" ")[1:]).split(" or ")))


class CommandGit(CommandPlugin):

    def __init__(self):
        self.command = "!git"
        self.helpstring = "!git: Repo link and changelog."

    def func(self, parent, message):
        return "{0}\n{1}\n```{2}```".format(
            "https://gitlab.com/neosloth/bolas",
            "https://github.com/superstepa/bolas",
            check_output("git log --oneline -3", shell=True).decode("utf-8"))


class CommandCockatrice(CommandPlugin):

    def __init__(self):
        self.command = "!cockatrice"
        self.helpstring = "!cockatrice: Add yourself to the cockatrice role."
        self.role_name = "Cockatrice"

    def func(self, parent, message):

        if message.server is None:
            return "Sorry, I can't set roles in PMs."

        # The discord bot Client only stores the user,
        # so we have to manually get the Member object
        client_member = message.server.get_member(parent.user.id)

        sufficient_permissions = message.channel.permissions_for(
            client_member).manage_roles

        if not sufficient_permissions:
            return "I do not have sufficient permissions to set roles."

        cockatrice_role = None

        # Find the appropriate role object
        for role in message.server.roles:
            if role.name == self.role_name:
                cockatrice_role = role

        # Can't do anything if the role doesn't exist
        if cockatrice_role is None:
            return "Sorry, this server does not have a cockatrice role."

        if cockatrice_role in message.author.roles:
            # The remove role method is a coroutine so we have to wrap it in an asyncio call
            asyncio.ensure_future(
                parent.remove_roles(message.author, cockatrice_role)
            )
            return "Removed {0.name} from the Cockatrice role.".format(
                message.author
            )
        else:
            # The add role method is a coroutine so we have to wrap it in an asyncio call
            asyncio.ensure_future(
                parent.add_roles(message.author, cockatrice_role)
            )
            return "Added {0.name} to the Cockatrice role.".format(
                message.author
            )

class CommandRule(CommandPlugin):
    def __init__(self):
        self.command = "!rule"
        self.helpstring = "!rule {rule number}: Cite a mtg rule."
        self.FILE_NAME = "./MagicCompRules_20170707.txt"


    def get_rule(self, num):
        try:
            with open(self.FILE_NAME, "r") as f:
                # Using enumerate so the file is read sequentially and is not stored in memory
                for i, line in enumerate(f):
                    if (line.startswith(str(num))):
                        return "```{}```".format(line)
            return "Could not find the matching rule."
        except FileNotFoundError:
            return "Could not find the magic comprehensive rules file."


    def func(self, parent, message):
        args = message.content.split()
        if len(args) > 1:
            return self.get_rule(args[1])
        else:
            return "Please provide a rule number."\
                " See the full list of rules here: http://magic.wizards.com/en/game-info/gameplay/rules-and-formats/rules"
