import discord
import asyncio


from .commands import CommandPlugin
from .chat_hooks import HookPlugin

class Bolas(discord.Client):

    def __init__(self):
        """ Constructor for the  bot class.

        Args:
            token (str): the token for the discord bot.
        """
        super().__init__()

        self.commands = CommandPlugin.plugins
        self.chat_hook = HookPlugin.plugins

        self.admins = ["120767447681728512"]

        self.HELP_COMMAND = "!help"
        self.QUIT_COMMAND = "!quit"

        self.MESSAGE_MAX_LEN = 2000

    def generate_help_embed(self):

        result = discord.Embed(title="Bolas Help",
                               description="You can also PM me with your queries!")

        for plugin in (CommandPlugin.plugins + HookPlugin.plugins):
            result.add_field(name=plugin.name.strip(),
                             value=plugin.helpstring.strip(),
                             inline=False)
        result.add_field(name="Donate",
                         value="[Donate using Liberapay](https://liberapay.com/neosloth/donate)")
        return result

    async def say(self, message, channel, embed=None):
        """ Wrapper for send_typing and send_message """

        try:
            await channel.send(message, embed=embed)
        except discord.errors.HTTPException:
            print("Insufficient permissions for " + channel.id)

    async def on_message(self, message):
        """Overloaded Method"""
        if message.author != self.user:
            # Get the message itself.
            text = message.content
            user = message.author

            # The first word is the command.
            command = text.split(" ")[0]

            if (command == self.HELP_COMMAND):
                await self.say(None,
                               message.channel,
                               self.generate_help_embed())
                return

            if (command == self.QUIT_COMMAND and user.id in self.admins):
                await self.logout()

            for cmd in self.commands:
                if (cmd.command == command):
                    result = cmd.func(self, message)
                    # Some commands don't need to self.logger.info a message
                    if (result is not None):
                        if isinstance(result, discord.Embed):
                            await self.say(None, message.channel, result)
                        else:
                            await self.say(str(result), message.channel)
                    # Don't run the chat hook if we found a command
                    return

            for plugin in self.chat_hook:
                result = plugin.func(self, message)
                if result is not None:
                    if isinstance(result, list):
                        for r in result:
                            if (isinstance(r, discord.embeds.Embed)):
                                await self.say(None, message.channel, r)
                            else:
                                await self.say(str(r), message.channel)
                    else:
                        await self.say(str(result), message.channel)

    async def on_ready(self):
        """Overloaded Method"""
        print("Logged in as {0}".format(self.user.name))
