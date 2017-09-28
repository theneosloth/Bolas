import discord
import asyncio

from .commands import CommandPlugin
from .chat_hooks import HookPlugin

from random import choice


class Bolas(discord.Client):

    def __init__(self, token):
        """ Constructor for the  bot class.

        Args:
            token (str): the token for the discord bot.
        """
        super().__init__()

        self.token = token

        self.commands = CommandPlugin.plugins
        self.chat_hook = HookPlugin.plugins

        self.admins = []

        self.HELP_COMMAND = "!help"
        self.QUIT_COMMAND = "!quit"

        self.MESSAGE_MAX_LEN = 2000

        # Concatenate the helpstrings from each one of the plugins
        self.docstring = "```{0}\n\nYou can also PM me with your queries!```".format("\n\n".join(
            x.helpstring.strip() for x in (CommandPlugin.plugins +
                                           HookPlugin.plugins))
        )

    async def say(self, message, channel):
        """ Wrapper for send_typing and send_message """

        if (len(message) > self.MESSAGE_MAX_LEN):
            print("Splitting into two messages.")
            await self.say(message[:self.MESSAGE_MAX_LEN], channel)
            await self.say(message[self.MESSAGE_MAX_LEN:], channel)
            return

        print("Saying: {0}".format(message).encode("ascii", "ignore"))
        await self.send_typing(channel)
        await self.send_message(channel, message)

    async def on_message(self, message):
        """Overloaded Method"""
        if message.author != self.user:
            # Get the message itself.
            text = message.content
            user = message.author

            # The first word is the command.
            command = text.split(" ")[0]

            print("{0} sent: {1}".format(user, text).
                  encode("ascii", "ignore"))

            if (command == self.HELP_COMMAND):
                await self.say(self.docstring,
                               message.channel)
                return

            if (command == self.QUIT_COMMAND and user.id in self.admins):
                await self.close()

            for cmd in self.commands:
                if (cmd.command == command):
                    await self.say(str(cmd.func(self, message)),
                                   message.channel)
                    # Don't run the chat hook if we found a command
                    return

            for plugin in self.chat_hook:
                result = plugin.func(self, message)

                if result and isinstance(result, str):
                    await self.say(result, message.channel)
                elif result and isinstance(result, list):
                    for r in result:
                        await self.say(r, message.channel)

    async def on_ready(self):
        """Overloaded Method"""
        print("Logged in as {0}".format(self.user.name))

        formats = ["Vintage", "Pauper", "EDH", "Legacy"]
        await self.change_presence(game=discord.Game(
            name="{0}".format(choice(formats))))
