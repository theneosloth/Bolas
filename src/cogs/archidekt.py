import asyncio
import json
import re
import os.path
import requests
import random
import urllib.request as request

from discord import Embed, File
from discord.ext import commands
from urllib.parse import quote, quote_plus
from urllib.error import HTTPError

from .commands import Misc
from .tokens import Tokens

class Archidekt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pattern = re.compile("\[\[((?:[^\]]|\][^\]])+)\]\]")
        self.tokens = Tokens(bot)
        self.ctx = Misc(bot)
        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.DIRECTORY = os.path.realpath(os.path.join(
            self.ROOT_DIR, "../../misc/"
        ))
        self.MAX_CARDS = 8
        self.MAX_CARDS_BEFORE_LIST = 4
        # Need to be all lowercase
        
        self.COLORS = {"white" : "w",
                       "blue" : "u",
                       "black" : "b",
                       "red" : "r",
                       "green" : "g"            
        }
        
        self.COLOR_IDENTITY = {"w" : "Mono-White | W",
                               "u" : "Mono-Blue | U",
                               "b" : "Mono-Black | B",
                               "r" : "Mono-Red | R",
                               "g" : "Mono-Green | G",
                               "wu" : "Azorius | WU",
                               "ub" : "Dimir | UB",
                               "br" : "Rakdos | BR",
                               "rg" : "Gruul | RG",
                               "wg" : "Selesnya | GW",
                               "wb" : "Orzhov | WB",
                               "ur" : "Izzet | UR",
                               "bg" : "Golgari | BG",
                               "wr" : "Boros | RW",
                               "ug" : "Simic | UG",
                               "wub" : "Esper | WUB",
                               "ubr" : "Grixis | UBR",
                               "brg" : "Jund | BRG",
                               "wrg" : "Naya | RGW",
                               "wug" : "Bant | GWU",
                               "wbg" : "Abzan | WBG",
                               "wur" : "Jeskai | URW",
                               "ubg" : "Sultai | BGU",
                               "wbr" : "Mardu | RWB",
                               "urg" : "Temur | GUR",
                               "wubr" : "Sans-Green | WUBR",
                               "ubrg" : "Sans-White | UBRG",
                               "wbrg" : "Sans-Blue | BRGW",
                               "wurg" : "Sans-Black | RGWU",
                               "wubg" : "Sans-Red | GWUB",
                               "wubrg" : "5 Color | WUBRG"
        }
        
    async def embed_link(self, ctx, url="https://archidekt.com/decks/514420"):
        "Return embed of an Archidekt link."
        if not "archidekt" in url:
            await self.ctx.send(ctx,"Please provide an archidekt link!", delete_after=5)
            return
        og_url = url
        if "#" in url:
            url = url.split("#")
            url = url[0]
        if url[-1] == "/":
            url = url[:-1]
        url = url.split("/")
        deck_id = url[-1]
        url = "https://archidekt.com/api/decks/" + deck_id + "/"
        try:
            response = request.urlopen(url)
        except HTTPError as e:
            response = e.read()
            try:
                deck = json.loads(response)
                if "error" in deck:
                    await self.ctx.send(ctx,"Archidekt: " + deck["error"], delete_after=5)
                    return
                if "detail" in deck:
                    await self.ctx.send(ctx,"Archidekt: " + deck["detail"], delete_after=5)
                    return
            except json.decoder.JSONDecodeError:
                pass
        deck = json.loads(response.read().decode("utf-8", "replace"))
        description = "A deck on Archidekt.com"
        embed = Embed(title=deck['name'].replace("*", ""),
                      url=og_url,
                      description=description)
        embed.set_thumbnail(url=deck['customFeatured'] if deck['customFeatured'] != "" else deck['featured'])
        embed.set_author(name=deck['owner']['username'])
        return og_url, embed
    
    @commands.command()
    async def all_tokens(self, ctx, *, url="https://archidekt.com/user/2874 [EDH/B]"):
        "Returns tokens of all defined Archidekt lists of a user."
        await self.ctx.send(ctx,"This can take ~5-20 seconds, and DMs you the tokens instead of posting here", delete_after=5)
        if not "archidekt" in url or not "/user/" in url:
            await self.ctx.send(ctx,"Please provide the link to your archidekt user list", delete_after=5)
            return
        if " " in url:
            url = url.split(" ")
            str_filter = url[1]
            url = url[0]
        else:
            str_filter = ""
        try:
            if int(str_filter) < 10:
                limit = int(str_filter)
                str_filter = ""
        except ValueError as e:
            if ctx.message.author.id == 141131991218126848:
                limit = 25
            else:
                limit = 10        
        if url[-1] == "/":
            url = url[:-1]
        url = url.split("/")
        user_id = url[-1]
        user_url = "https://archidekt.com/api/users/" + user_id + "/"
        try:
            response = request.urlopen(user_url)
        except HTTPError as e:
            response = e.read()
            try:
                deck = json.loads(response)
                if "error" in deck:
                    await self.ctx.send(ctx,"Archidekt: " + deck["error"], delete_after=5)
                    return
                if "detail" in deck:
                    await self.ctx.send(ctx,"Archidekt: " + deck["detail"], delete_after=5)
                    return
            except json.decoder.JSONDecodeError:
                pass
        user_decks = json.loads(response.read().decode("utf-8", "replace"))
        token_array = []
        x = 0
        for deck_arr in user_decks['decks']:
            if x <= limit and not deck_arr['private'] and (str_filter == "" or str_filter in deck_arr['name']):
                x=x+1
                url = "https://archidekt.com/api/decks/" + str(deck_arr['id']) + "/"
                try:
                    response = request.urlopen(url)
                except HTTPError as e:
                    pass
                deck = json.loads(response.read().decode("utf-8", "replace"))
                token_array = await self.tokens.get_tokens(ctx, deck, token_array)
        tokens = "**User:** " + user_decks['username'] + "\n"
        tokens+= "**Tokens:**\n"
        if token_array:
            token_array.sort()
            for token in token_array:
                tokens+= token + "\n"
            length = len(tokens)
            tokens = tokens[:length - 1]
        else:
            tokens = "No tokens needed for any of these decks."
        filename = "tokens.txt"
        filename_os = os.path.realpath(os.path.join(
            self.DIRECTORY, filename
        ))
        with open(filename_os, "w") as file:
            file.write(tokens)
        with open(filename_os, "rb") as file:
            await ctx.author.send("You need the following tokens:", file=File(file, filename))
            os.remove(filename_os)
        
    @commands.command()
    async def tokens(self, ctx, *, url = "https://archidekt.com/decks/514420"):
        "Return tokens of an Archidekt list."
        if not "archidekt" in url:
            await self.ctx.send(ctx,"Please provide an archidekt link!", delete_after=5)
            return
        if "#" in url:
            url = url.split("#")
            url = url[0]
        if url[-1] == "/":
            url = url[:-1]
        url = url.split("/")
        deck_id = url[-1]
        url = "https://archidekt.com/api/decks/" + deck_id + "/"
        try:
            response = request.urlopen(url)
        except HTTPError as e:
            response = e.read()
            try:
                deck = json.loads(response)
                if "error" in deck:
                    await self.ctx.send(ctx,"Archidekt: " + deck["error"], delete_after=5)
                    return
                if "detail" in deck:
                    await self.ctx.send(ctx,"Archidekt: " + deck["detail"], delete_after=5)
                    return
            except json.decoder.JSONDecodeError:
                pass
        deck = json.loads(response.read().decode("utf-8", "replace"))
        token_array = await self.tokens.get_tokens(ctx, deck)
        tokens = "**Deck:** " + deck['name'] + "\n"
        tokens+= "**Tokens:**\n"
        if token_array:
            token_array.sort()
            for token in token_array:
                tokens+= token + "\n"
            length = len(tokens)
            tokens = tokens[:length - 1]
        else:
            tokens = "No tokens needed for this deck."
        await self.ctx.send(ctx,tokens)

async def setup(bot):
    await bot.add_cog(Archidekt(bot))