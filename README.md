<div align="center">
  <h1 align="center">discord-bot</h1>
  <p align="center">
    <a href="https://docs.python.org/3/"><img src="https://img.shields.io/badge/python 3-3776AB.svg?style=&logo=python&logoColor=white" alt="Python" href=""/></a>
    <a href="https://pre-commit.com/"><img src="https://img.shields.io/badge/pre--commit-FAB040.svg?style=&logo=pre-commit&logoColor=black" alt="precommit" /></a>
  </p>
</div>

______________________________________________________________________

# Features

## Commands

Slash and prefix commands:
- `/afk` (`+afk`): Let others know you're AFK (Away From Keyboard).
- `/alias add` (`+alias`): Create a custom alias for quick reuse.
- `/alias list` (`+aliases`): Display a list of your saved aliases.
- `/alias remove` (`+unalias`): Remove a saved alias.
- `/avatar` (`+avatar`): Display the specified member's avatar(s).
- `/badge` (`+badge`): Change your badge (top role icon) on the server.
- `/banner` (`+banner`): Display the specified member's banner.
- `/color` (`+color`, `+cor`): Change your color (top role color) on the server.
- `/emote add`: Add a custom emote to the server.
- `/emote remove`: Remove a custom emote from the server.
- `/emote rename`: Rename a custom emote in the server.
- `/fake`: Send a message impersonating another user in the current channel.
- `/remind` (`+remind`, `+remindme`): Set a reminder for yourself or others.
- `/server` banner (`+serverbanner`): Display the guild's banner.
- `/server` icon (`+servericon`, `+server`): Display the guild's icon.
- `/snipe` (`+snipe`): Restore the last deleted message in the current channel.
- `/sticker add`: Add a sticker to the server.
- `/sticker remove`: Remove a sticker from the server.
- `/sticker rename`: Rename a sticker in the server.
- `/summarize` (`+summarize`, `+resumo`): Summarize the recent conversation in the chat.
- `/weather` (`+weather`, `+w`, `+clima`): Retrieve the current weather for a specified city.

## Listeners

These features run automatically, without user commands:
- Automatically transcribes voice messages (speech-to-text).
- Automatically downloads tracks from Spotify links.
- Automatically fixes Twitter/X and Instagram link previews.
- Automatically evaluates simple math expressions.

# Getting Started

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Bot account](https://docs.disnake.dev/en/stable/discord.html)

## Installing

1. Clone the repository using [Git](https://git-scm.com/).

```sh
git clone git@github.com:leandcesar/discord-bot.git
```

2. Go to directory.

```sh
cd discord-bot
```

## Running

3. Ensure to fill in the necessary environment variables in the `.env` file.
1. Build the Docker service for the application.

```sh
make build
```

5. Check if everything was installed correctly.

```sh
make up
```

## Cleaning up

6. Uninstall all Docker components.

```sh
make down
```

# Contributing

## Prerequisites

- [Python 3.10 or higher](https://www.python.org/downloads/)
- [Coroutines and Awaitables](https://docs.python.org/3/library/asyncio-task.html)

## Development

1. Create a [venv](https://docs.python.org/3/library/venv.html) and install dependencies with [pip](https://pip.pypa.io/en/stable/).

```sh
make install
```

2. Create a new branch with a descriptive name.

```sh
git checkout -b awesome-branch-name
```

3. Implement and add your code changes on this new branch.

## Code Style

4. Perform static code analysis with [ruff](https://beta.ruff.rs/docs/) and [mypy](https://mypy-lang.org/).

```sh
make lint
```

5. Validate code security issues with [bandit](https://bandit.readthedocs.io/en/latest/).

```sh
make security
```

6. Format the code according to defined standards with [black](https://black.readthedocs.io/en/stable/) and organize imports with [isort](https://pycqa.github.io/isort/).

```sh
make format
```

## Contribute

7. Commit your changes to your local branch using [Conventional Commit](https://www.conventionalcommits.org/en/) messages.

```sh
git add .
git commit -m 'feat(scope): example message'
```

8. Push your changes to the remote [GitHub](https://github.com/) repository.

```sh
git push origin awesome-branch-name
```

9. Create a Pull Request to the `main` branch.

## Cleaning up

10. Remove temporary files.

```sh
make clean
```

11. Uninstall all dependencies.

```sh
make uninstall
```

# References

- [disnake](https://docs.disnake.dev/en/stable/): asynchronous Discord API wrapper for Python
- [disnake-ext-plugins](https://github.com/DisnakeCommunity/disnake-ext-plugins): plugin extension for disnake providing a alternative to cogs
- [AIOHTTP](https://docs.aiohttp.org/en/stable/): asynchronous HTTP Client/Server for Python
- [Pillow (PIL Fork)](https://pillow.readthedocs.io/en/stable/): Python Imaging Library
- [spotDL](https://spotdl.io/docs/): Spotify music downloader
