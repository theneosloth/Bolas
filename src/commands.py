import asyncio
import os.path
import re
import urllib.request
import urllib.error
import discord

from itertools import chain
from random import choice, random
from subprocess import check_output
from collections import defaultdict
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

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

    @property
    def helpstring(self):
        return self._helpstring

    @property
    def command(self):
        """Get the command"""
        return self._command

    @property
    def name(self):
        """Get the name of the plugin (in this case it is the command)"""
        return self._command


class CommandObey(CommandPlugin):

    def __init__(self):
        self._command = "!obey"

        self._helpstring = "!obey: " \
                          "This only works if you are one of the chosen ones."

        self.obey_dict = {
            # neosloth
            120767447681728512: "I obey.",
            # Average Dragon
            182268688559374336: "Eat a dick, dragon.",
            # Garta
            217005730149040128: "Welcome, Srammiest Man",
            # spitefiremase
            165971889351688192: "Mase, you're cooler and smarter and stronger and funnier in real life",
            # Shaper
            115501385679634439: "Shaped shape shaping shapes~"
        }

    def func(self, parent, message):
        if message.author.id in self.obey_dict.keys():
            return self.obey_dict[message.author.id]
        else:
            return "I will not obey."

class CommandAddMe(CommandPlugin):
    """!addme: The link to add Bolas to your Discord room."""

    def __init__(self):
        self._command = "!addme"
        self._helpstring = "!addme: " \
                          "The link to add Bolas to your Discord server."

    def func(self, parent, message):
        return "https://discordapp.com/oauth2/authorize?"\
            "client_id=245372541915365377&scope=bot&permissions=0"


class CommandCoin(CommandPlugin):

    def __init__(self):
        self._command = "!coin"
        self._helpstring = "!coin: Flips a coin."

    def func(self, parent, message):
        return choice(["Heads", "Tails"])


class CommandChoice(CommandPlugin):

    def __init__(self):
        self._command = "!choose"
        self._helpstring = "!choose: Chooses an option. "\
                          "Example: !choose apples or oranges"

    def func(self, parent, message):
        return "I choose: {0}".format(
            choice(" ".join(message.content.split(" ")[1:]).split(" or ")))


class CommandGit(CommandPlugin):

    def __init__(self):
        self._command = "!git"
        self._helpstring = "!git: Repo link and changelog."

    def func(self, parent, message):
        return "{}\n```{}```".format(
            "https://theneosloth.github.io/Bolas/",
            check_output("git log --oneline -3", shell=True).decode("utf-8"))


class CommandStats(CommandPlugin):

    def __init__(self):
        self._command = "!stats"
        self._helpstring = "!stats: " \
                          " Return the number of users and servers served."

    def func(self, parent, message):
        users = list(chain.from_iterable(
            [list(server.members) for server in parent.guilds]))

        return "Fetching cards for {} servers and {} users ({} unique users)".format(
            len(parent.guilds),
            len(users),
            len(set(users))
        )



class CommandRule(CommandPlugin):
    def __init__(self):
        self._command = "!rule"
        self._helpstring = "!rule {rule number or set of keywords.}:"\
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



class CommandVideo(CommandPlugin):

    def __init__(self):
        self._command = "!videocall"
        self._helpstring = "!videocall:"\
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


