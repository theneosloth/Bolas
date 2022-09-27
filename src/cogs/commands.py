import os.path
import discord
import random
import requests
import aiohttp
import urllib.parse
from datetime import datetime, timedelta
from io import BytesIO

from subprocess import check_output

from discord.ext import tasks, commands


class Misc(commands.Cog):
    def __init__(self, bot):
        """Miscellaneous simple commands."""
        self.bot = bot

    @commands.command()
    async def hello(self, ctx):
        """Only works if you are one of the chosen ones."""

        obey_dict = {
            # neosloth
            120767447681728512: "Hi neosloth.",
            # Average Dragon
            182268688559374336: "neosloth: Eat a dick, dragon.",
            # Garta
            217005730149040128: "neosloth: Welcome, Srammiest Man",
            # spitefiremase
            165971889351688192: "neosloth: Mase, you're cooler and smarter and stronger and funnier in real life",
            # Shaper
            115501385679634439: "neosloth: Shaped shape shaping shapes~",
            # Braden
            279686121149956096: "neosloth: Braden is definitely lame.",
            # Sickrobot
            98525939910078464: "neosloth: *sniffle* yea, sure",
            # Melffy Bunilla
            141131991218126848: "Hi cutie. <3",
            # Mori
            161511401322446848: ":sheep:"
        }

        if ctx.message.author.id in obey_dict.keys():
            await self.send(ctx,obey_dict[ctx.message.author.id])
        else:
            await self.send(ctx,"owo hi, ʰᵒʷ ʳ ᵘ")

    @commands.command()
    async def addme(self, ctx):
        """The link to add Bolas to your Discord server."""
        await self.send(ctx,"https://discordapp.com/oauth2/authorize?"
                       "client_id=850633920012877874&scope=bot&permissions=262144")

    async def fetch(url):
        async with aiohttp.ClientSession() as session, \
                session.get(url) as response:
            return await response

    async def send(self, ctx, content=None, embed=None, file=None, delete_after=None):
        context = {}
        if content:
            context['content'] = content
        if embed:
            context['embed'] = embed
        if file:
            context['file'] = file
        if delete_after:
            context['delete_after'] = delete_after
        if not self.bot.dev_mode or ctx.message.author.id == 141131991218126848:
            await ctx.send(**context)

    @commands.command()
    async def updates(self, ctx):
        "Get the current updates on the Emrakul bot."
        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.FILE_NAME = os.path.realpath(os.path.join(
            self.ROOT_DIR, "../../misc/updates/Emrakul-updates.txt"
        ))
        await self.send(ctx,file=discord.File(self.FILE_NAME))

    @commands.command()
    async def flirt(self, ctx):
        "Return the image of a given card."
        cute_choice = random.choices(["../../misc/emrablush.jpg",
                                      "../../misc/emrashy.png",
                                      ])
        flirt_line = random.choices(["Did it hurt when you broke through the plane's crust ascending from the underworld?",
                                     "Did it hurt when you broke through time and space to feed on reality itself?",
                                     "I'm learning about important dates in history. Wanna be one of them?",
                                     "Do you have a map? I keep getting lost in your eyes.",
                                     "You're so beautiful that you made me forget my pickup line.",
                                     "I was wondering if you had an extra heart. Mine was just stolen.",
                                     "Are you extraterrestrial? Because you just abducted my heart.",
                                     "You know what you would look really beautiful in? My tentacles.",
                                     "The spark in your soul is so bright, Heliod must be jealous.",
                                     "One night I looked up at the stars and thought, 'Wow, so many planes to consume.' But now that I'm looking at you, that all seems so pointless.",
                                     "If beauty were time, you'd be eternity.",
                                     "I love you to your plane and back.",
                                     "Hey cutie, you must be an eldritch horror because I find you maddening.",
                                     "You make me lose my mind!",
                                     "I can't wait for it to be full moon, so I can see you again.",
                                     "Three words. Fourteen letters. Say it and I'm all yours.\n\nBanding with you.",
                                     "Three words. Fourteen letters. Say it and I'm all yours.\n\nPartner with you.",
                                     "Two words. Fourteen letters.\n\nFriends Forever!",
                                     "I hope each night to become eternal, so I can be with you forever.",
                                     "You are the only Treasure I wouldn't sacrifice, not even for value.",
                                     ])
        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.FILE_NAME = os.path.realpath(os.path.join(
            self.ROOT_DIR, cute_choice[0]
        ))
        await self.send(ctx,flirt_line[0])
        await self.send(ctx,file=discord.File(self.FILE_NAME))

    @commands.command()
    async def scryfall_extension(self, ctx):
        "Download a simple Chrome extension that restores the Magiccards.info function to auto-focus the search bar."
        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.FILE_NAME = os.path.realpath(os.path.join(
            self.ROOT_DIR, "../../misc/scryfall_search_bar_ext.zip"
        ))
        install_guide = "1. Save this to a place you don't accidentally delete\n"
        install_guide += "2. Go to chrome://extensions/\n"
        install_guide += "3. Click in the top right on 'Developer mode'\n"
        install_guide += "4. Click 'Load unpacked'\n"
        install_guide += "5. Choose this .zip file, or folder if you unpacked it"
        await self.send(ctx,install_guide)
        await self.send(ctx,file=discord.File(self.FILE_NAME))

    @commands.command()
    async def asmor(self, ctx):
        "Asmoranomardicadaistinaculdacar"
        await self.send(ctx,"Asmoranomardicadaistinaculdacar")

    @commands.command()
    async def roll(self, ctx):
        "Roll any dice."
        args = ctx.message.content.split()
        table = random.choices([0, 1], [10, 1])
        people = random.randrange(1, 9999)
        if len(args) > 1:
            amount = 1
            result_amount = ""
            if "d" in args[1]:
                dice_arr = args[1].split("d")
                number = dice_arr[1]
                if not dice_arr[0] == "":
                    try:
                        amount = int(dice_arr[0])
                    except ValueError as e:
                        await self.send(ctx,"ö̴̲̳̼̯́̿͒ĥ̵͎̺̔̇̃̀͑̕ ̶̻̞̹̺͍̩̇͊̏̒̄͐͛͐̌̓n̷͖̪͌̀̄̑̓́̊̏͝o̴̡̲̺̭͙̖͉̝͎̪̎̂̈̍̓̈́ ̴̩͖̂̋͝w̴̱̭͖̲͍̓̿͌̓̀͋ͅh̸͍̣̣͒̔̂͛̊̽͝ȃ̷̡̨͎̖͍̞̪̣̪͑̌̄͊͌͛̀̚͝t̷͖͌ ̵̢͇̮̪͈̘͐́͑̆h̶͎̹̟̺̮̮̩̉̔͆̋̐͜͠ą̶͔̬̱̤̭̦͌̐͆̿̃̍͜͜ͅv̸̻̟͈̗̦̳̬̰̩́̄e̵̺͚̻͔̯̎͒̾ ̶̢̧̥̳̗̮̪̬̻̉͗͋̋̓͗͑̎̎ͅỳ̶͚̹͇̙̣̪̪͓͐̌̈́̽͑͝ő̴̧̟̜͔̘̥̠͋̀͐̀̆̎̾̇̏ú̸̡̡̫̟̻̼̰̺͙̐͋̐̚͠ ̵̢̳̣͈̾̈́͑̾͒̚͝d̷̤̥̱͉̒̌͌ọ̸̬̼͒̓̈̐̌̃̃̎̋͠-̷͓̀͊-̷̩̲̯͈̤̠̫̜͛̽͂̐͒͑͌͛͑-̶̧̞͖̼͔̙͓̗͔̥͆̊̅ ")
            else:
                number = args[1]
            if not number == "2":
                result_amount = "a"
                if amount > 1:
                    result_amount = "{}".format(amount)
                await self.send(ctx,"*Emrakul rolls {} massive interdimensional d{}, {} Innistrad people are crushed under the weight*".format(result_amount, number, people))
            if table[0] > 0:
                await self.send(ctx,"It fell off the plane **uwu**")
            else:
                try:
                    if int(amount) > 20:
                        await self.send(ctx,"....oh god they spilled all over I can't count all these....where's my favorite dice??? **>.<**")
                    elif int(number) < 2:
                        if amount > 1:
                            result_amount = " {} times".format(amount)
                        await self.send(ctx,"The dice landed on {}{}....what did you expect".format(number, amount))
                    elif int(number) == 2:
                        await self.send(ctx,"Emrakul: (╯°□°）╯︵ ┻━┻")
                        await self.flip(ctx)
                    else:
                        random_num = ""
                        for x in range(0, amount):
                            random_num = "{}{},".format(
                                random_num, random.randrange(1, int(number)))
                        if amount > 1:
                            result_txt = "Your results are {}".format(
                                random_num[:-1])
                        else:
                            result_txt = "Your result is {}".format(
                                random_num[:-1])
                        await self.send(ctx,result_txt)
                except ValueError as e:
                    await self.send(ctx,"ö̴̲̳̼̯́̿͒ĥ̵͎̺̔̇̃̀͑̕ ̶̻̞̹̺͍̩̇͊̏̒̄͐͛͐̌̓n̷͖̪͌̀̄̑̓́̊̏͝o̴̡̲̺̭͙̖͉̝͎̪̎̂̈̍̓̈́ ̴̩͖̂̋͝w̴̱̭͖̲͍̓̿͌̓̀͋ͅh̸͍̣̣͒̔̂͛̊̽͝ȃ̷̡̨͎̖͍̞̪̣̪͑̌̄͊͌͛̀̚͝t̷͖͌ ̵̢͇̮̪͈̘͐́͑̆h̶͎̹̟̺̮̮̩̉̔͆̋̐͜͠ą̶͔̬̱̤̭̦͌̐͆̿̃̍͜͜ͅv̸̻̟͈̗̦̳̬̰̩́̄e̵̺͚̻͔̯̎͒̾ ̶̢̧̥̳̗̮̪̬̻̉͗͋̋̓͗͑̎̎ͅỳ̶͚̹͇̙̣̪̪͓͐̌̈́̽͑͝ő̴̧̟̜͔̘̥̠͋̀͐̀̆̎̾̇̏ú̸̡̡̫̟̻̼̰̺͙̐͋̐̚͠ ̵̢̳̣͈̾̈́͑̾͒̚͝d̷̤̥̱͉̒̌͌ọ̸̬̼͒̓̈̐̌̃̃̎̋͠-̷͓̀͊-̷̩̲̯͈̤̠̫̜͛̽͂̐͒͑͌͛͑-̶̧̞͖̼͔̙͓̗͔̥͆̊̅ ")
        else:
            dice = random.choices([4, 6, 8, 10, 12, 20])
            await self.send(ctx,"*Emrakul rolls a massive interdimensional d{}, {} Innistrad townspeople are crushed by this dice*".format(dice[0], people))
            if table[0] > 0:
                await self.send(ctx,"It fell off the table uwu")
            else:
                await self.send(ctx,random.randrange(1, dice[0]))

    @commands.command()
    async def flip(self, ctx):
        "Flip a coin."
        side = random.choices([0, 1], [6000, 1])
        cat = random.choices([0, 1], [500, 1])
        people = random.randrange(1, 9999)
        await self.send(ctx,"*Emrakul throws a coin on an interdimensional scale, {} Innistrad townspeople are crushed when the coin lands*".format(people))
        if side[0] > 0:
            await self.send(ctx,"The coin landed on its side (a 1:6000 chance)")
        else:
            if cat[0] > 0:
                await self.send(ctx,"Alms Collector stole your coin, you drew a card instead")
            else:
                start = random.choices([0, 1])
                if start[0] > 0:
                    odds = [51, 49]
                else:
                    odds = [49, 51]
                coin = random.choices(["heads", "tails"], odds)
                await self.send(ctx,"The coin landed on {}".format(coin[0]))

    @commands.command()
    async def advice(self, ctx):
        "Emrakul gives advice."
        args = ctx.message.content.split()
        people = random.randrange(1, 9999)
        advice = random.choices(["It is certain.",
                                 "It is decidedly so.",
                                 "Without a doubt.",
                                 "Yes definitely.",
                                 "You may rely on it.",
                                 "As I see it, yes.",
                                 "Most likely.",
                                 "Outlook good.",
                                 "Yes.",
                                 "Signs point to yes.",
                                 "Reply hazy, try again.",
                                 "Ask again later.",
                                 "Better not tell you now.",
                                 "Cannot predict now.",
                                 "Concentrate and ask again.",
                                 "Don't count on it.",
                                 "My reply is no.",
                                 "My sources say no.",
                                 "Outlook not so good.",
                                 "Very doubtful.",
                                 "You did great today.",
                                 "I'm proud of you.",
                                 "You look stunning today.",
                                 "OMG I just saw a gif of a cute puppy.",
                                 "Did you hydrate today?",
                                 "You probably need to get some food.",
                                 "Someone in here needs to go to bed.",
                                 "You're valid.",
                                 ])
        await self.send(ctx,"*Emrakul wants to help you, but while starting to think she started to lean on the Innistrad plane, {} Innistrad townspeople were crushed due to that*".format(people))
        await self.send(ctx,advice[0])

    @commands.command()
    async def powerlevel(self, ctx):
        "What's the power level?!"
        seven = random.choices(["seven",
                                "سَبْعَة",
                                "sete",
                                "七",
                                "sedam",
                                "sedm",
                                "syv",
                                "zeven",
                                "siete",
                                "seitsemän",
                                "sept",
                                "sieben",
                                "επτά",
                                "sette",
                                "七",
                                "7",
                                "sju",
                                "siedem",
                                "sete",
                                "șapte",
                                "семь",
                                "siete",
                                "sju",
                                "семь",
                                "เจ็ด",
                                "yedi",
                                "сім",
                                "bảy", ])
        await self.send(ctx,"The deck has a power level of {} (7) out of 10.".format(seven[0]))

    @commands.command()
    async def cut(self, ctx):
        "Ask emmy for cut."
        land = random.choices(
            ["a plains", "an island", "a swamp", "a mountain", "a forest"])
        await self.send(ctx,"You should cut {}.".format(land[0]))

    @commands.command()
    async def git(self, ctx):
        """Repo link."""
        await self.send(ctx,"https://github.com/MelffyBunilla/Emrakul")

    @commands.command()
    async def stats(self, ctx):
        """Return the number of users and servers served."""
        users = list(self.bot.get_all_members())

        await self.send(ctx,"Fetching cards for {} servers and {} users ({} unique users)".format(
            len(self.bot.guilds),
            len(users),
            len(set(users))
        ))

    @commands.command()
    async def video(self, ctx):
        """Create a new jitsi videocall with everyone mentioned."""
        # Random 10 digit number
        call_id = str(random())[2:12]
        url = "https://meet.jit.si/{}".format(call_id)

        # Simply send out the url if no one was mentioned
        if not ctx.message.mentions:
            await self.send(ctx,url)

        invite_message = "{} is inviting you to a videocall.\n{}".format(
            ctx.author.name,
            url
        )

        await self.send(ctx.author,invite_message)

        for mention in ctx.message.mentions:
            await self.send(mention,invite_message)


async def setup(bot):
    await bot.add_cog(Misc(bot))
