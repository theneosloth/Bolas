import os.path
import re
import urllib.request as request

from discord.ext import commands
from urllib.error import HTTPError

from .commands import Misc


class Rule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ctx = Misc(bot)
        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.FILE_NAME = os.path.realpath(os.path.join(
            self.ROOT_DIR, "../../misc/rules/MagicCompRules_20181005.txt"
        ))

        self.RULE_LIMIT = 10

    def get_rule(self, args):
        # First argument (presumably the rule number)
        num = args[1]
        # All the words after the command
        tokens = args[1:]
        result = ""
        rule_count = 0

        file_name = self.get_rule_file()

        try:
            with open(file_name, "r", encoding="utf-8") as f:
                # Using enumerate so the file is read sequentially
                # and is not stored in memory
                for i, line in enumerate(f):
                    if (line.startswith(str(num))):
                        if len(line) >= 1923:
                            return line[0:1923] + "..."
                        else:
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

    def get_rule_file(self):
        try:
            response = request.urlopen(
                "https://magic.wizards.com/en/game-info/gameplay/rules-and-formats/rules")
        except HTTPError as e:
            pass
        html = response.read().decode("utf-8", "replace")
        if html != '':
            txt_file = re.search(r'(MagicCompRules(.*)\.txt)', html)
            txt_url = re.search(
                r'(https:\/\/media\.wizards\.com\/(.*)\.txt)', html)
            file_name = os.path.realpath(os.path.join(
                self.ROOT_DIR, "../../misc/rules/", txt_file[0].replace(
                    '%', '_')
            ))
            if file_name != '':
                if not os.path.isfile(file_name):
                    directory = os.path.realpath(os.path.join(
                        self.ROOT_DIR, "../../misc/rules/"
                    ))
                    files_in_directory = os.listdir(directory)
                    filtered_files = [
                        file for file in files_in_directory if file.endswith(".txt")]
                    for file in filtered_files:
                        path_to_file = os.path.join(directory, file)
                        os.remove(path_to_file)
                    request.urlretrieve(
                        txt_url[0].replace(" ", "%20"), file_name)
        return file_name

    @commands.command()
    async def rule(self, ctx):
        "!rule {rule number or set of keywords.}: Cite an mtg rule."
        args = ctx.message.content.split()
        if len(args) > 1:
            # Surround the result with markdown code tags (for nice bullets)
            rule = ""
            if len(args) == 2:
                rule += "<https://www.yawgatog.com/resources/magic-rules/#R{}>\n".format(
                    args[1].replace(".", ""))
            rule += "```markdown\n{}```".format(self.get_rule(args))
            await self.ctx.send(ctx,rule)
        else:
            await self.ctx.send(ctx,"Please provide a rule number or a set of keywords."
                           "See the full list of rules here: http://magic.wizards.com"
                           "/en/game-info/gameplay/rules-and-formats/rules")

    @commands.command()
    async def rule_pdf(self, ctx):
        "!rule_pdf Get the link to the current rule PDF"
        try:
            response = request.urlopen(
                "https://magic.wizards.com/en/game-info/gameplay/rules-and-formats/rules")
            html = response.read().decode("utf-8", "replace")
            if html != '':
                pdf_url = re.search(
                    r'(https:\/\/media\.wizards\.com\/(.*)\.pdf)', html)
                message = pdf_url[0]
        except HTTPError as e:
            message = e
        await self.ctx.send(ctx,message)


async def setup(bot):
    await bot.add_cog(Rule(bot))
