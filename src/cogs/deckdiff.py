import json
import re
import urllib.error
import urllib.request
from collections import defaultdict
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from discord import Embed
from discord.ext import commands


class Diff(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        # Dict of valid url domains, and options for those domains
        self.valid_urls = {
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
            "scryfall.com": {
                'subdomains': ["api"],
                'paths':
                    [
                        {"value": "export", "index": 4},
                        {"value": "text", "index": 5},
                    ],
                'replace': [{"old": r"\.com/@\w+/", "new": ".com/"}],
            },
            "www.moxfield.com": {
                'subdomains': ["api"],
                'paths':
                    [
                        {"value": "v1", "index": 1},
                        {"value": "all", "index": 3},
                        {"value": "download", "index": 5},
                    ],
                'replace': [{"old": "www.", "new": ""}],
                'query': [("exportId", "{{exportId}}")],
                'pre_request_paths':
                    [
                        {
                            "target": "exportId",
                            "path": "/v2/decks/all/",
                            "replace_map": [
                                {"origin_index": 4, "replace_index": 4},
                            ]
                        },
                    ]
            },
        }

        self.re_stripangle = re.compile(r"^<(.*)>$")
        # Gets count and card name from decklist line
        self.re_line = re.compile(
            r"^\s*(?:(?P<sb>SB:)\s)?\s*"
            r"(?P<count>[0-9]+)x?\s+(?P<name>.*?)\s*"
            r"(?:<[^>]*>\s*)*(?:#.*)?$")

        # Dict of card names that should be replaced due to inconsistency
        # AKA Wizards needs to errata Lim-Dûl's Vault already :(
        self.name_replacements = {
            "Lim-Dul's Vault": "Lim-Dûl's Vault"
        }

    # Error class for sending error messages
    class MessageError(Exception):
        def __init__(self, message):
            self.message = message

    # Parses a string to get a valid url
    # Returns None if not a good url
    # MessageError unknown url if url found and not in valid urls
    def get_valid_url(self, s):
        # strip surrounding < >. This allows for non-embedding links
        strip = self.re_stripangle.match(s)
        if strip:
            s = strip[1]

        url = urlsplit(s, scheme="https")
        if (url.netloc and url.path and
                (url.scheme == "http" or url.scheme == "https")):
            valid_opts = self.valid_urls.get(url.netloc, None)
            if not valid_opts:
                raise Diff.MessageError(
                    "Unknown url <{}>".format(s))
            url = list(url)

            query_n = valid_opts.get("query", None)
            if query_n:
                query_l = parse_qsl(url[3])
                query_l.extend(query_n)
                url[3] = urlencode(query_l)

            # Add subdomains to the domain, in order
            for subdomain in valid_opts.get("subdomains", []):
                url[1] = ".".join([subdomain, url[1]])

            # Add each path to the position specified by the index value
            for path in valid_opts.get("paths", []):
                current_path = url[2].split("/")
                current_path.insert(path["index"], path["value"])
                url[2] = "/".join(current_path)

            url_str = urlunsplit(url)
            # Perform replacements after getting final URL
            for replace in valid_opts.get("replace", []):
                url_str = re.sub(replace["old"], replace["new"], url_str)

            # Make any required api calls required to build URL
            # This is my shitty attempt to do so in a way that's reasonably dynamic
            # Blame Moxfield
            # -Sick
            for pre_request_path in valid_opts.get("pre_request_paths"):
                path = pre_request_path["path"]
                baseurl = list(urlsplit(url_str, scheme="https"))
                for replacement in pre_request_path["replace_map"]:
                    existing_path = baseurl[2].split("/")
                    new_path = path.split("/")
                    new_path.insert(replacement["replace_index"], existing_path[replacement["origin_index"]])
                    path = "/".join(new_path)

                baseurl = baseurl[0:2]
                baseurl.extend([path, '', ''])
                baseurl = urlunsplit(baseurl)

                target_result = self.get_special_query_arguments(baseurl, pre_request_path["target"])
                replace_target = '%7B%7B' + pre_request_path["target"] + '%7D%7D'
                url_str = url_str.replace(replace_target, target_result)

            return url_str
        else:
            return None

    # Handle pre-decklist url calls
    # Only used for Moxfield atm
    def get_special_query_arguments(self, url, targetKey):
        try:
            # Should definitely split this into a few more lines
            files = (urllib.request.urlopen(
                urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            ).read().decode("utf-8", "replace"))

            data = json.loads(files)

            return data[targetKey]

        except urllib.error.URLError as e:
            raise Diff.MessageError("Failed to open url.")

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
                if not card["category"]:  # No category means mainboard
                    mainboard.append(
                        "{0} {1}".format(
                            card["quantity"],
                            card["card"]["oracleCard"]["name"]
                        ))
                elif card["category"] == "Sideboard":
                    sideboard.append(
                        "{0} {1}".format(
                            card["quantity"],
                            card["card"]["oracleCard"]["name"]
                        ))
            return "\n".join(mainboard + sideboard)
        except ValueError:
            return deck  # If data is not JSON, assume it has proper format

    # Parses decklist string into a tuple of dicts for main and sideboards
    def get_list(self, deck):
        mainboard = defaultdict(int)
        sideboard = defaultdict(int)

        lst = mainboard
        for line in self.format_to_txt(deck).split("\n"):
            match = self.re_line.match(line)
            if match:
                lst[self.filter_name(match["name"])] += int(match["count"])
            elif "Sideboard" in line:
                lst = sideboard
        return mainboard, sideboard

    # Diffs two decklist dicts
    # Returns 4-tuple with count and card name columns for both lists
    def get_diff(self, list_l, list_r):
        cards = frozenset(list_l.keys()) | frozenset(list_r.keys())
        diff = ([], [], [], [])
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
        str_diff = (
            ([str(i) for i in diff[0]], diff[1]),
            ([str(i) for i in diff[2]], diff[3])
        )
        for num, lst in enumerate(str_diff, start=1):
            output = "\n".join(map(lambda x: "{} {}".format(*x), zip(*lst)))
            # Discord doesn't like empty fields
            if output:
                embed.add_field(name="{} {}".format(name, num), value=output,
                                inline=True)
        return embed

    @commands.command()
    async def diff(self, ctx):
        """List of differences between two decklists."""
        try:
            urls = [m for m in (self.get_valid_url(w)
                                for w in ctx.message.content.split()[1:]) if m]
            if len(urls) != 2:
                raise Diff.MessageError("Exactly two urls are needed.")

            try:
                # Should definitely split this into a few more lines
                files = (urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}))
                             .read().decode("utf-8", "replace")
                         for u in urls)
                decklists = [self.get_list(f) for f in files]
            except urllib.error.URLError as e:
                raise Diff.MessageError("Failed to open url.")

            main_diff = self.get_diff(decklists[0][0], decklists[1][0])
            side_diff = self.get_diff(decklists[0][1], decklists[1][1])

            result = Embed()
            self.format_diff_embed(main_diff, "Mainboard", result)
            self.format_diff_embed(side_diff, "Sideboard", result)

            # Discord doesn't allow embeds to be more than 1024 in length
            if len(result) < 1024:
                await ctx.send(embed=result)
            else:
                await ctx.send("Diff too long.")

        except Diff.MessageError as e:
            return await(ctx.send(e.message))


def setup(bot):
    bot.add_cog(Diff(bot))
