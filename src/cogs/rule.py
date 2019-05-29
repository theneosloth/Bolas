import os.path

from discord.ext import commands

class Rule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.FILE_NAME = os.path.realpath(os.path.join(
            self.ROOT_DIR, "../../misc/MagicCompRules_20181005.txt"
        ))

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

    @commands.command()
    async def rule(self, ctx):
        "!rule {rule number or set of keywords.}: Cite am mtg rule."
        args = ctx.message.content.split()
        if len(args) > 1:
            # Surround the result with markdown code tags (for nice bullets)
            await ctx.send("```markdown\n{}```".format(self.get_rule(args)))
        else:
            await ctx.send("Please provide a rule number or a set of keywords." \
                "See the full list of rules here: http://magic.wizards.com" \
                "/en/game-info/gameplay/rules-and-formats/rules")
