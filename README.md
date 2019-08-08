[![Stats](https://img.shields.io/badge/discord-207%20servers%2015420%20unique%20users-blue.svg)](https://discordapp.com/oauth2/authorize?client_id=245372541915365377&scope=bot&permissions=0)
[![Docker Pulls](https://img.shields.io/docker/pulls/neosloth/bolasbot.svg)](https://hub.docker.com/r/neosloth/bolasbot)


# Bolas

[https://theneosloth.github.io/Bolas/](https://theneosloth.github.io/Bolas)


Bolas is a mtg card-fetcher discord bot that is heavily inspired by [yawgmoth](https://github.com/Lerker3/yawgmoth).

The docstring for each one of the plugins are all concatenated together and can be displayed with the hardcoded “!help” command.

## List of commands

``` 
A magic the gathering card fetcher bot

Diff:
  diff     List of differences between two decklists.
Fetcher:
  art      Return the art of a given card.
  flavor   Return the flavor text of a given card.
  image    Return the image of a given card.
  price    Return the price of a given card.
  reserved Return whether the given card is reserved.
  rulings  Show all the rulings for a given card.
Misc:
  addme    The link to add Bolas to your Discord server.
  git      Repo link and changelog.
  obey     Only works if you are one of the chosen ones.
  stats    Return the number of users and servers served.
  video    Create a new jitsi videocall with everyone mentioned.
Rule:
  rule     !rule {rule number or set of keywords.}: Cite am mtg rule.
​No Category:
  help     Shows this message

Type !help command for more info on a command.
You can also type !help category for more info on a category
```

## How to run

Export BOLAS_SECRET_TOKEN. Execute run.py.

```sh
export BOLAS_SECRET_TOKEN=THIS-IS-A-SECRET
python ./run.py

```

## Using docker

The arm64v8 and amd64 images are available at [neosloth/bolasbot](https://hub.docker.com/r/neosloth/bolasbot). For other architectures the image can be built using the included Dockerfile

### Building the image

``` sh
docker build --tag=bolasbot .
```

### Running Bolas

``` sh
docker run -e BOLAS_SECRET_TOKEN=THIS_IS_A_SECRET --name bolas --restart unless-stopped bolasbot

```

## Add Bolas to your Discord server

[Click here](https://discordapp.com/oauth2/authorize?client_id=245372541915365377&scope=bot&permissions=0)
