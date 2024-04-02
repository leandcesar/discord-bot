<div align="center">
  <h1 align="center">discord-bot</h1>
  <p align="center">
    <a href="https://docs.python.org/3/"><img src="https://img.shields.io/badge/python 3-3776AB.svg?style=&logo=python&logoColor=white" alt="Python" href=""/></a>
    <a href="https://pre-commit.com/"><img src="https://img.shields.io/badge/pre--commit-FAB040.svg?style=&logo=pre-commit&logoColor=black" alt="precommit" /></a>
  </p>
</div>

---

# Getting Started

## Prerequisites

- [Python 3.10 or higher](https://www.python.org/downloads/)
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
3. Create a [venv](https://docs.python.org/3/library/venv.html) and install the dependencies with [poetry](https://python-poetry.org/).
```sh
make install
```
4. Check if everything was installed correctly.
```sh
make version
```

## Running

4. Fill environment variables in `.env` file.
5. Run.
```sh
make run
```

# Contributing

1. Initialize [Gitflow](https://www.atlassian.com/br/git/tutorials/comparing-workflows/gitflow-workflow).
```sh
git flow init
```
2. Create a new branch with a descriptive name (`git flow feature|bugfix|hotfix start awesome_branch_name`).
```sh
git flow feature start awesome_branch_name
```
3. Implement the code changes on the new branch.
4. Analyze the code statically with [ruff](https://beta.ruff.rs/docs/) and organize imports with [mypy](https://mypy-lang.org/).
```sh
make lint
```
5. Format the code to defined standards with [black](https://black.readthedocs.io/en/stable/) and organize imports with [isort](https://pycqa.github.io/isort/).
```sh
make format
```
6. Validate code security issues with [bandit](https://bandit.readthedocs.io/en/latest/).
```sh
make security
```
7. Commit your changes to your local branch using [Conventional Commit](https://www.conventionalcommits.org/en/) messages.
```sh
git commit -m 'feat(scope): example message'
```
8. Push your changes to the remote [GitHub](https://github.com/) repository.
```sh
git push origin feature/awesome_branch_name
```
9. Create a Pull Request to the `develop` branch.

# Cleaning up

1. Remove temp files.
```sh
make clean
```
2. Uninstall all.
```sh
make uninstall
```

# References

- [disnake](https://docs.disnake.dev/en/stable/index.html)
- [aiohttp](https://docs.aiohttp.org/en/stable/)
- [pillow](https://pillow.readthedocs.io/en/stable/#)
- [imagga](https://docs.imagga.com/)
