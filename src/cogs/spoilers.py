import asyncio
import json
import requests
import aiohttp
import os.path
import urllib.request as request
import urllib.parse
import pytz
import discord

from discord import Embed, File, ForumChannel
from discord.ext import commands, tasks
from urllib.parse import quote, quote_plus
from datetime import datetime, timedelta
from io import BytesIO

from .commands import Misc


class Spoilers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.FILE_NAME = os.path.realpath(os.path.join(
            self.ROOT_DIR, "../../misc/spoiler_threads/threads.txt"
        ))
        self.task_start = datetime.now()
        self.news_cycle.start()
        self.restart_news_started = False
        self.ctx = Misc(bot)

    @commands.command()
    async def remove_news_channel(self, ctx):
        "!remove_news_channel: Remove news channel. (Manage Channels Permission required)"
        if ctx.message.author.guild_permissions.manage_channels:
            guild_id = ctx.message.guild.id
            with open(self.FILE_NAME) as file:
                lines = file.readlines()
                all_lines = ""
                for line in lines:
                    tmp_threads = line.rstrip().split(',')
                    if not int(tmp_threads[0]) == guild_id:
                        all_lines+= line.rstrip() + '\n'
            threads_file = open(self.FILE_NAME, 'w')
            threads_file.write(all_lines)
            threads_file.close()
            await self.ctx.send(ctx, "News Channel removed from Emmy.")
        else:
            await self.ctx.send(ctx, "You don't have the permissions to use this command.")
    
    @commands.command()
    async def add_news_channel(self, ctx):
        "!add_news_channel {Channel ID} {optional: Tag}: Add news channel. (Right click a channel, then click 'Copy ID') (Manage Channels Permission required)"
        if ctx.message.author.guild_permissions.manage_channels:
            args = ctx.message.content.split()        
            if len(args) > 1:
                try:
                    parent_id = int(args[1])
                    channel = ctx.message.guild.get_channel(parent_id)
                    if isinstance(channel, ForumChannel):
                        guild_id = ctx.message.guild.id
                        with open(self.FILE_NAME) as file:
                            lines = file.readlines()
                            threads = []
                            for line in lines:
                                tmp_threads = line.rstrip().split(',')
                                threads.append(int(tmp_threads[0]))
                        if not guild_id in threads:
                            threads_file = open(self.FILE_NAME, 'a+')
                            thread = {
                                "name": "Forum Channel added to News Command",
                                "content": "This is a test thread, you can delete it if you want."
                            }
                            thread_info = str(guild_id) + ',' + str(parent_id)
                            thread_tag_id = ""
                            if len(args) > 2:
                                for tag_id, tag in channel._available_tags.items():                            
                                    if tag.name == args[2]:
                                        thread_tag_id = ',' + str(tag.id)
                                        thread["applied_tags"] = [channel.get_tag(tag.id)]
                            try:
                                thread, message = await channel.create_thread(**thread)
                                try:
                                    await thread.edit(archived=True)
                                    threads_file.write(f"{thread_info}{thread_tag_id}\n")
                                except discord.errors.Forbidden as e:
                                    await thread.send("Missing channel permissions. (Emmy needs to manage posts)")
                            except discord.errors.Forbidden as e:
                                await self.ctx.send(ctx, "Missing channel permissions. (Emmy needs to create and manage posts)")
                        else:
                            await self.ctx.send(ctx, "You already added a News Channel to this Server.")
                    else:
                        await self.ctx.send(ctx, "The provided channel id is not a forum channel.")
                except ValueError as e:
                    await self.ctx.send(ctx, "Please provide a forum channel id. (Right click a channel, then click 'Copy ID')")            
            else:
                await self.ctx.send(ctx, "Please provide a forum channel id. (Right click a channel, then click 'Copy ID')")
        else:
            await self.ctx.send(ctx, "You don't have the permissions to use this command.")

    async def close_threads(self, guild_id, parent_id):
        guild = self.bot.get_guild(guild_id)
        guild_threads = await guild.active_threads()
        for thread in guild_threads:
            if thread.parent_id == parent_id:
                dt = datetime.now().replace(tzinfo=pytz.UTC)

                msg_dt = thread.created_at
                if thread.last_message:
                    message = thread.fetch_message(thread.last_message_id)
                    msg_dt = message.edited_at
                msg_dt = msg_dt + \
                    timedelta(minutes=thread.auto_archive_duration)

                if not thread.flags.pinned and dt > msg_dt:
                    await thread.edit(archived=True)

    async def get_news(self):
        dt = datetime.now()
        dt_now = str(dt.timestamp())[:10]
        dt = dt - timedelta(minutes=5)
        dt_previous = str(dt.timestamp())[:10]
        #api_url = f"https://api.pushshift.io/reddit/search/submission/?subreddit=magictcg&sort=asc&sort_type=created_utc&after={dt_previous}&before={dt_now}&size=1000"
        api_url = f"https://api.pushshift.io/reddit/search/submission/?subreddit=magictcg&sort=asc&sort_type=created_utc&after=1663487566&before={dt_now}&size=1000"
        newspaper = []
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                res = await response.json()
        if session is not None:
            await session.close()
        if res:
            for value in res['data']:
                if value['link_flair_text'] == "Spoiler":
                    tmp_news = {
                        "name": value['title'][:100],
                        "content": f"{urllib.parse.unquote(value['selftext'])}\n\n{value['full_link']}"[:2000],
                    }
                    # if "preview" in value:
                    #    session = aiohttp.ClientSession()
                    #    async with session.get(value['url']) as response:
                    #        img = await response.content.read()
                    #    if session is not None:
                    #        await session.close()
                    #    thread['file'] = discord.File(fp=BytesIO(img),filename=value['id'])
                    if "gallery_data" in value:
                        tmp_dict = []
                        i = 1
                        for item in value['gallery_data']['items']:
                            if item['media_id'] in value['media_metadata'] and i <= 10:
                                if value['media_metadata'][item['media_id']]['status'] == 'valid':
                                    img_url = urllib.parse.unquote(
                                        value['media_metadata'][item['media_id']]['s']['u']).replace("&amp;", "&")
                                    session = aiohttp.ClientSession()
                                    async with session.get(img_url) as response:
                                        img = await response.content.read()
                                    if session is not None:
                                        await session.close()
                                    img_name = item['media_id'] + ".jpg"
                                    tmp_dict.append(discord.File(
                                        fp=BytesIO(img), filename=img_name))
                                    i += 1
                        if len(tmp_dict) > 0:
                            tmp_news['files'] = tmp_dict
                    newspaper.append(tmp_news)
        return newspaper
    
    async def post_news_to_channels(self):
        """Get spoiler posts from reddit."""
        
        dt = datetime.now()
        dt_now = str(dt.timestamp())[:10]
        dt = dt - timedelta(minutes=5)
        dt_previous = str(dt.timestamp())[:10]
        #api_url = f"https://api.pushshift.io/reddit/search/submission/?subreddit=magictcg&sort=asc&sort_type=created_utc&after={dt_previous}&before={dt_now}&size=1000"
        api_url = f"https://api.pushshift.io/reddit/search/submission/?subreddit=magictcg&sort=asc&sort_type=created_utc&after=1663487566&before={dt_now}&size=1000"
        #api_url = "https://api.pushshift.io/reddit/search/submission/?subreddit=magictcg&sort=asc&sort_type=created_utc&after=1663487566&before=1663652569&size=1000"
        channel = self.bot.get_channel(1020929706478022658)
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                res = await response.json()
        if session is not None:
            await session.close()
        if res:
            for value in res['data']:
                if value['link_flair_text'] == "Spoiler":
                    thread = {
                        "name": value['title'][:100],
                        "content": f"{urllib.parse.unquote(value['selftext'])}\n\n{value['full_link']}"[:2000],
                        "applied_tags": [channel.get_tag(1020929955607085066)]
                    }
                    # if "preview" in value:
                    #    session = aiohttp.ClientSession()
                    #    async with session.get(value['url']) as response:
                    #        img = await response.content.read()
                    #    if session is not None:
                    #        await session.close()
                    #    thread['file'] = discord.File(fp=BytesIO(img),filename=value['id'])
                    if "gallery_data" in value:
                        tmp_dict = []
                        i = 1
                        for item in value['gallery_data']['items']:
                            if item['media_id'] in value['media_metadata'] and i <= 10:
                                if value['media_metadata'][item['media_id']]['status'] == 'valid':
                                    img_url = urllib.parse.unquote(
                                        value['media_metadata'][item['media_id']]['s']['u']).replace("&amp;", "&")
                                    session = aiohttp.ClientSession()
                                    async with session.get(img_url) as response:
                                        img = await response.content.read()
                                    if session is not None:
                                        await session.close()
                                    img_name = item['media_id'] + ".jpg"
                                    tmp_dict.append(discord.File(
                                        fp=BytesIO(img), filename=img_name))
                                    i += 1
                        if len(tmp_dict) > 0:
                            thread['files'] = tmp_dict
                    #await channel.create_thread(**thread)

    @tasks.loop(minutes=5)
    async def news_cycle(self):
        await self.bot.wait_until_ready()
        if not self.restart_news_started:
            print("test")
            self.restart_news_started = True
            self.restart_news.restart()
        with open(self.FILE_NAME) as file:
            lines = file.readlines()
            threads = []
            for line in lines:
                tmp_threads = line.rstrip().split(',')
                tmp_thread = {}
                tmp_thread['guild_id'] = int(tmp_threads[0])
                tmp_thread['parent_id'] = int(tmp_threads[1])
                if len(tmp_threads) > 2:
                    tmp_thread['tag_id'] = int(tmp_threads[2])
                threads.append(tmp_thread)
        for thread in threads:
            await self.close_threads(thread['guild_id'], thread['parent_id'])
            newspaper = await self.get_news()
            print(newspaper)
    
    @tasks.loop(minutes=1)
    async def restart_news(self):
        print("test")
        dt = datetime.now()
        ts = self.task_start + timedelta(minutes=2)
        print(ts)

        if dt < ts:
            self.restart_news_started = False
            self.task_start = ts
            self.news_cycle.restart()


async def setup(bot):
    await bot.add_cog(Spoilers(bot))
