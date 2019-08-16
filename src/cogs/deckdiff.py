import json
import re
import urllib.request
import urllib.error

from discord.ext import commands
from discord import Embed
from collections import defaultdict
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode


class Diff(commands.Cog):

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
        # Dict of valid url domains, and options for those domains
        self.urls_options = {
            "deckstats.net": {
                "query":[("export_dec", "1")]
            },
            "tappedout.net": {
                "query":[("fmt", "txt")]
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
            "Lim-Dul's Vault": "Lim-Dûl's Vault"
        }

    #Error class for sending error messages
    class MessageError(Exception):
        def __init__(self, message):
            self.message = message

    # Parses a string to get a valid url
    # Returns None if not a good url
    # MessageError unknown url if url found and not in valid urls
    def get_valid_url(self, raw_url):
        #strip surrounding < >. This allows for non-embedding links
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

            # Add query params, if the configuration exists
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
        return None

    # Normalizes names.
    def filter_name(self, name):
        return self.name_replacements.get(name, name)

    # Format json deck info into txt list (for archidekt only)
    def format_to_txt(self, deck):
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


    # Parses decklist string into a tuple of dicts for main and sideboards
    def get_list(self, deck):
        mainboard = defaultdict(int)
        sideboard = defaultdict(int)

        deck_list = mainboard
        for line in self.format_to_txt(deck).split("\n"):
            match = self.re_line.match(line)
            if match:
                deck_list[self.filter_name(match["name"])] += int(match["count"])
            elif "Sideboard" in line:
                deck_list = sideboard

        return {"mainboard": mainboard, "sideboard": sideboard}

    # Diffs two decklist dicts
    # Returns 4-tuple with count and card name columns for both lists
    def get_diff(self, list1, list2):
        diff = defaultdict(str)

        cards = sorted(list(frozenset(list1.keys()) | frozenset(list2.keys())))
        for card in cards:
            quantity_diff = list1.get(card, 0) - list2.get(card, 0)
            if quantity_diff > 0:
                diff[1] += f"{quantity_diff} {card}\n"
            elif quantity_diff < 0:
                diff[2] += f"{abs(quantity_diff)} {card}\n"

        return diff

    def execute(self, message):
        " Perform actual diff. "
        try:
            urls = [
                url for url in (
                    self.get_valid_url(message)
                    for message in message.split()[1:])
                if url
                ]
            if len(urls) != 2:
                raise Diff.MessageError("Exactly two urls are needed.")

            try:
                # Should definitely split this into a few more lines
                files = (urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent':'Mozilla/5.0'}))
                        .read().decode("utf-8", "replace")
                    for u in urls)
                decklists = [self.get_list(deck) for deck in files]
            except urllib.error.URLError as exc:
                raise Diff.MessageError("Failed to open url.")

            maindiff = self.get_diff(
                decklists[0]["mainboard"],
                decklists[1]["mainboard"],
                )
            sidediff = self.get_diff(
                decklists[0]["sideboard"],
                decklists[1]["sideboard"],
                )

            result = Embed()
            diffs_by_type = [("Mainboard", maindiff), ("Sideboard", sidediff)]
            for name, diff in diffs_by_type:
                for num, content in diff.items():
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
        "List of differences between two decklists."
        is_valid, result = self.execute(ctx.message.content)

        if not is_valid:
            return await ctx.send(result)

        return await ctx.send(embed=result)

def setup(bot):
    bot.add_cog(Diff(bot))
