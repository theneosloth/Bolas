import re
import urllib.request
import urllib.error

from discord.ext import commands
from discord import Embed
from collections import defaultdict
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode


class Diff(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
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
                raise Diff.MessageError(
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
                raise Diff.MessageError("Error parsing file.")
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

    @commands.command()
    async def diff(self, ctx):
        "List of differences between two decklists."
        try:
            urls = [m for m in (self.get_valid_url(w)
                for w in ctx.message.content.split()[1:]) if m]
            if len(urls) != 2:
                raise Diff.MessageError("Exactly two urls are needed.")

            try:
                # Should definitely split this into a few more lines
                files = (urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent':'Mozilla/5.0'}))
                        .read().decode("utf-8", "replace")
                    for u in urls)
                decklists = [self.get_list(f) for f in files]
            except urllib.error.URLError as e:
                raise Diff.MessageError("Failed to open url.")

            maindiff = self.get_diff(decklists[0][0], decklists[1][0])
            sidediff = self.get_diff(decklists[0][1], decklists[1][1])

            result = Embed()
            self.format_diff_embed(maindiff, "Mainboard", result)
            self.format_diff_embed(sidediff, "Sideboard", result)
            await ctx.send(embed=result)
        except Diff.MessageError as e:
            return await(ctx.send(e.message))

def setup(bot):
    bot.add_cog(Diff(bot))
