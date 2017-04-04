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
        self.admins = ["neosloth"]

        self.HELP_COMMAND = "!help"
        self.QUIT_COMMAND = "!quit"

        self.MESSAGE_MAX_LEN = 2000

        # Concatenate the helpstrings from each one of the plugins
        self.docstring = "```{0}\n\nYou can also PM me!```".format("\n\n".join(
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

            # Split it into words.
            msg = text.split(" ")

            # The first word is the command.
            command = msg[0]

            # The remainder are the arguments.
            args = msg[1:]

            print("{0} sent: {1} {2}".format(user, command, args).
                  encode("ascii", "ignore"))

            if (command == self.HELP_COMMAND):
                await self.say(self.docstring,
                               message.channel)
                return

            if (command == self.QUIT_COMMAND):
                await self.close()

            for cmd in self.commands:
                if (cmd.command == command):
                    await self.say(str(cmd.func(user, args)),
                                   message.channel)
                    # Don't run the chat hook if we found a command
                    return

            for plugin in self.chat_hook:
                result = plugin.func(message)

                if result:
                    await self.say(result, message.channel)

    async def on_ready(self):
        """Overloaded Method"""
        print("Logged in as {0}".format(self.user.name))

        formats = ["Vintage", "Pauper",  "EDH", "Legacy"]

        await self.change_presence(game=discord.Game(
            name="{0}".format(choice(formats))))