class CommandDiff(CommandPlugin):

    def __init__(self):
        self._command = "!diff"
        self._helpstring = "!diff:"\
                          " Generates diff of two decklists."

        # Dict of valid url domains, and options for those domains
        self.valid_urls = {
            "deckstats.net": {
                "query":[("export_dec", "1")]
            },
            "tappedout.net": {
                "query":[("fmt", "dec")]
            }
        }

        self.re_stripangle = re.compile(r"^<(.*)>$")
        # Gets count and card name from decklist line
        self.re_line = re.compile(
                r"^\s*(?:(?P<sb>SB:)\s)?\s*"
                r"(?P<count>[0-9]+)x?\s+(?P<name>.*?)\s*"
                r"(?:<[^>]*>\s*)*(?:#.*)?$")
        # Lines to skip when reading decklists
        self.re_skip = re.compile(r"^\s*(?:$|//)")

        # Dict of card names that should be replaced due to inconsistancy
        # AKA Wizards needs to errata Lim-Dûl's Vault already :(
        self.name_replacements = {
            "Lim-Dul's Vault": "Lim-Dûl's Vault"
        }

    #Error class for sending error messages
    class MessageError(Exception):
        def __init__(self, message):
            self.message = message

    # Parses a string to get a valid url
    # Returns None if not a good url
    # MessageError unknown url if url found and not in valid urls
    def get_valid_url(self, s):
        #strip surrounding < >. This allows for non-embedding links
        strip = self.re_stripangle.match(s)
        if strip:
            s = strip[1]

        url = urlsplit(s, scheme="https")
        if (url.netloc and url.path and
                (url.scheme == "http" or url.scheme == "https")):
            valid_opts = self.valid_urls.get(url.netloc, None)
            if not valid_opts:
                raise CommandDiff.MessageError(
                        "Unknown url <{}>".format(s))
            url = list(url)
            query_n = valid_opts.get("query", None)
            if query_n:
                query_l = parse_qsl(url[3])
                query_l.extend(query_n)
                url[3] = urlencode(query_l)
            return urlunsplit(url)
        else:
            return None

    # Normalizes names.
    def filter_name(self, name):
        return self.name_replacements.get(name, name)

    # Parses decklist string into a tuple of dicts for main and sideboards
    def get_list(self, deck):
        mainboard = defaultdict(int)
        sideboard = defaultdict(int)
        for line in deck.split("\n"):
            if self.re_skip.match(line):
                continue
            match = self.re_line.match(line)
            if not match:
                raise CommandDiff.MessageError("Error parsing file.")
            if match["sb"]:
                lst = sideboard
            else:
                lst = mainboard
            lst[self.filter_name(match["name"])] += int(match["count"])
        return (mainboard, sideboard)

    # Diffs two decklist dicts
    # Returns 4-tuple with count and card name columns for both lists
    def get_diff(self, list_l, list_r):
        cards = frozenset(list_l.keys()) | frozenset(list_r.keys())
        diff = ([],[],[],[])
        for c in cards:
            if list_l[c] > list_r[c]:
                diff[1].append(c)
                diff[0].append(list_l[c] - list_r[c])
            elif list_r[c] > list_l[c]:
                diff[3].append(c)
                diff[2].append(list_r[c] - list_l[c])
        return diff

    # Takes a diff 4-tuple and adds it as fields on given embed.
    def format_diff_embed(self, diff, name, embed):
        strdiff = (
                ([str(i) for i in diff[0]], diff[1]),
                ([str(i) for i in diff[2]], diff[3])
        )
        for num, lst in enumerate(strdiff, start=1):
            output = "\n".join(map(lambda x: "{} {}".format(*x), zip(*lst)))
            # Discord doesn't like empty fields
            if output:
                embed.add_field(name="{} {}".format(name, num), value=output,
                        inline=True)
        return embed

    def func(self, parent, message):
        try:
            urls = [m for m in (self.get_valid_url(w)
                for w in message.content.split()[1:]) if m]
            if len(urls) != 2:
                raise CommandDiff.MessageError("Exactly two urls are needed.")

            try:
                # Should definitely split this into a few more lines
                files = (urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent':'Mozilla/5.0'}))
                        .read().decode("utf-8", "replace")
                    for u in urls)
                decklists = [self.get_list(f) for f in files]
            except urllib.error.URLError as e:
                raise CommandDiff.MessageError("Failed to open url.")

            maindiff = self.get_diff(decklists[0][0], decklists[1][0])
            sidediff = self.get_diff(decklists[0][1], decklists[1][1])

            result = discord.Embed()
            self.format_diff_embed(maindiff, "Mainboard", result)
            self.format_diff_embed(sidediff, "Sideboard", result)
            return result
        except CommandDiff.MessageError as e:
            return e.message
