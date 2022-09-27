import os.path
import re
import json
import html
import urllib.request as request

from discord import Embed, File
from discord.ext import commands
from urllib.error import HTTPError
from datetime import date

from .commands import Misc

class Colorpie(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ctx = Misc(bot)
        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.DIRECTORY = os.path.realpath(os.path.join(
            self.ROOT_DIR, "../../misc/"
        ))
        self.COLORS = {"w":"white",
                       "u":"blue",
                       "b":"black",
                       "r":"red",
                       "g":"green"
        }
        
        self.NUMBERS = {"1":"primary",
                        "2":"secondary",
                        "3":"tertiary"}


    def get_colorpie(self, ctx, color=None, number=None):
        colorpie_link, colorpie_title = self.get_colorpie_link() 
        result = ""
        result+= "**{}** <{}>\n".format(colorpie_title.upper(), colorpie_link)            

        try:
            response = request.urlopen(colorpie_link)
            html_data = response.read().decode("utf-8", "replace")
            if html_data != '':
                page_data = html_data.splitlines()
                color_line = None
                for line in page_data:
                    if "<h2>" in line:
                        color_line = re.search(r'(<h2>([a-zA-Z&;]*)?<\/h2>)',line)
                    if not color_line is None and ("primary" in color_line[0].lower() or "secondary" in color_line[0].lower() or "tertiary" in color_line[0].lower()):
                        if (color is None or color.lower() in color_line[0].lower()) and (number is None or number in color_line[0].lower()):
                            if "<h2>" in line and ("primary" in line.lower() or "secondary" in line.lower() or "tertiary" in line.lower()):
                                result+= "\n**{}**\n".format(html.unescape(color_line[2]))
                            if "<li>" in line and "</li>" in line:
                                li_line = re.search(r'(<li>(.*?)<\/li>)',line)
                                result+= "- {}\n".format(html.unescape(li_line[2]).replace("<nbsp> . . . </nbsp>","..."))
        except HTTPError as e:
            pass   
        return result
    
    def get_colorpie_link(self):        
        year = str(date.today().year)[0:1]
        url = "https://magic.wizards.com/en/section-articles-see-more-ajax?l=en&f=13541&search-result-theme=&limit=6&fromDate=&toDate=&sort=DESC&word=mechanical+color+pie+{}&offset=0".format(year)
        try:
            response = request.urlopen(url)
            data = json.loads(response.read().decode("utf-8", "replace"))
            colorpie_url = None
            if len(data['data']) > 0:
                for el in data['data']:
                    if colorpie_url is None:
                        colorpie_url = re.search(r'(\/en\/articles\/archive\/making-magic\/mechanical-color-pie-[0-9\-]*)',el)
                        if not colorpie_url is None:
                            colorpie_title = re.search(r'(<h3>(.*?)<\/h3>)',el)
        except HTTPError as e:
            response = e.read()
        if not colorpie_url is None:
            return "https://magic.wizards.com{}".format(colorpie_url[0]), colorpie_title[2]
        else:
            return None

    @commands.command()
    async def colorpie(self, ctx, *, search_str = ""):
        "Get colorpie information."
        # args = ctx.message.content.split()
        if not search_str.strip() == "":
            search_arr = search_str.split()
            if search_arr[0] in self.COLORS or search_arr[0] in self.COLORS.values():
                search_color = search_arr[0]
                search_number = None
                if search_color in self.COLORS:
                    search_color = self.COLORS[search_color.lower()]
                if len(search_arr) > 1:                    
                    if search_arr[1] in self.NUMBERS or search_arr[1] in self.NUMBERS.values():
                        search_number = search_arr[1]
                        if search_number in self.NUMBERS:
                            search_number = self.NUMBERS[search_number]                 
                colorpie = self.get_colorpie(ctx, search_color, search_number)                
                if len(colorpie) <= 1900:
                    await self.ctx.send(ctx,"Emrakul used the Internet Explorer and found the following:\n```markdown\n{}```".format(colorpie))
                else:
                    txt_number = ""
                    if not search_number is None:
                        txt_number = "-{}".format(search_number)
                    filename = "colorpie-{}{}.txt".format(search_color, txt_number)
                    filename_os = os.path.realpath(os.path.join(
                        self.DIRECTORY, filename
                    ))
                    with open(filename_os, "w") as file:
                        file.write(colorpie)
                    with open(filename_os, "rb") as file:
                        await self.ctx.send(ctx,"Emrakul used the Internet Explorer and found the following:", file=File(file, filename))
                        os.remove(filename_os)
            else:
                colorpie_link, colorpie_title = self.get_colorpie_link()
                await self.ctx.send(ctx,"Please provide optionally a color (+ optionally [1-3 or primary, secondary, tertiary]).\n" \
                               "See the {} article here: <{}>".format(colorpie_title,colorpie_link), delete_after=5)
        else:
            colorpie = self.get_colorpie(ctx)
            filename = "colorpie.txt"
            filename_os = os.path.realpath(os.path.join(
                self.DIRECTORY, filename
            ))
            with open(filename_os, "w") as file:
                file.write(colorpie)
            with open(filename_os, "rb") as file:
                await self.ctx.send(ctx,"Emrakul used the Internet Explorer and found the following:", file=File(file, filename))
                os.remove(filename_os)
    
    @commands.command()
    async def colorpie_link(self, ctx):
        "Get the links to the current Mechanical Color Pie Articles"
        year = str(date.today().year)[0:1]
        url = "https://magic.wizards.com/en/section-articles-see-more-ajax?l=en&f=13541&search-result-theme=&limit=6&fromDate=&toDate=&sort=DESC&word=mechanical+color+pie+{}&offset=0".format(year)
        try:
            response = request.urlopen(url)
            data = json.loads(response.read().decode("utf-8", "replace"))
            colorpie_url = None
            colorpie_changes_url = None
            if len(data['data']) > 0:
                for el in data['data']:
                    if colorpie_url is None:
                        colorpie_url = re.search(r'(\/en\/articles\/archive\/making-magic\/mechanical-color-pie-[0-9\-]*)',el)
                        if not colorpie_url is None:
                            colorpie_title = re.search(r'(<h3>(.*?)<\/h3>)',el)
                    if colorpie_changes_url is None:
                        colorpie_changes_url = re.search(r'(\/en\/articles\/archive\/making-magic\/mechanical-color-pie-[0-9]{4}-[a-z]*-[0-9\-]*)',el)
                        if not colorpie_changes_url is None:
                            colorpie_changes_title = re.search(r'(<h3>(.*?)<\/h3>)',el)
        except HTTPError as e:
            response = e.read()
        message = ""
        if not colorpie_url is None:
            message+= "**{}**: <https://magic.wizards.com{}>\n".format(colorpie_title[2],colorpie_url[0])
        if not colorpie_changes_url is None:
            message+= "**{}**: <https://magic.wizards.com{}>\n".format(colorpie_changes_title[2],colorpie_changes_url[0])
        await self.ctx.send(ctx,message)
            

async def setup(bot):
    await bot.add_cog(Colorpie(bot))