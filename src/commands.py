import asyncio
import os.path

from random import choice, random
from subprocess import check_output

from .plugin_mount import PluginMount


class CommandPlugin(metaclass=PluginMount):
    """
    Class that stores the instances for each command.
    Every command must contain a command string property and a func function
    """

    def func(self, parent, message):
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
            "182268688559374336": "Eat a dick, dragon.",
            # Garta
            "217005730149040128": "Welcome, Srammiest Man",
            # spitefiremase
            "165971889351688192": "Mase, you're cooler and smarter and stronger and funnier in real life",
            # Shaper
            "115501385679634439": "Shaped shape shaping shapes~"
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
        return "https://discordapp.com/oauth2/authorize?"\
            "client_id=245372541915365377&scope=bot&permissions=0"


class CommandCoin(CommandPlugin):

    def __init__(self):
        self.command = "!coin"
        self.helpstring = "!coin: Flips a coin."

    def func(self, parent, message):
        return choice(["Heads", "Tails"])


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
            "https://theneosloth.github.io/Bolas/",
            check_output("git log --oneline -3", shell=True).decode("utf-8"))


class CommandStats(CommandPlugin):

    def __init__(self):
        self.command = "!stats"
        self.helpstring = "!stats: " \
                          " Return the number of users and servers served."

    def func(self, parent, message):
        num_servers = len(parent.servers)
        num_users = sum([len(server.members) for server in parent.servers])
        return "Fetching cards for {} servers and {} users".format(
            num_servers,
            num_users
        )


class CommandLfg(CommandPlugin):

    def __init__(self):
        self.command = "!lfg"
        self.helpstring = "!lfg: Add yourself to the LFG role."
        self.role_name = "LFG"

    def func(self, parent, message):

        if message.server is None:
            return "Sorry, I can't set roles in PMs."

        # The discord bot Client only stores the user,
        # so we have to manually get the Member object
        client_member = message.server.get_member(parent.user.id)

        sufficient_permissions = message.channel.permissions_for(
            client_member).manage_roles

        if not sufficient_permissions:
            return None

        lfg_role = None

        # Find the appropriate role object
        for role in message.server.roles:
            if role.name == self.role_name:
                lfg_role = role

        # Can't do anything if the role doesn't exist
        if lfg_role is None:
            return "Sorry, this server does not have a LFG role."

        if lfg_role in message.author.roles:
            # The remove role method is a coroutine
            # so we have to wrap it in an asyncio call
            asyncio.ensure_future(
                parent.remove_roles(message.author, lfg_role)
            )
            return "Removed {0.name} from the LFG role.".format(
                message.author
            )

        asyncio.ensure_future(
            parent.add_roles(message.author, lfg_role)
        )
        return "Added {0.name} to the LFG role.".format(
            message.author
        )


class CommandRule(CommandPlugin):
    def __init__(self):
        self.command = "!rule"
        self.helpstring = "!rule {rule number or set of keywords.}:"\
                          " Cite a mtg rule."
        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        # Move 1 directory up and into misc
        self.FILE_NAME = os.path.realpath(os.path.join(
            self.ROOT_DIR, "../misc/MagicCompRules_20181005.txt"))

        self.RULE_LIMIT = 10

    def get_rule(self, args):
        # First argument (presumably the rule number)
        num = args[1]
        # All the words after the command
        tokens = args[1:]
        result = ""
        rule_count = 0

        try:
            with open(self.FILE_NAME, "r", encoding="utf-8") as f:
                # Using enumerate so the file is read sequentially
                # and is not stored in memory
                for i, line in enumerate(f):
                    if (line.startswith(str(num))):
                        return line
                    # Append the rule number if all the words are in
                    # that rule.
                    # Only check the lines that start with a number.
                    # Also check if we've gone over our rule count
                    if (line[0].isdigit() and all(
                            word.lower() in line.lower() for word in tokens
                    ) and (rule_count < self.RULE_LIMIT)):

                        result = "{}* {}\n".format(result, line.split(" ")[0])
                        rule_count += 1

            if rule_count >= self.RULE_LIMIT:
                result += "The query returned too many results, " \
                          " so some of the results were omitted. " \
                          "Please provide more keywords to narrow the search."

            return result or "Could not find the matching rule."
        except FileNotFoundError:
            return "Could not find the magic comprehensive rules file."

    def func(self, parent, message):
        args = message.content.split()
        if len(args) > 1:
            # Surround the result with markdown code tags (for nice bullets)
            return "```markdown\n{}```".format(self.get_rule(args))
        else:
            return "Please provide a rule number or a set of keywords." \
                "See the full list of rules here: http://magic.wizards.com" \
                "/en/game-info/gameplay/rules-and-formats/rules"


class CommandAppearin(CommandPlugin):

    def __init__(self):
        self.command = "!appearin"
        self.helpstring = "!appearin:"\
                          " Create a new appearin call with everyone mentioned."

    def func(self, parent, message):
        # Random 10 digit number
        call_id = str(random())[2:12]
        url = "https://appear.in/{}?widescreen".format(call_id)

        # Simply send out the url if no one was mentioned
        if not message.mentions:
            return url

        invite_message = "{} is inviting you to a call.\n{}".format(
            message.author.name,
            url
        )

        asyncio.ensure_future(
            parent.send_message(message.author, invite_message))

        for mention in message.mentions:
            asyncio.ensure_future(
                parent.send_message(mention, invite_message))

        # No message is returned to the chat
        return None


class CommandVideo(CommandPlugin):

    def __init__(self):
        self.command = "!videocall"
        self.helpstring = "!videocall:"\
                          " Create a new videocall with everyone mentioned."

    def func(self, parent, message):
        # Random 10 digit number
        call_id = str(random())[2:12]
        url = "https://meet.jit.si/{}".format(call_id)

        # Simply send out the url if no one was mentioned
        if not message.mentions:
            return url

        invite_message = "{} is inviting you to a videocall.\n{}".format(
            message.author.name,
            url
        )

        asyncio.ensure_future(
            parent.send_message(message.author, invite_message))

        for mention in message.mentions:
            asyncio.ensure_future(
                parent.send_message(mention, invite_message))

        # No message is returned to the chat
        return None
