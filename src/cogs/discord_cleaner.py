import re

from discord.ext import commands

class Cleaner(commands.Cog):
    """
    Set up on a per server basis
    """

    def __init__(self, bot):
        self.whitelist = {
            # EDH Discord server. Remove all non link posts from #decklists
            144547963484635137: (["decklists"], re.compile(".*http(s)*:\/\/.*")),
            # PlayEDH
            304276578005942272: (["decklists"], re.compile(".*http(s)*:\/\/.*")),
            # Dragon's server
            334571063197302784: (["decklists"], re.compile(".*http(s)*:\/\/.*")),
            # Teferi server
            278284235125686272: (["decklists"], re.compile(".*http(s)*:\/\/.*")),
            # Test Server
            404881906690293760: (["sshhhh"], re.compile(".*http(s)*:\/\/.*"))
        }
        self.bot = bot


    @commands.Cog.listener("on_message")
    async def channel_cleaner(self, message):

        # Terminate execution when in PMs
        if message.guild is None:
            return

        # Stop the function if the channel is not checked or if the
        # channel doesn't exist
        if (message.guild.id not in self.whitelist) or (
                (message.channel is None) or (message.channel.name not in self.whitelist[message.guild.id][0])):
            return

        client_member = message.guild.get_member(self.bot.user.id)
        if not message.channel.permissions_for(client_member).manage_messages:
            return

        if (self.whitelist[message.guild.id][1].match(message.content)) is None:
            await message.delete()
