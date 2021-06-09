import discord

from random import random
from subprocess import check_output

from discord.ext import commands
from discord_slash import cog_ext, SlashContext


class Misc(commands.Cog):
    def __init__(self, bot):
        """Miscellaneous simple commands."""
        self.bot = bot
        
    @commands.command()
    async def obey(self, ctx):
        """Only works if you are one of the chosen ones."""

        obey_dict = {
            # neosloth
            120767447681728512: "Hi dad.",
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
            141131991218126848: "Hi mum.",
            # Mori
            161511401322446848: ":sheep:"
        }

        if ctx.message.author.id in obey_dict.keys():
            await ctx.send(obey_dict[ctx.message.author.id])

    @commands.command()
    async def addme(self, ctx):
        """The link to add Emrakul to your Discord server."""
        await ctx.send("https://discordapp.com/oauth2/authorize?"
                       "client_id=850633920012877874&permissions=0&scope=bot%20applications.commands")

    @commands.command()
    async def git(self, ctx):
        """Repo link."""
        await ctx.send("https://github.com/MelffyBunilla/Emrakul")

    @commands.command()
    async def stats(self, ctx):
        """Return the number of users and servers served."""
        users = list(self.bot.get_all_members())

        await ctx.send("Fetching cards for {} servers and {} users ({} unique users)".format(
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
            await ctx.send(url)

        invite_message = "{} is inviting you to a videocall.\n{}".format(
            ctx.author.name,
            url
        )

        await ctx.author.send(invite_message)

        for mention in ctx.message.mentions:
            await mention.send(invite_message)    

    @cog_ext.cog_slash(name="obey",
                      description="Only works if you are one of the chosen ones.")
    async def _obey(self, ctx):
        obey_dict = {
            # neosloth
            120767447681728512: "Hi dad.",
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
            141131991218126848: "Hi mum.",
            # Mori
            161511401322446848: ":sheep:"
        }

        if ctx.message.author.id in obey_dict.keys():
            await ctx.send(obey_dict[ctx.message.author.id])

    @cog_ext.cog_slash(name="addme",
                      description="The link to add Emrakul to your Discord server.")
    async def _addme(self, ctx: SlashContext):
        await ctx.send("https://discordapp.com/oauth2/authorize?"
                       "client_id=850633920012877874&permissions=0&scope=bot%20applications.commands")
  
    @cog_ext.cog_slash(name="git",
                      description="Repo link.")
    async def _git(self, ctx):
        await ctx.send("https://github.com/MelffyBunilla/Emrakul")

    @cog_ext.cog_slash(name="stats",
                      description="Return the number of users and servers served.")
    async def _stats(self, ctx):
        users = list(self.bot.get_all_members())

        await ctx.send("Fetching cards for {} servers and {} users ({} unique users)".format(
            len(self.bot.guilds),
            len(users),
            len(set(users))
        ))

    @cog_ext.cog_slash(name="help",
                       description="Just type / and browse through the commands.")
    async def _help(self, ctx):
        await ctx.send("Just type / and browse through the commands.")       
        
    @cog_ext.cog_slash(name="video",
                      description="Create a new jitsi videocall with everyone mentioned.")
    async def _video(self, ctx):
        # Random 10 digit number
        call_id = str(random())[2:12]
        url = "https://meet.jit.si/{}".format(call_id)

        # Simply send out the url if no one was mentioned
        if not ctx.message.mentions:
            await ctx.send(url)

        invite_message = "{} is inviting you to a videocall.\n{}".format(
            ctx.author.name,
            url
        )

        await ctx.author.send(invite_message)

        for mention in ctx.message.mentions:
            await mention.send(invite_message)


def setup(bot):
    bot.add_cog(Misc(bot))
