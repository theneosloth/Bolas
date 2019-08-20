import json
import re
import requests

from discord.ext import commands
from discord import Embed
from collections import defaultdict
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode


class Diff(commands.Cog):
    """
    Class to handle all operations related to getting
    differences between deck lists.

    """

    def __init__(self, bot):
        """
        Initializaton method.

        Parameters:
        -----------
        bot : dicord.ext.commands.Bot
            Discord Bot object.

        Returns:
        --------
        None

        """
        self.bot = bot

        # url domains and their options.
        self.urls_options = {
            "deckstats.net": {
                "query": [("export_dec", "1")]
                },
            "tappedout.net": {
                "query": [("fmt", "txt")]
                },
            "www.mtggoldfish.com": {
                'paths': [{"value": "download", "index": 2}]
                },
            "www.hareruyamtg.com": {
                'paths': [{"value": "download", "index": 3}],
                'replace': [{"old": "/show/", "new": ""}],
                },
            "archidekt.com": {
                'paths':
                    [
                        {"value": "api", "index": 1},
                        {"value": "small/", "index": 4},
                    ],
                },
            }

        self.re_stripangle = re.compile(r"^<(.*)>$")

        # Gets count and card name from decklist line
        self.re_line = re.compile(
                r"^\s*(?:(?P<sb>SB:)\s)?\s*"
                r"(?P<count>[0-9]+)x?\s+(?P<name>.*?)\s*"
                r"(?:<[^>]*>\s*)*(?:#.*)?$")

        # Dict of card names that should be replaced due to inconsistancy
        # AKA Wizards needs to errata Lim-Dûl's Vault already :(
        self.name_replacements = {
            "Lim-Dul's Vault": "Lim-Dûl's Vault",
            }

    class MessageError(Exception):
        """ Error class for sending error messages. """
        def __init__(self, message):
            """ Initializaton method. """
            self.message = message

    def get_valid_url(self, raw_url):
        """
        Parses a string into a valid url.

        Query and/or params are added or modified per
        configuration in self.urls_options.

        Parameters:
        -----------
        raw_url : str
            String to be parsed/transformed.

        Returns:
        --------
        str
            Empty URL or new URL with added params/queries.

        Raises:
        -------
        Diff.ErrorMessage
            When the URL doesn't have any options configured (Diff.url_options)

        """
        # strip surrounding < >. This allows for non-embedding links
        strip = self.re_stripangle.match(raw_url)
        if strip:
            raw_url = strip[1]

        url = urlsplit(raw_url, scheme="https")
        if (url.netloc and url.path and
                (url.scheme == "http" or url.scheme == "https")):
            valid_opts = self.urls_options.get(url.netloc, None)
            if not valid_opts:
                raise Diff.MessageError(f"Unknown url <{raw_url}>")
            url = list(url)

            # Add query params
            query = parse_qsl(url[3])
            query.extend(valid_opts.get("query", []))
            url[3] = urlencode(query)

            # Add each path to the position specified by the index value
            for path in valid_opts.get("paths", []):
                current_path = url[2].split("/")
                current_path.insert(path["index"], path["value"])
                url[2] = "/".join(current_path)

            url_str = urlunsplit(url)
            # Perform replacements after getting final URL
            for replace in valid_opts.get("replace", []):
                url_str = url_str.replace(replace["old"], replace["new"])

            return url_str
        return ""

    def filter_name(self, name):
        """
        Normalizes names.

        Parameters:
        -----------
        name : str
            String to be normalized.

        Returns:
        --------
        str
            Normalized name/string.

        """
        return self.name_replacements.get(name, name)

    def format_to_txt(self, deck):
        """
        Format json deck info into txt list.

        As of writting, this is only required for archidekt.com.
        Parameters:
        -----------
        deck : str
            Deck data in string format (txt or json).

        Returns:
        --------
        str
            Deck data in txt format.

        Samples
        -------
        input : json

            {
                cards:
                    [
                        {
                            card:
                                {
                                    oracleCard:
                                        {
                                            name: AAAAAA
                                        }
                                },
                            quantity: 1,
                            category: Sideboard
                        },
                        ...
                    ]

            }

        input : str

            1 AAAAAA\n
            ...
            \n
            separator
            2 BBBBBB\n
            ...

        output : str

            1 AAAAAA\n
            ...
            \n
            separator
            2 BBBBBB\n
            ...

        """
        try:
            json_deck = json.loads(deck)  # Raise ValueError if not JSON
            mainboard = []
            sideboard = ["//Sideboard"]  # Separator line
            for card in json_deck["cards"]:
                quantity = card["quantity"]
                name = card["card"]["oracleCard"]["name"]
                # No category means mainboard
                if not card["category"]:
                    mainboard.append(f"{quantity} {name}")
                elif card["category"] == "Sideboard":
                    sideboard.append(f"{quantity} {name}")
            return "\n".join(mainboard + sideboard)
        except ValueError:
            return deck  # If data is not JSON, assume it has proper format

    def get_list(self, deck):
        """
        Parses decklist string into a dict.

        Parameters:
        -----------
        deck : str
            Deck data in txt.

        Returns:
        --------
        dict
            Deck data in dict format.
            Guaranteed to have two keys: mainboard and sideboard.

        Samples
        -------
        input : str

            1 AAAAAA\n
            ...
            \n
            separator
            2 BBBBBB\n
            ...

        output : dict

            {
                "mainboard":
                    {
                        "AAAAAA": 1,
                        ...
                    },
                "siteboard":
                    {
                        "BBBBBB": 2,
                        ...
                    },
            }

        """
        mainboard = defaultdict(int)
        sideboard = defaultdict(int)

        deck_list = mainboard
        for line in self.format_to_txt(deck).split("\n"):
            match = self.re_line.match(line)
            if match:
                deck_list[self.filter_name(
                    match["name"])] += int(match["count"])
            elif "Sideboard" in line:
                deck_list = sideboard

        return {"mainboard": mainboard, "sideboard": sideboard}

    def get_diff(self, set1, set2):
        """
        Get differences between two dicts.

        Parameters:
        -----------
        set1 : dict
            First set of data to compare.
        set2 : dict
            Second set of data to compare.

        Returns:
        --------
        dict
            Resulting differences in dict format.

        Samples
        -------
        input : dict

            set1:
                {
                    "AAAAAA": 1,
                    ...
                }
            set2:
                {
                    "AAAAAA": 2,
                    ...
                }

        output : dict(str)

            {
                2:
                    1 AAAAAA\n
                    ...
            }

        """
        diff = defaultdict(str)

        cards = sorted(list(frozenset(set1.keys()) | frozenset(set2.keys())))
        for card in cards:
            quantity_diff = set1.get(card, 0) - set2.get(card, 0)
            if quantity_diff > 0:
                diff[1] += f"{quantity_diff} {card}\n"
            elif quantity_diff < 0:
                diff[2] += f"{abs(quantity_diff)} {card}\n"

        return diff

    def execute(self, message):
        """
        Perform a diff based on URLs provided in param.

        Parameters:
        -----------
        message: str
            Message for Discord bot.

        Returns:
        --------
        tuple
            (bool, str)

        Samples
        -------
        input : str
            !command http://url1 http://url2.com

        output : tuple(bool, str)

            (False, "Error message")

            (True, "1 AAAAAA\n")

        """
        try:
            # Get URLs
            urls = [
                url for url in (
                    self.get_valid_url(message)
                    for message in message.split()[1:])
                if url
                ]
            if len(urls) != 2:
                raise Diff.MessageError("Exactly two urls are needed.")

            # Get deck lists
            try:
                files = (requests.get(url).text for url in urls)
                decklists = [self.get_list(deck) for deck in files]
            except requests.exceptions.RequestException as exc:
                raise Diff.MessageError("Failed to open url.")

            # Get diffs
            maindiff = self.get_diff(
                decklists[0]["mainboard"],
                decklists[1]["mainboard"],
                )
            sidediff = self.get_diff(
                decklists[0]["sideboard"],
                decklists[1]["sideboard"],
                )

            # Format diffs for embed
            result = Embed()
            diffs_by_type = [("Mainboard", maindiff), ("Sideboard", sidediff)]
            for name, diff in diffs_by_type:
                for num, content in sorted(diff.items()):
                    result.add_field(
                        name=f"{name} {num}",
                        value=content,
                        inline=True,
                        )

            # Discord API has a 1024 length limit for embeds
            if len(result) < 1024:
                return True, result
            else:
                return False, "Diff too long."

        except Diff.MessageError as exc:
            return False, exc.message

    @commands.command()
    async def diff(self, ctx):
        """
        Entry point for bot command.

        Parameters:
        -----------
        ctx : discord.bot.commands.Context
            Context instance of bot message.

        Returns:
        --------
        None

        """
        is_valid, result = self.execute(ctx.message.content)

        if not is_valid:
            return await ctx.send(result)

        return await ctx.send(embed=result)


def setup(bot):
    """ Setup command for Discord bot. """
    bot.add_cog(Diff(bot))
