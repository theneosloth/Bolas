[Stats](https://discord.com/api/oauth2/authorize?client_id=850633920012877874&permissions=0&scope=bot)

# Emrakul

Emrakul is a mtg card-fetcher discord bot based on [Bolas](https://github.com/theneosloth/Bolas), which itself is heavily inspired by [yawgmoth](https://github.com/Lerker3/yawgmoth).

The docstring for each one of the plugins are all concatenated together and can be displayed with the hardcoded “!help” command.

## Changes compared to Bolas
```
The price command now also works for DFC cards
You can use regex like on Scryfall now
You can search for DFC cards also with the full name using the two slashes like some websites do
The messages that pop up when you search something embarrassingly wrong destroy themselves in 5..., 4..., 3..., 2..., 1...
"sad robot", "bob" and "tim" now show the proper versions they reference
When the Bolas bot owner types in !obey, it says "Hi dad." and when I type it says "Hi mum."
```

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

## Add Emrakul to your Discord server

[Click here](https://discord.com/api/oauth2/authorize?client_id=850633920012877874&permissions=0&scope=bot)
