import logging
import logging.handlers

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

        self.admins = ["120767447681728512"]

        self.HELP_COMMAND = "!help"
        self.QUIT_COMMAND = "!quit"

        self.MESSAGE_MAX_LEN = 2000

        # Concatenate the helpstrings from each one of the plugins
        self.docstring = "```{0}\n\nYou can also PM me with your queries!```".format("\n\n".join(
            x.helpstring.strip() for x in (CommandPlugin.plugins +
                                           HookPlugin.plugins))
        )


        self.logger = logging.getLogger('discord')
        self.logger.setLevel(logging.INFO)
        handler = logging.handlers.RotatingFileHandler(filename='discord.log', encoding='utf-8',
                                                       mode='w', backupCount=1, maxBytes=1000000)
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        self.logger.addHandler(handler)



    async def say(self, message, channel, embed=None):
        """ Wrapper for send_typing and send_message """

        #self.logger.info("Saying: #{0}".format(message).encode("ascii", "ignore"))

        try:
            await self.send_message(channel, message, embed=embed)
        except discord.errors.HTTPException:
            self.logger.error("Insufficient permissions for " + channel.id)

    async def on_message(self, message):
        """Overloaded Method"""
        if message.author != self.user:
            # Get the message itself.
            text = message.content
            user = message.author

            # The first word is the command.
            command = text.split(" ")[0]

            #self.logger.info("{0} sent: {1}".format(user, text).
            #      encode("ascii", "ignore"))

            if (command == self.HELP_COMMAND):
                await self.say(self.docstring,
                               message.channel)
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
        self.logger.info("Logged in as {0}".format(self.user.name))

        formats = ["Vintage", "Pauper", "EDH", "Legacy"]
        await self.change_presence(game=discord.Game(
            name="{0}".format(choice(formats))))
