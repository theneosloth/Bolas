[https://theneosloth.github.io/Bolas/](https://theneosloth.github.io/Bolas)

# Bolas

Bolas is a mtg card-fetcher discord bot that is heavily inspired by [yawgmoth](https://github.com/Lerker3/yawgmoth). I am using this project as a way to try out some new approaches to api wrappers and plugin systems, so the way some parts of the bot are implemented are a bit esoteric.

## Structure

The core of the bot is located in bot.py, all simple commands such as !pingme should go in commands.py. More advanced functionality such as the card fetcher should be developed in card_hooks.py. Those files contain the base class that the plugins should be derived from.

The plugins are loaded through a metaclass called PluginMount. Every class derived from PluginMount will be automatically loaded and added to either the self.chat_hook or self.commands variables.

The docstring for each one of the plugins are all concatenated together and can be displayed with the hardcoded “!help” command.

## How to run

Export BOLAS_SECRET_TOKEN. Execute run.py.

```sh
#!/usr/bin/env bash
export BOLASDIR=/home/bolas/bolas
export $BOLAS_SECRET_TOKEN=THIS-IS-A-SECRET

cd $BOLASDIR
source $BOLASDIR/bin/activate
pgrep -f run.py || python $BOLASDIR/run.py

```

## Stats

Fetching cards for 152 servers and 15122 users (9151 unique users) as of September 2018.

## Add Bolas to your Discord server

[Click here](https://discordapp.com/oauth2/authorize?client_id=245372541915365377&scope=bot&permissions=0)
